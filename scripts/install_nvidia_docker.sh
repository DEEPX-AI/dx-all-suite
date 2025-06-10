#!/bin/bash

# refer: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

## Install NVIDIA Container Toolkit

# 1. Configure the production repository:
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 1-1. Optionally, configure the repository to use experimental packages:
sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list


# 2. Update the packages list from the repository:

sudo apt-get update

# 3. Install the NVIDIA Container Toolkit packages:
sudo apt-get install -y nvidia-container-toolkit


## install nvidia-docker2

# 1. install packages
sudo apt-get update
sudo apt-get install -y nvidia-docker2

# 2. restart docker service demon
sudo systemctl restart docker

# 3. test
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi

