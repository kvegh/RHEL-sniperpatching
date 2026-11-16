"""Create only the verified NEW post-install, pre-sync cold VM checkpoint.

Reason: the selected collections expose no snapshot-create operation; native
virsh supplies it without another dependency. See
docs/implementation.md#pre-sync-satellite-checkpoint.
"""
import contextlib
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET

NAME = 'post-satellite-install'
OWNER = 'RHEL-sniperpatching NEW pre-sync checkpoint'
COMMAND_TIMEOUT = 60
POWER_TIMEOUT = 300
MAX_BYTES = 2 * 1024 * 1024


class Refused(RuntimeError):
    """A safe public explanation, without native arguments or output."""

    def __init__(self, message, unknown=False):
        super().__init__(message)
        self.unknown = unknown
        self.restarted = False
        self.restart_failed = False


def require(condition, message):
    if not condition:
        raise Refused(message)


def normalized(value):
    fields = {'op', 'vm_name', 'uuid', 'mac', 'network', 'ca_sha256',
              'installed_verified', 'pre_sync_verified', 'check'}
    require(isinstance(value, dict) and set(value) == fields, 'Use the exact checkpoint input fields.')
    require(value['op'] in ('inspect', 'create', 'verify'), 'Choose inspect, create or verify.')
    for field in ('vm_name', 'network'):
        require(isinstance(value[field], str)
                and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,62}', value[field]),
                'Require bounded native names.')
    try:
        valid_uuid = isinstance(value['uuid'], str) and str(uuid.UUID(value['uuid'])) == value['uuid']
    except ValueError:
        valid_uuid = False
    require(valid_uuid, 'Require a canonical VM UUID.')
    require(isinstance(value['mac'], str)
            and re.fullmatch(r'[0-9a-f]{2}(?::[0-9a-f]{2}){5}', value['mac']),
            'Require a canonical NIC identity.')
    require(isinstance(value['ca_sha256'], str) and re.fullmatch(r'[0-9a-f]{64}', value['ca_sha256']),
            'Require the verified Satellite CA fingerprint.')
    require(all(type(value[field]) is bool
                for field in ('installed_verified', 'pre_sync_verified', 'check')),
            'Verification and check inputs must be Booleans.')
    if value['op'] == 'create':
        require(value['installed_verified'] and value['pre_sync_verified'],
                'Refuse capture or power changes without verified installation and pre-sync state.')
    return value


def xml_root(text):
    require(isinstance(text, str) and len(text.encode()) <= MAX_BYTES, 'Native XML exceeds the bounded interface.')
    try:
        return ET.fromstring(text)
    except ET.ParseError:
        raise Refused('Native XML could not be validated.') from None


def domain_identity(text, target):
    root = xml_root(text)
    require(root.tag == 'domain' and root.get('type') == 'kvm'
            and root.findtext('name') == target['vm_name']
            and root.findtext('uuid') == target['uuid'], 'Native VM identity differs from the selected guest.')
    require(root.find('./os/loader') is None and root.find('./os/nvram') is None
            and (root.find('os') is None or root.find('os').get('firmware') in (None, 'bios')),
            'Firmware or NVRAM-backed guests are outside this checkpoint scope.')
    require(not any(root.findall('./devices/' + tag) for tag in ('hostdev', 'filesystem', 'tpm'))
            and not root.findall('.//{http://libvirt.org/schemas/domain/qemu/1.0}commandline'),
            'Refuse unqualified external guest state.')
    disks = root.findall("./devices/disk[@device='disk']")
    require(len(disks) == 1
            and all(d.get('device') == 'disk' or
                    (d.get('device') == 'cdrom' and d.find('readonly') is not None)
                    for d in root.findall('./devices/disk')),
            'Require one system disk and no additional writable storage.')
    disk = disks[0]
    source, driver, device = disk.find('source'), disk.find('driver'), disk.find('target')
    path = source.get('file', '') if source is not None else ''
    require(disk.get('type') == 'file' and driver is not None and driver.get('type') == 'qcow2'
            and source is not None and set(source.attrib) <= {'file', 'index'}
            and Path(path).is_absolute() and os.path.normpath(path) == path
            and device is not None and re.fullmatch(r'[a-z][a-z0-9]*', device.get('dev', ''))
            and disk.find('readonly') is None and disk.find('shareable') is None,
            'Require one exact local writable qcow2 system disk.')
    require(not disk.findall('backingStore/source'), 'Backing chains are outside this checkpoint scope.')
    interfaces = root.findall('./devices/interface')
    require(len(interfaces) == 1 and interfaces[0].get('type') == 'network'
            and interfaces[0].find('mac') is not None and interfaces[0].find('source') is not None
            and interfaces[0].find('mac').get('address') == target['mac']
            and interfaces[0].find('source').get('network') == target['network'],
            'Native NIC identity differs from the selected guest.')
    return {'vm_name': target['vm_name'], 'uuid': target['uuid'], 'mac': target['mac'],
            'network': target['network'], 'disk': path, 'target': device.get('dev')}


def provenance(identity, target):
    return {'schema_version': 1, 'owner': OWNER, 'snapshot_name': NAME,
            'identity': identity, 'ca_sha256': target['ca_sha256'],
            'installed_verified': True, 'pre_sync_verified': True}


def verify_snapshot(text, identity, target):
    root = xml_root(text)
    require(root.tag == 'domainsnapshot' and root.findtext('name') == NAME
            and root.findtext('state') == 'shutoff',
            'Require the exact owned cold checkpoint.')
    try:
        description = json.loads(root.findtext('description', ''))
    except (TypeError, ValueError):
        raise Refused('Checkpoint provenance is missing or malformed.') from None
    require(isinstance(description, dict) and type(description.get('schema_version')) is int
            and all(type(description.get(field)) is bool
                    for field in ('installed_verified', 'pre_sync_verified'))
            and description == provenance(identity, target),
            'Checkpoint provenance or CA binding differs; never overwrite it.')
    stored = root.find('domain')
    require(stored is not None and domain_identity(ET.tostring(stored, encoding='unicode'), target) == identity,
            'Stored checkpoint VM or disk identity differs.')
    memory = root.find('memory')
    disks = root.findall('./disks/disk')
    require(memory is not None and memory.attrib == {'snapshot': 'no'}
            and len({d.get('name') for d in disks}) == len(disks)
            and [(d.get('name'), d.get('snapshot')) for d in disks if d.get('snapshot') != 'no']
            == [(identity['target'], 'internal')],
            'Require an internal system-disk snapshot with no saved memory.')


def native_command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=COMMAND_TIMEOUT,
                                env=dict(os.environ, LC_ALL='C'))
    except subprocess.TimeoutExpired:
        raise Refused('Native command timed out; inspect actual state before continuing.', unknown=True) from None
    require(result.returncode == 0, 'Native command failed; inspect protected native state.')
    require(len(result.stdout.encode()) <= MAX_BYTES, 'Native response exceeds the bounded interface.')
    return result.stdout


@contextlib.contextmanager
def vm_lock(target):
    require(os.geteuid() == 0, 'Require the selected hypervisor management context.')
    path = '/run/lock/rhel-new-satellite-snapshot-' + target['uuid'] + '.lock'
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode) and info.st_uid == 0 and info.st_nlink == 1,
                'Require an owner-protected per-VM lock.')
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Refused('Another checkpoint operation owns this VM.') from None
        yield
    finally:
        os.close(descriptor)


class Manager:
    """One native operation; guest/API verification stays with the playbook."""

    def __init__(self, run=native_command, sleep=time.sleep, monotonic=time.monotonic):
        self.run, self.sleep, self.monotonic = run, sleep, monotonic

    def virsh(self, *args):
        return self.run(['virsh', '-c', 'qemu:///system', *args])

    def identity(self, target, inactive=False):
        flags = ['--inactive'] if inactive else []
        return domain_identity(self.virsh('dumpxml', target['vm_name'], *flags), target)

    def state(self, target):
        return self.virsh('domstate', target['vm_name']).strip()

    def wait_state(self, target, expected):
        deadline = self.monotonic() + POWER_TIMEOUT
        while self.state(target) != expected:
            require(self.monotonic() < deadline, 'Guest state deadline expired; never force a power transition.')
            self.sleep(2)

    def preflight(self, identity, target):
        path = Path(identity['disk'])
        info = path.lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and not path.is_symlink()
                and str(path.resolve()) == str(path), 'Require regular, unshared native storage without symlinks.')
        names = self.virsh('list', '--all', '--name').split()
        require(len(names) <= 64 and len(names) == len(set(names)), 'Require a bounded native VM inventory.')
        for name in names:
            if name == target['vm_name']:
                continue
            other = xml_root(self.virsh('dumpxml', name, '--inactive'))
            require(not any(Path(d.get('file')).resolve() == path
                            for d in other.findall('./devices/disk/source') if d.get('file')),
                    'Another VM refers to the selected disk.')
        capacity = re.search(r'^Capacity:\s+([0-9]+)\s*$', self.virsh('domblkinfo', target['vm_name'], str(path)), re.M)
        require(capacity is not None, 'Require current native disk capacity.')
        space = os.statvfs(path.parent)
        require(space.f_bavail * space.f_frsize >= max(1024 ** 3, int(capacity[1])),
                'Insufficient backing storage reserve; no shutdown was requested.')
        require('--atomic' in self.virsh('help', 'snapshot-create'), 'Require native atomic snapshot support.')

    def start(self, target, identity):
        require(self.state(target) == 'shut off' and self.identity(target, True) == identity,
                'Refuse restart of a changed or uncertain guest.')
        self.virsh('start', target['vm_name'])
        self.wait_state(target, 'running')
        require(self.identity(target) == identity, 'Post-start native VM identity differs.')

    def execute(self, target):
        target = normalized(target)
        identity = self.identity(target, True)
        require(self.identity(target) == identity, 'Live and persistent VM identities differ.')
        state = self.state(target)
        names = self.virsh('snapshot-list', target['vm_name'], '--name').split()
        require(len(names) <= 64 and len(names) == len(set(names)), 'Require bounded native checkpoint metadata.')
        exists = NAME in names
        if exists:
            verify_snapshot(self.virsh('snapshot-dumpxml', target['vm_name'], NAME), identity, target)
        result = {'name': NAME, 'operation': target['op'], 'exists': exists, 'cold_verified': exists,
                  'vm_running': state == 'running', 'changed': False, 'check_mode': target['check'],
                  'reused': False, 'recovered_start': False}
        if target['op'] == 'verify':
            require(exists, 'The required pre-sync checkpoint is absent.')
            return result
        if target['op'] == 'inspect':
            return result
        require(state == 'running' or (exists and state == 'shut off'),
                'Begin from a running verified guest or an existing verified off checkpoint.')
        if not exists:
            self.preflight(identity, target)
        if target['check']:
            result['changed'] = not exists or state == 'shut off'
            result['reused'] = exists
            return result
        if exists:
            result['reused'] = True
            if state == 'shut off':
                self.start(target, identity)
                result.update(changed=True, vm_running=True, recovered_start=True)
            return result

        shutdown_requested = False
        capture_requested = False
        try:
            shutdown_requested = True
            self.virsh('shutdown', target['vm_name'], '--mode', 'acpi')
            self.wait_state(target, 'shut off')
            require(self.identity(target, True) == identity, 'VM identity changed during shutdown.')
            image = json.loads(self.run(['qemu-img', 'info', '--output=json', identity['disk']]))
            require(image.get('format') == 'qcow2' and not image.get('backing-filename')
                    and not image.get('encrypted', False)
                    and not image.get('format-specific', {}).get('data', {}).get('data-file'),
                    'Refuse an unsupported backing chain, encryption or external data file.')
            snapshot = ET.Element('domainsnapshot')
            ET.SubElement(snapshot, 'name').text = NAME
            ET.SubElement(snapshot, 'description').text = json.dumps(provenance(identity, target), sort_keys=True)
            ET.SubElement(snapshot, 'memory', snapshot='no')
            ET.SubElement(ET.SubElement(snapshot, 'disks'), 'disk', name=identity['target'], snapshot='internal')
            with tempfile.NamedTemporaryFile(mode='w', prefix='satellite-checkpoint-', suffix='.xml') as source:
                os.chmod(source.name, 0o600)
                source.write(ET.tostring(snapshot, encoding='unicode'))
                source.flush()
                capture_requested = True
                self.virsh('snapshot-create', target['vm_name'], source.name, '--atomic')
            verify_snapshot(self.virsh('snapshot-dumpxml', target['vm_name'], NAME), identity, target)
            result.update(exists=True, cold_verified=True, changed=True)
            self.start(target, identity)
            result['vm_running'] = True
            return result
        except Exception as error:
            safe = error if isinstance(error, Refused) else Refused('Native checkpoint state could not be validated.')
            if capture_requested:
                # An acknowledgement/readback failure can hide a completed operation.
                # Never infer that nothing ran or automatically restart/retry it.
                safe.unknown = True
            elif shutdown_requested:
                try:
                    if self.state(target) == 'shut off' and self.identity(target, True) == identity:
                        self.start(target, identity)
                        safe.restarted = True
                        safe.unknown = False
                except Exception:
                    safe.restart_failed = True
            raise safe from None


def main():
    target = normalized(json.loads(sys.stdin.read(MAX_BYTES + 1)))
    locking = vm_lock(target) if target['op'] == 'create' and not target['check'] else contextlib.nullcontext()
    with locking:
        result = Manager().execute(target)
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        safe = error if isinstance(error, Refused) else Refused('Checkpoint operation could not be verified.', unknown=isinstance(error, KeyboardInterrupt))
        print(json.dumps({'result': 'failed', 'error': str(safe),
                          'outcome': 'unknown' if safe.unknown else 'failed',
                          'original_vm_restarted': safe.restarted, 'restart_failed': safe.restart_failed}))
        raise SystemExit(1) from None
