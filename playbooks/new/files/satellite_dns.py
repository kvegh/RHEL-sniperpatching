"""Add only this verified NEW VM's DHCP reservation and native libvirt DNS host.

Reason: libvirt net-update supports live, additive changes without restarting
the shared network. Parse and validate both scopes before issuing any update.
See docs/new-satellite.md and https://libvirt.org/formatnetwork.html.
"""
import ipaddress
import json
import re
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET


class Refused(ValueError):
    pass


def require(condition):
    if not condition:
        raise Refused('NEW VM DNS identity, ownership or address check failed')


def normalized(target):
    require(set(target) == {'vm_name', 'uuid', 'mac', 'address', 'fqdn', 'network', 'check'})
    for key in ('vm_name', 'network'):
        require(isinstance(target[key], str) and re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,62}', target[key]))
    require(isinstance(target['check'], bool))
    require(str(uuid.UUID(target['uuid'])) == target['uuid'].lower())
    require(re.fullmatch(r'[0-9a-f]{2}(?::[0-9a-f]{2}){5}', target['mac']) is not None)
    require(str(ipaddress.IPv4Address(target['address'])) == target['address'])
    fqdn = target['fqdn']
    require(isinstance(fqdn, str) and len(fqdn) <= 253 and '.' in fqdn and not fqdn.endswith('.'))
    require(all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in fqdn.split('.')))
    require(fqdn.split('.')[0] == target['vm_name'])
    return target


def domain_matches(xml, target):
    root = ET.fromstring(xml)
    require(root.findtext('name') == target['vm_name'])
    require(root.findtext('uuid', '').lower() == target['uuid'])
    interfaces = root.findall('./devices/interface')
    matches = [item for item in interfaces if item.get('type') == 'network'
               and item.find('mac') is not None and item.find('source') is not None
               and item.find('mac').get('address', '').lower() == target['mac']
               and item.find('source').get('network') == target['network']]
    require(len(matches) == 1)


def plan(xml, target):
    root = ET.fromstring(xml)
    require(root.findtext('name') == target['network'])
    require(root.find('dns') is None or root.find('dns').get('enable', 'yes') != 'no')
    ip_nodes = root.findall('ip')
    parents = []
    for index, node in enumerate(ip_nodes):
        if node.get('family', 'ipv4') != 'ipv4' or node.find('dhcp') is None:
            continue
        prefix = node.get('prefix') or node.get('netmask')
        subnet = ipaddress.ip_network(node.get('address') + '/' + prefix, strict=False)
        if ipaddress.IPv4Address(target['address']) in subnet:
            require(target['address'] != node.get('address'))
            require(ipaddress.IPv4Address(target['address']) not in (subnet.network_address, subnet.broadcast_address))
            parents.append((index, node))
    require(len(parents) == 1)
    index, parent = parents[0]
    desired_host = {'mac': target['mac'], 'name': target['vm_name'], 'ip': target['address']}
    matches = []
    for node in root.findall('./ip/dhcp/host'):
        if (node.get('mac', '').lower() == target['mac'] or node.get('ip') == target['address']
                or node.get('name') in (target['vm_name'], target['fqdn'])):
            require(node.attrib == desired_host and len(node) == 0)
            matches.append(node)
    require(len(matches) <= 1)
    dns_matches = []
    for node in root.findall('./dns/host'):
        names = [item.text for item in node.findall('hostname')]
        if node.get('ip') == target['address'] or target['fqdn'] in names:
            require(node.attrib == {'ip': target['address']} and names == [target['fqdn']])
            dns_matches.append(node)
    require(len(dns_matches) <= 1)
    actions = []
    if not matches:
        host = ET.Element('host', desired_host)
        actions.append(('ip-dhcp-host', ET.tostring(host, encoding='unicode'), index))
    if not dns_matches:
        host = ET.Element('host', {'ip': target['address']})
        ET.SubElement(host, 'hostname').text = target['fqdn']
        actions.append(('dns-host', ET.tostring(host, encoding='unicode'), None))
    return actions


def run(*arguments):
    result = subprocess.run(['virsh', '-c', 'qemu:///system', *arguments],
                            capture_output=True, text=True, timeout=30)
    require(result.returncode == 0)
    return result.stdout


def main():
    target = normalized(json.load(sys.stdin))
    domain_matches(run('dumpxml', target['vm_name']), target)
    lease = run('net-dhcp-leases', target['network'])
    rows = [line.split() for line in lease.splitlines() if 'ipv4' in line.split()]
    current = [row for row in rows if str(ipaddress.ip_interface(row[row.index('ipv4') + 1]).ip) == target['address']]
    require(len(current) == 1 and target['mac'] in [part.lower() for part in current[0]])
    plans = {scope: plan(run('net-dumpxml', target['network'], *flags), target)
             for scope, flags in (('config', ['--inactive']), ('live', []))}
    count = sum(len(actions) for actions in plans.values())
    if not target['check']:
        for scope, actions in plans.items():
            for section, xml, parent_index in actions:
                arguments = ['net-update', target['network'], 'add-last', section, xml, '--' + scope]
                if parent_index is not None:
                    arguments.extend(['--parent-index', str(parent_index)])
                run(*arguments)
        for scope, flags in (('config', ['--inactive']), ('live', [])):
            require(not plan(run('net-dumpxml', target['network'], *flags), target))
    print(json.dumps({'changed': count > 0, 'updates': count,
                      'check_mode': target['check'], 'network_restarted': False}))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        raise SystemExit('Targeted NEW VM DNS operation failed; inspect protected inputs and native status before retrying.') from None
