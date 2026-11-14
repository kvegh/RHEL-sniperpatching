# New Satellite installation sequence

The new track includes installing Satellite, then building and verifying the
Core 2.20 execution environment and running the demo through the selected AAP.
OLD is the remote demo and its own AAP; NEW is our local Satellite and current
production AAP. As of 14 November 2026, all four server setup stages have passed:
DNS, full RHEL preparation, Satellite 6.19.6 packages and certified initial
configuration. Native service health and authenticated HTTPS passed with
certificate validation. Demo content configuration and host patching acceptance
remain unfinished.

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

The server installation has passed this sequence; the complete NEW patching demo
has not. Keep CaC current with the actual deployed state as each later stage is
implemented and verified.

## Implemented NEW preparation stages

| Public playbook | Managed target | Behavior |
|---|---|---|
| `playbooks/new/configure_satellite_dns.yml` | Selected hypervisor | Verify exact VM identity and lease, refuse conflicting resources, add only its DHCP/DNS entries in live/persistent libvirt state without restarting the network. Check mode plans only. |
| `playbooks/new/prepare_satellite_host.yml` | Exact NEW guest | Verify SSH/VM identity and supported RHEL; configure documented repositories; upgrade installed RHEL packages; reboot as required; compare running/native installed kernels; verify DNS, swap, SELinux, time and no remaining updates. |
| `playbooks/new/install_satellite_packages.yml` | Exact prepared NEW guest | Recheck identity, DNS, resources, repositories, kernel and zero RHEL updates; install only the Satellite6.19 package family. |
| `playbooks/new/configure_satellite.yml` | Exact packaged NEW guest | Validate installed native answer schema, seed only the protected initial login, run the certified installer role and verify services plus authenticated TLS. |

All four stages have passed through the selected AAP.
The package stage, `playbooks/new/install_satellite_packages.yml`, rechecks the
exact guest identity, final FQDN/forward/reverse DNS, swap, SELinux, time, enabled
repositories, running kernel and absence of RHEL updates before installing the
documented `satellite` package. It requires a 6.19 package version and reports
package installation separately from initial configuration. The certified
installer role configured the application afterward and verified its services
and authenticated API. A copied NEW demo playbook does not establish content
configuration, client registration or patching acceptance.

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

The [NEW demo EE recipe](../playbooks/new/demo-execution-environment/README.md)
pins Core 2.20.10 and the exact certified Satellite 6.0.0 archive. The built image
passed its vendored API import, twelve NEW fixtures, nine module interfaces and
six stage syntaxes. It adds no packages and preserves the vendor base inventories,
runtime settings and layer prefix. Publication passed uncached manifest/config
and every-blob SHA-256/size verification. Private CaC must bind the receiving-Hub
digest explicitly; publication alone does not establish those live bindings.

## Job-local Satellite CA trust

Protected project configuration can supply an optional `sniper_satellite_ca_pem`
public certificate. Native Ansible tasks write a mode0600 file inside Ansible's
own temporary directory, with a forced handler that removes it on success or failure. Its path is passed
explicitly to certified collection 6.0.0 and the incremental-update URI.
An existing `SATELLITE_CA_PATH` remains a supported initial path. Empty input
retains normal trust and certificate validation stays enabled. The image,
system trust stores and existing credential schemas are unchanged; populated
CA data belongs in private Vault configuration.

The NEW read-only runtime template uses its dedicated demo EE and API credential,
with become disabled. It checks installed content and syntax, then authenticates
through both the collection and native URI HTTPS paths. Successful execution is
required before claiming AAP-to-Satellite runtime acceptance. Client registration,
content changes and host patching remain separate stages.

Recorded live verification on 14 November 2026: the normal corrected CaC import
and NEW read-only runtime job succeeded through AAP. Artifacts verified actual
Core2.20.10, Python3.12.15, certified Satellite6.0.0, all six stage syntaxes,
module interfaces and authenticated collection/native URI HTTPS. The job
contacted no managed clients and changed no Satellite content. This is runtime
readiness, separately from complete NEW patching-demo acceptance.

## Selected installer implementation

Use the certified `redhat.satellite_operations.installer` role for the application
installation step after the documented RHEL/DNS prerequisites. Red Hat's
[Satellite 6.19 RHEL 9 package manifest](https://docs.redhat.com/en/documentation/red_hat_satellite/6.19/html/package_manifest/sat-6-19-rhel9)
includes the operations collection, and the vendor's
[installer role documentation](https://github.com/RedHatSatellite/satellite-operations-collection/blob/master/roles/installer/README.md)
defines the Satellite scenario and supported options. Resolve and qualify the
certified release for the selected Core 2.20 runtime before pinning it. Keep
secret inputs in protected configuration and suppress secret-bearing output.
The certified operations 4.0.0 installer completed successfully on the NEW server.

The [installer EE recipe](../playbooks/new/execution-environment/README.md) pins
the verified certified operations 4.0.0 archive and official Core 2.20.10 base.
Its local image, vendor runtime/layer preservation and installer syntax checks
passed. Publication was independently verified through a fresh manifest/blob
readback. The private CaC binds its immutable digest and existing registry
credential. The subsequent initial configuration passed native service health
and authenticated HTTPS checks; full demo acceptance remains separate.

## Protected initial configuration

The initial configuration job reads the existing project credential pattern's
`SATELLITE_USERNAME`, `SATELLITE_PASSWORD` and `SATELLITE_SERVER_URL`. The NEW
initial password is generated into the whole-file private Vault capture and
stored as a secret native credential input; it is never a public playbook
variable, a command-line option or a reported artifact. OLD credentials remain
unchanged.

The job checks the installed scenario's exact answer-file path and the native
Puppet parameter definitions, preserves every other answer, refuses a different
existing administrator credential, and writes the selected fields as root0600.
The certified role runs with secret-bearing output suppressed and no credential
options. Final checks require native service health and authenticated HTTPS
using the CA selected by the installed answer file, with certificate validation
enabled. Only the documented Satellite firewalld service is added when its
existing daemon is running; unrelated policy is preserved.

After deployment, the queued application-configuration handover uses CoP
`infra.satellite_configuration`. That phase preserves OLD and the existing
public-code/private-Vault split; its implementation is distinct from this
initial installer and remains pending.
