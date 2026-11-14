# NEW track

This directory contains seven demo playbooks and separate NEW setup stages. Select its full
`playbooks/new/<stage>.yml` path in AAP, with this track's protected environment
inputs, inventory and execution environment. Generic survey definitions remain
at the repository's `surveys/` directory.

See the [project guide](../../README.md) and [operations](../../docs/operations.md).

The NEW tree starts from the reviewed OLD demo logic. A copied playbook is not
proof of new Satellite/API/EE compatibility. The new Satellite installation,
new environment CaC and end-to-end demo acceptance are separate pending stages.
Follow the [installation sequence](../../docs/new-satellite.md).

NEW always means our local Satellite and up-to-date production AAP. Run
`configure_satellite_dns.yml` first and `prepare_satellite_host.yml` second;
these do not install the Satellite application. The shared CaC importer creates
their definitions but does not launch them. It requires an explicitly registered
destination with protected API access and the declared hypervisor/EE dependencies.

The NEW demo dependency manifests pin certified `redhat.satellite` **6.0.0**.
Its filter module manages filters only; explicit rules remain in
`content_view_filter_rule`, so the original-only RPM inclusion filter does not
create a package-name rule. OLD retains its independent **3.14.0** pin and source.
The [installer EE](execution-environment/README.md) independently pins certified
`redhat.satellite_operations` **4.0.0**. Offline interface and fixture checks are
separate from NEW EE publication and live demo acceptance.
