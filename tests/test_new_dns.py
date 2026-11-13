"""Exercise NEW-only libvirt ownership, conflict and idempotency boundaries."""
import copy
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('new_dns', ROOT / 'playbooks/new/files/satellite_dns.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
TARGET = {'vm_name': 'satellite', 'uuid': '11111111-2222-4333-8444-555555555555',
          'mac': '52:54:00:11:22:33', 'address': '192.0.2.20',
          'fqdn': 'satellite.example.test', 'network': 'example', 'check': True}
NETWORK = """<network><name>example</name><domain name='different.test'/>
<ip address='192.0.2.1' prefix='24'><dhcp><range start='192.0.2.10' end='192.0.2.50'/>
<host mac='52:54:00:99:88:77' name='colleague' ip='192.0.2.30'/>
</dhcp></ip></network>"""
DOMAIN = """<domain><name>satellite</name><uuid>11111111-2222-4333-8444-555555555555</uuid>
<devices><interface type='network'><mac address='52:54:00:11:22:33'/>
<source network='example'/></interface></devices></domain>"""


class NewDnsBoundaries(unittest.TestCase):
    def execute(self, check, conflict=False):
        state = {'config': NETWORK, 'live': NETWORK}
        if conflict:
            state['live'] = NETWORK.replace("name='colleague'", "name='satellite'")
        calls = []
        def run(*args):
            calls.append(args)
            if args[0] == 'dumpxml':
                return DOMAIN
            if args[0] == 'net-dhcp-leases':
                return '2030-01-01 00:00:00 52:54:00:11:22:33 ipv4 192.0.2.20/24 satellite -\n'
            if args[0] == 'net-dumpxml':
                return state['config' if '--inactive' in args else 'live']
            self.assertEqual(args[0], 'net-update')
            scope = 'config' if '--config' in args else 'live'
            root = ET.fromstring(state[scope])
            if args[3] == 'ip-dhcp-host':
                parent = root.find('./ip/dhcp')
            else:
                parent = root.find('dns')
                if parent is None:
                    parent = ET.SubElement(root, 'dns')
            parent.append(ET.fromstring(args[4]))
            state[scope] = ET.tostring(root, encoding='unicode')
            return ''
        out = io.StringIO()
        with patch.object(m, 'run', run), patch.object(m.sys, 'stdin', io.StringIO(json.dumps(dict(TARGET, check=check)))):
            with contextlib.redirect_stdout(out):
                if conflict:
                    with self.assertRaises(m.Refused):
                        m.main()
                else:
                    m.main()
        return calls, out.getvalue(), state

    def test_check_mode_reads_both_scopes_and_never_changes_the_network(self):
        calls, out, state = self.execute(check=True)
        self.assertEqual(state, {'config': NETWORK, 'live': NETWORK})
        self.assertFalse(any(args[0] == 'net-update' for args in calls))
        self.assertEqual(json.loads(out)['updates'], 4)
        self.assertTrue(json.loads(out)['check_mode'])

    def test_a_live_scope_conflict_is_found_before_any_config_write(self):
        calls, out, _ = self.execute(check=False, conflict=True)
        self.assertFalse(any(args[0] == 'net-update' for args in calls))
        self.assertEqual(out, '')

    def test_normal_run_only_adds_and_rechecks_the_four_exact_entries(self):
        calls, out, state = self.execute(check=False)
        writes = [args for args in calls if args[0] == 'net-update']
        self.assertEqual(len(writes), 4)
        self.assertTrue(all(args[2] == 'add-last' for args in writes))
        self.assertFalse(json.loads(out)['network_restarted'])
        for xml in state.values():
            self.assertEqual(m.plan(xml, TARGET), [])
            root = ET.fromstring(xml)
            self.assertEqual(root.find('domain').get('name'), 'different.test')
            colleague = next(x for x in root.findall('./ip/dhcp/host') if x.get('name') == 'colleague')
            self.assertEqual(colleague.get('ip'), '192.0.2.30')

    def test_exact_native_domain_identity_is_required(self):
        m.domain_matches(DOMAIN, TARGET)
        for field, value in [('uuid', 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'),
                             ('vm_name', 'another'), ('network', 'other'),
                             ('mac', '52:54:00:aa:bb:cc')]:
            target = dict(TARGET, **{field: value})
            with self.assertRaises(m.Refused):
                m.domain_matches(DOMAIN, target)

    def test_only_two_additive_entries_are_planned(self):
        before = ET.tostring(ET.fromstring(NETWORK))
        actions = m.plan(NETWORK, TARGET)
        self.assertEqual([item[0] for item in actions], ['ip-dhcp-host', 'dns-host'])
        self.assertEqual(ET.tostring(ET.fromstring(NETWORK)), before)
        self.assertEqual(ET.fromstring(actions[0][1]).attrib,
                         {'mac': TARGET['mac'], 'name': 'satellite', 'ip': TARGET['address']})
        self.assertEqual(ET.fromstring(actions[1][1]).findtext('hostname'), TARGET['fqdn'])

    def test_existing_exact_entries_are_idempotent(self):
        root = ET.fromstring(NETWORK)
        dns = ET.SubElement(root, 'dns')
        for section, xml, _ in m.plan(NETWORK, TARGET):
            (root.find('./ip/dhcp') if section == 'ip-dhcp-host' else dns).append(ET.fromstring(xml))
        self.assertEqual(m.plan(ET.tostring(root), TARGET), [])

    def test_partial_completion_plans_only_the_missing_entry(self):
        root = ET.fromstring(NETWORK)
        root.find('./ip/dhcp').append(ET.fromstring(m.plan(NETWORK, TARGET)[0][1]))
        self.assertEqual([item[0] for item in m.plan(ET.tostring(root), TARGET)], ['dns-host'])

    def test_other_host_ip_mac_or_name_is_never_overwritten(self):
        for attrs in ({'ip': TARGET['address']}, {'mac': TARGET['mac']}, {'name': 'satellite'}):
            root = ET.fromstring(NETWORK)
            root.find('./ip/dhcp/host').attrib.update(attrs)
            with self.assertRaises(m.Refused):
                m.plan(ET.tostring(root), TARGET)

    def test_conflicting_dns_and_disabled_dns_are_refused(self):
        for attrs, host in [({'enable': 'no'}, ''), ({}, "<host ip='192.0.2.99'><hostname>satellite.example.test</hostname></host>"),
                            ({}, "<host ip='192.0.2.20'><hostname>someone.example.test</hostname></host>")]:
            root = ET.fromstring(NETWORK)
            dns = ET.SubElement(root, 'dns', attrs)
            if host:
                dns.append(ET.fromstring(host))
            with self.assertRaises(m.Refused):
                m.plan(ET.tostring(root), TARGET)

    def test_bridge_broadcast_foreign_subnet_and_wrong_network_refused(self):
        for address in ('192.0.2.1', '192.0.2.255', '198.51.100.20'):
            with self.assertRaises(m.Refused):
                m.plan(NETWORK, dict(TARGET, address=address))
        with self.assertRaises(m.Refused):
            m.plan(NETWORK, dict(TARGET, network='different'))

    def test_untrusted_names_and_extra_input_fields_are_refused(self):
        self.assertEqual(m.normalized(copy.deepcopy(TARGET)), TARGET)
        for target in (dict(TARGET, vm_name='satellite;id'), dict(TARGET, fqdn='satellite..test'),
                       dict(TARGET, fqdn='other.example.test'), dict(TARGET, check='false'),
                       dict(TARGET, address='192.0.2.20;id'), dict(TARGET, extra=True)):
            with self.assertRaises((m.Refused, ValueError)):
                m.normalized(target)


if __name__ == '__main__':
    unittest.main()
