#!/bin/bash

# Install pgcli

sudo apt-get update
sudo apt-get install -y python3-pip libpq-dev
pip3 install psycopg2-binary pgcli

export PATH=$(eval echo ~$USER)/.local/bin:${PATH}
echo "export PATH=${PATH}" >> ~/.bashrc

# Install Docker
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Run Docker
sudo usermod -aG docker $USER
echo "You will need to exit the terminal and re-enter before docker permissions are reset"
sudo docker kill pdl || true
sudo docker rm pdl || true
sudo docker rmi logstoneducation/pdl-advanced-sql:latest || true
sudo docker run -p 5432:5432 --env PGDATA=/pdl/data --detach --name pdl -t docker.io/logstoneducation/pdl-advanced-sql

echo "You are all set!"
echo "Try the following command: pgcli -h localhost -U postgres -d airline"
