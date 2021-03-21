#!/bin/bash

sudo apt update
sudo apt install -y wget

# Install pgcli
sudo apt install -y python3-pip libpq-dev
pip3 install psycopg2-binary pgcli

export PATH=$(eval echo ~$USER)/.local/bin:${PATH}
echo "export PATH=${PATH}" >> ~/.bashrc

# Install Docker
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common \
	postgresql-client-11

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Run Docker
sudo usermod -aG docker $USER
echo "You will need to exit the terminal and re-enter before docker permissions are reset"
sudo docker kill pdl || true
sudo docker rm pdl || true
sudo docker rmi logstoneducation/pdl-advanced-sql:latest || true
sudo docker run -p 5432:5432 --env PGDATA=/pdl/data --detach --name pdl -t docker.io/logstoneducation/pdl-advanced-sql:latest

# Wait for server to spin up
sleep 60

# Dump data for possible use with cockroachDB
pg_dump -U postgres -h 127.0.0.1 -d airline --no-owner --no-comments > airline.sql

echo "You are all set!"
echo "Try the following command: pgcli -h localhost -U postgres -d airline"
