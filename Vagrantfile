# -*- mode: ruby -*-
# vi: set ft=ruby :

require_relative "scripts/config"
require_relative "scripts/process"

cfg = read_config("config.yaml")
params = process_config(cfg)

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
    config.vm.provision "shell",
      path: "bootstrap_manager.sh",
      env: {"VAGRANT_NODE_LIST" => hosts_string(params)}
  end # config

end
