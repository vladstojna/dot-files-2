#!/usr/bin/env bash

apt-get update
apt-get -y upgrade

# remove old versions if present
apt-get remove docker docker-engine docker.io containerd runc

# install dependencies
apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get -y install docker-ce docker-ce-cli containerd.io

docker --version

groupadd docker || true
usermod -aG docker vagrant
