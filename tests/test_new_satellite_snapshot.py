"""NEW-only tests for the fixed pre-sync cold checkpoint and native outcomes."""
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'new_satellite_snapshot', ROOT / 'playbooks/new/files/satellite_snapshot.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
TARGET = {'op': 'create', 'vm_name': 'satellite', 'uuid': '11111111-2222-4333-8444-555555555555',
          'mac': '52:54:00:11:22:33', 'network': 'example', 'ca_sha256': 'a' * 64,
          'installed_verified': True, 'pre_sync_verified': True, 'check': False}


class Native:
    """A small stateful native boundary; no libvirt or guest is contacted."""

    def __init__(self, disk):
        self.disk = disk
        self.domain = f"""<domain type="kvm"><name>satellite</name>
<uuid>{TARGET['uuid']}</uuid><os><type>hvm</type></os><devices>
<disk type="file" device="disk"><driver type="qcow2"/><source file="{disk}"/>
<target dev="vda"/></disk><interface type="network"><mac address="{TARGET['mac']}"/>
<source network="example"/></interface></devices></domain>"""
        self.live = None
        self.neighbor_disk = disk.parent / 'neighbor.qcow2'
        self.state = 'running'
        self.snapshots = {}
        self.calls = []
        self.image = {'format': 'qcow2'}
        self.hang_shutdown = False
        self.fail_start = False
        self.unknown_capture = False
        self.bad_readback = False
        self.change_after_shutdown = False
        self.atomic = True
        self.clock = 0

    def monotonic(self):
        self.clock += 200
        return self.clock

    def owned_snapshot(self):
        identity = m.domain_identity(self.domain, TARGET)
        root = ET.Element('domainsnapshot')
        ET.SubElement(root, 'name').text = m.NAME
        ET.SubElement(root, 'state').text = 'shutoff'
        ET.SubElement(root, 'description').text = json.dumps(m.provenance(identity, TARGET))
        ET.SubElement(root, 'memory', snapshot='no')
        ET.SubElement(ET.SubElement(root, 'disks'), 'disk', name='vda', snapshot='internal')
        root.append(ET.fromstring(self.domain))
        return ET.tostring(root, encoding='unicode')

    def power_calls(self):
        return [c for c in self.calls if c[0] == 'virsh'
                and c[3] in ('shutdown', 'start', 'destroy', 'snapshot-create')]

    def run(self, args):
        self.calls.append(args)
        if args[0] == 'qemu-img':
            return json.dumps(self.image)
        assert args[:3] == ['virsh', '-c', 'qemu:///system']
        command = args[3]
        if command == 'dumpxml':
            if args[4] == 'neighbor':
                return self.domain.replace(str(self.disk), str(self.neighbor_disk))
            return self.domain if '--inactive' in args else self.live or self.domain
        if command == 'domstate':
            return self.state + '\n'
        if command == 'snapshot-list':
            return '\n'.join(self.snapshots)
        if command == 'snapshot-dumpxml':
            return self.snapshots[args[5]]
        if command == 'list':
            return 'satellite\nneighbor\n'
        if command == 'domblkinfo':
            return 'Capacity: 1048576\nAllocation: 0\n'
        if command == 'help':
            return '--atomic' if self.atomic else '--disk-only'
        if command == 'shutdown':
            assert args[5:] == ['--mode', 'acpi']
            if not self.hang_shutdown:
                self.state = 'shut off'
            if self.change_after_shutdown:
                self.domain = self.domain.replace(TARGET['uuid'], 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee')
            return ''
        if command == 'snapshot-create':
            assert self.state == 'shut off' and args[-1] == '--atomic'
            root = ET.fromstring(Path(args[5]).read_text())
            ET.SubElement(root, 'state').text = 'shutoff'
            root.append(ET.fromstring(self.domain))
            if self.bad_readback:
                root.find('memory').set('snapshot', 'internal')
            self.snapshots[m.NAME] = ET.tostring(root, encoding='unicode')
            if self.unknown_capture:
                raise m.Refused('Native command timed out; inspect actual state before continuing.', unknown=True)
            return ''
        if command == 'start':
            if self.fail_start:
                raise m.Refused('Native command failed; inspect protected native state.')
            self.state = 'running'
            return ''
        raise AssertionError('Unexpected native operation')


@unittest.skipIf(os.environ.get('SNIPER_TRACK') == 'old', 'NEW-only checkpoint interface')
class NewSatelliteCheckpoint(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='satellite-snapshot-fixture-')
        self.addCleanup(self.directory.cleanup)
        disk = Path(self.directory.name) / 'satellite.qcow2'
        disk.write_bytes(b'synthetic fixture only')
        self.native = Native(disk)
        self.manager = m.Manager(run=self.native.run, sleep=lambda _: None, monotonic=self.native.monotonic)
        self.free = patch.object(m.os, 'statvfs', return_value=SimpleNamespace(f_bavail=8 * 1024 ** 3, f_frsize=1))
        self.free.start()
        self.addCleanup(self.free.stop)

    def execute(self, **changes):
        return self.manager.execute(dict(TARGET, **changes))

    def test_create_then_repeat_inspect_and_verify_preserve_other_snapshots(self):
        self.native.snapshots['unrelated'] = '<unrelated/>'
        result = self.execute()
        self.assertTrue(result['changed'] and result['cold_verified'] and result['vm_running'])
        self.assertEqual(set(self.native.snapshots), {'unrelated', m.NAME})
        self.assertEqual(self.native.snapshots['unrelated'], '<unrelated/>')
        before = len(self.native.power_calls())
        repeat = self.execute()
        self.assertFalse(repeat['changed'])
        self.assertTrue(repeat['reused'])
        for op in ('inspect', 'verify'):
            result = self.execute(op=op, installed_verified=False, pre_sync_verified=False)
            self.assertTrue(result['exists'] and result['cold_verified'])
        self.assertEqual(len(self.native.power_calls()), before)

    def test_inspect_and_verify_are_read_only_even_when_guest_is_off(self):
        self.native.snapshots[m.NAME] = self.native.owned_snapshot()
        self.native.state = 'shut off'
        for op in ('inspect', 'verify'):
            result = self.execute(op=op)
            self.assertTrue(result['cold_verified'])
            self.assertFalse(result['vm_running'] or result['changed'])
        self.assertFalse(self.native.power_calls())

    def test_existing_valid_off_checkpoint_can_recover_one_start(self):
        self.native.snapshots[m.NAME] = self.native.owned_snapshot()
        self.native.state = 'shut off'
        result = self.execute()
        self.assertTrue(result['changed'] and result['reused'] and result['recovered_start'])
        self.assertEqual([c[3] for c in self.native.power_calls()], ['start'])

    def test_missing_verify_fails_without_power(self):
        self.assertFalse(self.execute(op='inspect')['exists'])
        with self.assertRaises(m.Refused):
            self.execute(op='verify')
        self.assertFalse(self.native.power_calls())

    def test_false_preconditions_refuse_before_any_native_read_or_power(self):
        for field in ('installed_verified', 'pre_sync_verified'):
            with self.subTest(field=field), self.assertRaises(m.Refused):
                self.execute(**{field: False})
        self.assertFalse(self.native.calls)

    def test_untrusted_input_fields_and_types_are_rejected(self):
        for changes in ({'op': 'restore'}, {'uuid': 'not-a-uuid'}, {'vm_name': 'name;command'},
                        {'check': 'false'}, {'pre_sync_verified': 1}, {'ca_sha256': 'x' * 64},
                        {'extra': True}):
            with self.subTest(changes=changes), self.assertRaises(m.Refused):
                self.execute(**changes)
        self.assertFalse(self.native.calls)

    def test_wrong_name_uuid_mac_or_network_never_gets_powered(self):
        for before, after in (('<name>satellite</name>', '<name>another</name>'),
                              (TARGET['uuid'], 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'),
                              (TARGET['mac'], '52:54:00:aa:bb:cc'),
                              ('network="example"', 'network="different"')):
            original = self.native.domain
            self.native.domain = original.replace(before, after)
            with self.subTest(after=after), self.assertRaises(m.Refused):
                self.execute()
            self.native.domain = original
        self.assertFalse(self.native.power_calls())

    def test_unsupported_storage_firmware_and_extra_devices_are_refused(self):
        original = self.native.domain
        variants = [
            original.replace('type="qcow2"', 'type="raw"'),
            original.replace('</os>', '<nvram>/example/nvram</nvram></os>'),
            original.replace('</disk>', '<backingStore><source file="/example/base.qcow2"/></backingStore></disk>'),
            original.replace('</devices>', '<disk device="disk"/></devices>'),
            original.replace('</devices>', '<tpm/></devices>'),
            original.replace('</disk>', '<shareable/></disk>'),
            original.replace('</devices>', '<interface type="network"/></devices>')]
        for xml in variants:
            self.native.domain = xml
            with self.subTest(xml=xml), self.assertRaises(m.Refused):
                self.execute()
        self.assertFalse(self.native.power_calls())

    def test_live_and_persistent_disk_mismatch_is_refused(self):
        self.native.live = self.native.domain.replace(str(self.native.disk), '/example/changed.qcow2')
        with self.assertRaises(m.Refused):
            self.execute()
        self.assertFalse(self.native.power_calls())

    def test_shared_disk_capacity_and_missing_atomic_support_stop_before_shutdown(self):
        self.native.neighbor_disk = self.native.disk
        with self.assertRaises(m.Refused):
            self.execute()
        self.native.neighbor_disk = self.native.disk.parent / 'other.qcow2'
        self.native.atomic = False
        with self.assertRaises(m.Refused):
            self.execute()
        self.native.atomic = True
        with patch.object(m.os, 'statvfs', return_value=SimpleNamespace(f_bavail=0, f_frsize=1)):
            with self.assertRaises(m.Refused):
                self.execute()
        self.assertFalse(self.native.power_calls())

    def test_symlink_storage_is_refused_before_shutdown(self):
        original = self.native.disk.with_name('actual.qcow2')
        self.native.disk.rename(original)
        self.native.disk.symlink_to(original)
        with self.assertRaises(m.Refused):
            self.execute()
        self.assertFalse(self.native.power_calls())

    def test_foreign_or_malformed_same_name_checkpoint_is_never_replaced(self):
        original = self.native.owned_snapshot()
        for field, value in (('owner', 'another owner'), ('ca_sha256', 'b' * 64),
                             ('pre_sync_verified', False), ('pre_sync_verified', 1),
                             ('installed_verified', 1), ('schema_version', True)):
            root = ET.fromstring(original)
            description = json.loads(root.findtext('description'))
            description[field] = value
            root.find('description').text = json.dumps(description)
            self.native.snapshots[m.NAME] = ET.tostring(root, encoding='unicode')
            with self.subTest(field=field), self.assertRaises(m.Refused):
                self.execute(op='inspect')
        for tag, attribute, value in (('memory', 'snapshot', 'internal'), ('state', None, 'running'),
                                      ('domain/uuid', None, 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'),
                                      ('disks/disk', 'name', 'different')):
            root = ET.fromstring(original)
            if attribute:
                root.find(tag).set(attribute, value)
            else:
                root.find(tag).text = value
            self.native.snapshots[m.NAME] = ET.tostring(root, encoding='unicode')
            with self.subTest(tag=tag), self.assertRaises(m.Refused):
                self.execute()
        self.assertFalse(self.native.power_calls())

    def test_check_mode_never_powers_captures_or_recovers(self):
        result = self.execute(check=True)
        self.assertTrue(result['changed'])
        self.assertFalse(result['exists'] or self.native.power_calls())
        self.native.snapshots[m.NAME] = self.native.owned_snapshot()
        self.native.state = 'shut off'
        result = self.execute(check=True)
        self.assertTrue(result['changed'] and result['reused'])
        self.assertFalse(self.native.power_calls())

    def test_shutdown_deadline_does_not_force_stop_capture_or_start(self):
        self.native.hang_shutdown = True
        with self.assertRaisesRegex(m.Refused, 'deadline'):
            self.execute()
        self.assertEqual([c[3] for c in self.native.power_calls()], ['shutdown'])
        self.assertEqual(self.native.state, 'running')

    def test_unknown_capture_can_have_happened_and_is_not_restarted_or_retried(self):
        self.native.unknown_capture = True
        with self.assertRaises(m.Refused) as caught:
            self.execute()
        self.assertTrue(caught.exception.unknown)
        self.assertIn(m.NAME, self.native.snapshots)
        self.assertEqual(self.native.state, 'shut off')
        self.assertEqual([c[3] for c in self.native.power_calls()], ['shutdown', 'snapshot-create'])
        result = self.execute(op='inspect')
        self.assertTrue(result['cold_verified'])
        self.assertEqual(self.native.state, 'shut off')

    def test_failed_capture_readback_remains_unknown_and_off(self):
        self.native.bad_readback = True
        with self.assertRaises(m.Refused) as caught:
            self.execute()
        self.assertTrue(caught.exception.unknown)
        self.assertEqual(self.native.state, 'shut off')
        self.assertNotIn('start', [c[3] for c in self.native.power_calls()])

    def test_precapture_backing_failure_recovers_only_unchanged_off_guest(self):
        self.native.image['backing-filename'] = '/example/base.qcow2'
        with self.assertRaisesRegex(m.Refused, 'backing') as caught:
            self.execute()
        self.assertTrue(caught.exception.restarted)
        self.assertEqual(self.native.state, 'running')
        self.assertEqual([c[3] for c in self.native.power_calls()], ['shutdown', 'start'])
        self.assertFalse(self.native.snapshots)

    def test_recovery_failure_preserves_original_error_and_reports_restart_failure(self):
        self.native.image['backing-filename'] = '/example/base.qcow2'
        self.native.fail_start = True
        with self.assertRaisesRegex(m.Refused, 'backing') as caught:
            self.execute()
        self.assertTrue(caught.exception.restart_failed)
        self.assertFalse(caught.exception.restarted)
        self.assertEqual(self.native.state, 'shut off')

    def test_changed_guest_after_shutdown_is_never_started_or_captured(self):
        self.native.change_after_shutdown = True
        with self.assertRaises(m.Refused):
            self.execute()
        self.assertEqual([c[3] for c in self.native.power_calls()], ['shutdown'])

    def test_inspect_and_check_cli_do_not_create_a_lock_or_expose_identity(self):
        for changes in ({'op': 'inspect'}, {'check': True}):
            stream = io.StringIO()
            with patch.object(m.sys, 'stdin', io.StringIO(json.dumps(dict(TARGET, **changes)))), \
                    patch.object(m, 'Manager', return_value=self.manager), \
                    patch.object(m, 'vm_lock', side_effect=AssertionError('Read-only mode acquired a lock')), \
                    contextlib.redirect_stdout(stream):
                m.main()
            public = stream.getvalue()
            self.assertNotIn(str(self.native.disk), public)
            self.assertNotIn(TARGET['uuid'], public)
            self.assertNotIn(TARGET['mac'], public)
            self.assertNotIn(TARGET['ca_sha256'], public)
            self.assertIn('cold_verified', json.loads(public))

    def test_per_vm_lock_rejects_a_competing_operation_and_closes_descriptor(self):
        info = SimpleNamespace(st_mode=stat.S_IFREG | 0o600, st_uid=0, st_nlink=1)
        with patch.object(m.os, 'geteuid', return_value=0), patch.object(m.os, 'open', return_value=9), \
                patch.object(m.os, 'fstat', return_value=info), patch.object(m.os, 'close') as close, \
                patch.object(m.fcntl, 'flock', side_effect=BlockingIOError):
            with self.assertRaises(m.Refused):
                with m.vm_lock(TARGET):
                    self.fail('Competing operation was allowed')
        close.assert_called_once_with(9)

    def test_native_errors_and_timeouts_do_not_expose_command_arguments(self):
        args = ['virsh', '-c', 'qemu:///system', 'snapshot-create', 'synthetic-private-name']
        with patch.object(m.subprocess, 'run', return_value=SimpleNamespace(
                returncode=1, stdout='synthetic-private-data', stderr='synthetic-private-error')):
            with self.assertRaises(m.Refused) as caught:
                m.native_command(args)
        self.assertNotIn('synthetic-private', str(caught.exception))
        with patch.object(m.subprocess, 'run', side_effect=subprocess.TimeoutExpired(
                args, 60, output='synthetic-private-data')):
            with self.assertRaises(m.Refused) as caught:
                m.native_command(args)
        self.assertTrue(caught.exception.unknown)
        self.assertNotIn('synthetic-private', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
