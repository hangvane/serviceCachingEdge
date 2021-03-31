#!/bin/bash
wget --no-check-certificate https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b
ln -s /root/miniconda3/etc/profile.d/conda.sh /etc/profile.d/conda.sh
/root/miniconda3/bin/conda create -q -npy37 python=3.7 -y
/root/miniconda3/envs/py37/bin/pip install -r requirements.txt
/root/miniconda3/bin/conda install -y -npy37 -c conda-forge lpsolve55
/root/miniconda3/bin/conda install -y -npy37 keras
apt update
apt install -y libltdl7
wget --no-check-certificate https://download.docker.com/linux/ubuntu/dists/artful/pool/stable/amd64/docker-ce_18.06.3~ce~3-0~ubuntu_amd64.deb
dpkg -i *.deb
docker pull networkstatic/iperf3