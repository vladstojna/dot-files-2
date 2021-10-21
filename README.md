# Large Scale Systems Engineering - Project

## Repository Structure

Relevant items

* `config.yaml.example` - example configuration file loaded
  inside `Vagrantfile` that defines several VM options
  when deploying the environment
* `provisioning/` - synced folder which contains
  mostly Ansible playbooks and other miscellaneous files
* `results/` - synced folder where results are gathered
* `scripts/` - contains several helper scripts which
  are used to provision the VMs or execute on the host to post-process
  the results and more

There is a `README.md` in `provisioning` describing its contents.

## Instructions

Before running anything, we have to set the environment up.

Requirements:

* Vagrant version 2 or later
* VirtualBox version 6 or later
* OpenSSH

### Key Generation

Initially, we need to generate an SSH key

```shell
ssh-keygen -t rsa -b 4096 -f /path/to/private/key -q -N ''
```

Change `/path/to/private/key` to a path of your preference and remember it.
We will need it later.

### Configuration File

Create a copy of the file `config.yaml.example` and rename it to `config.yaml`.

```shell
cp config.yaml.example config.yaml
```

Open `config.yaml` and edit its contents to suit your needs.

For this example, we will use an Ansible manager/controller VM

```yaml
manager:
  hostname: manager
  cpus: 1
  memory: 1024
```

Four server VMs, each with 2 GiB of memory and 1 CPU

```yaml
replica:
  hostname: replica
  cpus: 1
  memory: 2048
  count: 4
```

One client VM with 2 GiB of memory and 2 CPUs

```yaml
client:
  hostname: client
  cpus: 2
  memory: 2048
  count: 1
```

Finally, set the path to the private key generated [here](#key-generation)

```yaml
key: /path/to/private/key
```

### Running Vagrant

To create and provision the VMs run. This step will also
generate an Ansible inventory file in `provisioning/inventory.ini`.

```shell
$ vagrant up
Bringing machine 'replica1' up with 'virtualbox' provider...
Bringing machine 'replica2' up with 'virtualbox' provider...
Bringing machine 'replica3' up with 'virtualbox' provider...
Bringing machine 'replica4' up with 'virtualbox' provider...
Bringing machine 'client1' up with 'virtualbox' provider...
Bringing machine 'manager' up with 'virtualbox' provider...
...
```

After Vagrant is done, SSH into the manager VM with:

```shell
vagrant ssh
```

and change directory inside the VM session:

```shell
cd provisioning
```

To test that everything is working and all machines are reachable run:

```shell
$ ansible managed -m ping
replica3 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
...
```

From this point onward, every command will be executed inside the manager
VM, in `~/provisioning`

### Docker Swarm Setup

To create a swarm and have all other machines join it, run:

```shell
$ ansible-playbook swarm-setup.yaml
...
```

This will create one swarm for the server machines and
another for the client machines.

### Build YCSB docker image in the client VMs

To prepare the client benchmark for execution we have to copy some files
and build the docker image.

```shell
$ ansible-playbook copy-files.client.yaml
...

$ ansible-playbook ycsb.yaml -e 'extra="--build-arg YCSB_BINDING=arangodb"'
...
```

After the playbook has finished, confirm the image exists with:

```shell
$ ansible clients -a 'docker images'
client1 | CHANGED | rc=0 >>
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
ycsb         latest    46c148188a6e   19 seconds ago   298MB
ubuntu       focal     ba6acccedd29   5 days ago       72.8MB
```

### Running the Server

It is possible to run the database server as:

* a single server
* a cluster of databases with sharded data

#### **Single**

Deploy a single server:

```shell
$ ansible-playbook server-single-deploy.yaml
...
```

This will create a container running ArangoDB inside the VM `replica1`.
To destroy the deployed server after running the benchmark, execute:

```shell
$ ansible-playbook server-single-destroy.yaml -e remove_volumes=yes
...
```

#### **Cluster**

ArangoDB has an [extensive documentation](https://www.arangodb.com/docs/stable/architecture-deployment-modes-cluster.html) regarding its cluster deployment.
The [cluster architecture](https://www.arangodb.com/docs/stable/architecture-deployment-modes-cluster-architecture.html) consists
of instances with three distinct roles:

* Agents
* Coordinators
* DB-Servers

We will be deploying a [sharded cluster](https://www.arangodb.com/docs/stable/architecture-deployment-modes-cluster-sharding.html) in this example.
Seeing as have 4 VMs deployed, we will be running one Coordinator on `replica1`,
one Agent on `replica2` and two DB-Servers on `replica3` and `replica4`.

First, let's label the swarm nodes for Docker to know on which to deploy each service:

```shell
$ ansible-playbook node-update-labels.yaml
...
```

Next, let's generate the docker compose file:

```shell
$ ansible-playbook server-cluster-generate.yaml -e constrained_placement=yes
...
```

Confirm that a file named `docker-compose.yaml` exists on `replica1`

```shell
$ ansible replica1 -a 'ls -l'
replica1 | CHANGED | rc=0 >>
total 4
-rw-rw-r-- 1 vagrant vagrant 3863 Oct 21 22:17 docker-compose.yaml
```

Now, deploy the stack. There is no need to clean up previous deployments
because this is the first time we are deploying.

```shell
$ ansible-playbook server-cluster-deploy.yaml -e cleanup=no
...
ok: [replica1] => {
    "msg": [
        "Creating network database_arango_net",
        "Creating service database_arango_db1",
        "Creating service database_arango_db2",
        "Creating service database_arango_coordinator",
        "Creating service database_arango_agency"
    ]
}
...
```

After the stack is deployed, wait around 30 seconds to allow the servers to
stabilize. You can also check the service logs with:

```shell
ansible replica1 -a 'docker service logs <service name>' | less
```

Finally, create a sharded collection.
We will control the synchronization to disk when running the benchmark and
that is why we pass `wait_sync=no`:

```shell
$ ansible-playbook server-cluster-shardcollection.yaml -e wait_sync=no
...
TASK [Shards created]
ok: [replica1] => {
    "msg": [
        "s10163",
        "s10164"
    ]
}
...
```

To query the properties of a collection, run:

TODO

### Running the benchmark

Before running the benchmark, we have to create and load the database.

```shell
ansible-playbook benchmark-load.yaml -e record_count=N
```

Load `20000` records into the database:

```shell
$ ansible-playbook benchmark-load.yaml -e record_count=20000
...
```

It is possible to run the benchmark with several parameters to tweak the
workload type, the number of operations, the number of threads and more.
For example:

```shell
ansible-playbook benchmark-run.yaml \
  -e replicas=N \
  -e workload=WORKLOAD \
  -e operation_count=N \
  -e threads=VALUE \
  -e target=VALUE \
  -e gather_dest=VALUE \
  -e transaction_update=VALUE \
  -e wait_sync=VALUE
```

Where:

* `replicas` is the number of [docker service replicas](https://docs.docker.com/engine/reference/commandline/service_create/#create-a-service-with-5-replica-tasks---replicas)
* `workload` is the [workload type](https://github.com/brianfrankcooper/YCSB/wiki/Core-Workloads)
* `operation_count` is the number of operations to perform
* `threads` is the number of client threads to spawn
* `target` throttles the client; it is the target throughput
  or `0` if the client is unthrottled
* `transaction_update` dictates whether updates to the collection have ACID properties or not
* `wait_sync` [forces synchronization of the document creation operation to disk](https://www.arangodb.com/docs/stable/data-modeling-documents-document-methods.html)
* `gather_dest` is the directory where the results will be gathered on the manager VM

Let's execute the benchmark with the following parameters:

```shell
$ ansible-playbook benchmark-run.yaml -e replicas=2 -e workload=workloadc -e operation_count=20000 -e threads=2 -e target=0 -e gather_dest=~/results
...
```

### Examining the Results

TODO
