# Provisioning & Automation

## General Structure

* `ansible.cfg` - configuration file used by Ansible
* `benchmark_scripts/` - a collection of simple shell scripts to automate
  benchmark execution with different parameters
* `client/` - templates and/or other files which will be templated and/or copied to the client VMs
* `server/` - templates and/or other files which will be templated and/or copied to the server VMs
* `group_vars/` - collection of Ansible variables for the groups defined in its inventory file
* `template/` - collection of Ansible playbooks which will be imported in other playbooks and should
  not be executed directly
* `tasks/` - collection of Ansible playbook tasks, organized by client, server and deployment style

## Playbooks

The playbook `self.yaml` is used by the managed VM during its provisioning step in Vagrant. It
generates the `inventory.ini` used by Ansible and should not be invoked directly.

### Installation Playbooks

Some playbooks only install packages, these are:

* `ntp.yaml` - installs NTP on all machines and is used for testing purposes
* `dstat.yaml` - installs `dstat` on all server machines
* `install-docker-compose.yaml` - installs `docker-compose` on the server machines

## Client-specific Playbooks

* `copy-files.client.yaml` - copies all the relevant files from `client/` to the client VMs
* `ycsb.yaml` - builds the YCSB Docker image on the client machines
* `benchmark-load.yaml` - used to load the database; supports several parameters
* `benchmark-run.yaml` - used to run the benchmark on the previously loaded database;
  supports several parameters

## Server-specific Playbooks

`server-*.yaml` playbooks are, as the name implies, used to automate work on the server VMs.
These are then divided into `server-single-*.yaml` and `server-cluster-*.yaml` playbooks, for a
single-server and cluster deployments, respectively.
They are used for setting services/containers up and destroying them afterwards,
querying the database properties and more.

Other interesting playbooks:

* `node-update-labels.yaml` - used strictly in cluster deployment and it sets or updates
the labels of Swarm nodes to constrain service deployment
* `server-query-properties.yaml` - can be used in both cluster or single deployment, checks
  deployment type and queries the database properties based on that

## Docker Swarm Playbooks

These are `swarm-*` playbooks and may contain `client` or `server`
in the name to define which machines they will target: client or server, respectively.
`swarm-lave.yaml` and `swarm-setup.yaml` combine the others into a single playbook.
