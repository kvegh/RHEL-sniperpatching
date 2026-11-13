# New Satellite installation sequence

The new track includes installing Satellite, then building and verifying the
Core 2.20 execution environment and running the demo through the selected AAP.
The VM provision and read-only prerequisite check are complete. Satellite itself
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
