# -*- mode: ruby -*-
# vi: set ft=ruby :

require_relative "scripts/config"
require_relative "scripts/process"

params = process_config(read_config("config.yaml"))

# transforms the parameter hash into a multiline string
# which will be written into the VMs /etc/hosts file
def hosts_string(params)
  outer = []
  outer.append([params[:manager][:ip], params[:manager][:hostname]].join(" "))
  [:replica, :client].each do |n|
    params[n].each do |values|
      outer.append([values[:ip], values[:hostname]].join(" "))
    end
  end
  return outer.join("\\n")
end

def host_nodes(params, key)
  return [params[key][0][:hostname]]
end

def worker_nodes(params, key)
  return params[key][1..-1].map { |x| x[:hostname] }
end

Vagrant.configure("2") do |config|

  box = "ubuntu/focal64"

  # each node creates a private network to allow host-only access to each machine
  # using a static IP address
  # parameters like CPU count, memory capacity and the number of nodes
  # are defined in config.yaml

  # create replicated server nodes
  params[:replica].each do |server|
    config.vm.define server[:hostname] do |config|
      config.vm.box = box
      config.vm.hostname = server[:hostname]
      config.vm.network "private_network", ip: server[:ip]
      config.vm.provider "virtualbox" do |vb|
        vb.gui = false
        vb.name = config.vm.hostname
        vb.memory = server[:memory]
        vb.cpus = server[:cpus]
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      end # vb
      config.vm.provision "shell", path: "bootstrap_docker.sh"
    end # config
  end # loop

  # create client nodes
  params[:client].each do |client|
    config.vm.define client[:hostname] do |config|
      config.vm.box = box
      config.vm.hostname = client[:hostname]
      config.vm.network "private_network", ip: client[:ip]
      config.vm.provider "virtualbox" do |vb|
        vb.gui = false
        vb.name = config.vm.hostname
        vb.memory = client[:memory]
        vb.cpus = client[:cpus]
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      end # vb
      config.vm.provision "shell", path: "bootstrap_docker.sh"
    end # config
  end # loop

  # create manager node
  config.vm.define params[:manager][:hostname], primary: true do |config|
    block = params[:manager]
    config.vm.box = box
    config.vm.hostname = block[:hostname]
    config.vm.network "private_network", ip: block[:ip]
    config.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.name = config.vm.hostname
      vb.memory = block[:memory]
      vb.cpus = block[:cpus]
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end # vb

    config.vm.synced_folder "provisioning", "/home/vagrant/provisioning",
      owner: "vagrant",
      group: "vagrant",
      mount_options: ["dmode=775", "fmode=664"]

    config.vm.provision "shell",
      path: "bootstrap_manager.sh",
      env: {"VAGRANT_NODE_LIST" => hosts_string(params)}

    # ansible test and inventory generation
    config.vm.provision "ansible_local", install: false do |ansible|
      ansible.groups = {
        # the first replica and client nodes are the swarm managers/hosts
        # the rest are worker nodes
        "server_hosts" => host_nodes(params, :replica),
        "server_workers" => worker_nodes(params, :replica),
        "client_hosts" => host_nodes(params, :client),
        "client_workers" => worker_nodes(params, :client),
        "hosts:children" => ["server_hosts", "client_hosts"],
        "workers:children" => ["server_workers", "client_workers"]
      }
      ansible.playbook = "provisioning/self.yaml"
      ansible.verbose = true
    end # ansible
  end # config

end
