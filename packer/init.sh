#!/bin/bash

uname -a
uptime

sudo apt update && sudo apt install -y git
ssh-keyscan bitbucket.org >> ~/.ssh/known_hosts
git clone git@bitbucket.org:LogstonEducation/pdl-advanced-sql-material-prep.git ~/pdl-advanced-sql-material-prep

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt update
sudo apt -y install postgresql-12 postgresql-client-12
systemctl status postgresql.service

sudo apt install -y python3-venv
cd ~/pdl-advanced-sql-material-prep
python3 -m venv env
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
