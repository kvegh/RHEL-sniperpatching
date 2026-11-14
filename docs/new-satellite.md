# New Satellite installation sequence

The new track includes installing Satellite, then building and verifying the
Core 2.20 execution environment and running the demo through the selected AAP.
OLD is the remote demo and its own AAP; NEW is our local Satellite and current
production AAP. The VM provision and read-only prerequisite check are complete. Satellite itself
is not installed yet. No installation playbook has been executed.

Follow Red Hat Satellite 6.19's connected-installation guide:

1. Use a freshly provisioned supported RHEL 9 x86_64 host and finalize its unique
   FQDN before installation. Verify static/transient hostname consistency,
   localhost, and full forward and reverse DNS. Stop before installation if they
   disagree; a hosts-file shortcut is not proof that DNS is correct.
2. Verify CPU, RAM, at least 4 GB swap, storage, enabled SELinux, synchronized
   time and required network access. Size synchronized content for available
   storage; a small demo disk does not imply that a full repository mirror fits.
3. Preserve the existing valid RHSM registration. Configure the guide's exact
   RHEL BaseOS, AppStream, Satellite and Satellite-maintenance repositories.
4. Upgrade RHEL packages before installing Satellite. Reboot when required,
   verify the running kernel and check for remaining updates. Recheck hostname,
   DNS and the other prerequisites after reboot.
5. Install the Satellite packages, then configure the server through the
   documented satellite-installer procedure. Keep credentials and environment
   values in the existing private Vault companion; do not print installer secrets.
6. Verify services and authenticated HTTPS/API access, then configure the
   deliberately scoped demo content and the new environment's own AAP templates.

References:

- [Planning and system/storage requirements](https://docs.redhat.com/en/documentation/red_hat_satellite/6.19/html/installing_satellite_server_in_a_connected_network_environment/planning-satellite-server-installation_satellite)
- [Environment preparation and DNS verification](https://docs.redhat.com/en/documentation/red_hat_satellite/6.19/html/installing_satellite_server_in_a_connected_network_environment/preparing-your-environment-for-satellite-server-installation)
- [Repositories, package upgrade, installation and configuration](https://docs.redhat.com/en/documentation/red_hat_satellite/6.19/html/installing_satellite_server_in_a_connected_network_environment/installing-satellite-server)

This is the implementation sequence, not a claim that the installation or
new-environment acceptance has passed. Keep CaC current with the actual deployed
state as each new-track stage is implemented and verified.

## Implemented NEW preparation stages

| Public playbook | Managed target | Behavior |
|---|---|---|
| `playbooks/new/configure_satellite_dns.yml` | Selected hypervisor | Verify exact VM identity and lease, refuse conflicting resources, add only its DHCP/DNS entries in live/persistent libvirt state without restarting the network. Check mode plans only. |
| `playbooks/new/prepare_satellite_host.yml` | Exact NEW guest | Verify SSH/VM identity and supported RHEL; configure documented repositories; upgrade installed RHEL packages; reboot as required; compare running/native installed kernels; verify DNS, swap, SELinux, time and no remaining updates. |

These stages have local validation, not live acceptance. Satellite application
package installation and initial configuration are the next separate stage.
A copied NEW demo playbook does not mean the fresh environment is operational.

## Deploying the AAP project configuration

Use the existing **Deploy RHEL Sniperpatching CaC** template. Its shared
`deploy-cac-project.yml` importer reads the fixed private encrypted capture and
requires the destination's registered inventory name and matching protected API
record. The current capture defines only the NEW setup project, inventory,
credential and templates. OLD definitions remain a separate encrypted historical
archive for the remote environment. No second importer or forwarding job is added.

The selected destination must already have the declared native hypervisor
Machine credential and compatible Core 2.20 EE. Importing configuration does not
launch setup, install Satellite or patch a host. Registering a destination and
its API access is distinct from successful API access through a worker's MCP.

## Runtime versions and bootstrap setup

The DNS and RHEL-preparation stages use built-in modules in the existing Core
2.20 management EE. They can prepare the server before the dedicated NEW demo
EE is built. Keep the shared SCM project free of a root collection requirement
that would override the job template's selected EE.

The OLD demo keeps its established Core 2.15.11/Satellite collection 3.14.0
runtime. NEW uses the current certified Satellite collection from Red Hat
Automation Hub, resolved and then exactly pinned in its Core 2.20 EE. Bind demo
templates explicitly to the appropriate immutable EE image. The later NEW-to-OLD
compatibility test uses that same NEW EE against the old targets.
