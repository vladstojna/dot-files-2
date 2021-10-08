#!/usr/bin/env bash

apt-get update
apt-get -y upgrade

# install ansible
apt-get -y install software-properties-common
apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get -y install ansible

# configure hosts file for the internal network defined by Vagrant
hosts="/etc/hosts"
if [ ! -f "$hosts.default" ]; then
    cp "$hosts" "$hosts.default"
else
    cp "$hosts.default" "$hosts"
fi

echo "# vagrant environment nodes" >> "$hosts"
echo -e ${VAGRANT_NODE_LIST} >> "$hosts"
