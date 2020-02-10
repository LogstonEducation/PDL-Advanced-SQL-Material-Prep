#!/bin/bash

uname -a
uptime

sudo apt update
sudo apt install -y make

curl -sSO https://dl.google.com/cloudagents/install-monitoring-agent.sh
sudo bash install-monitoring-agent.sh
rm install-monitoring-agent.sh

sudo apt update && sudo apt install -y git
ssh-keyscan bitbucket.org >> ~/.ssh/known_hosts
git clone git@bitbucket.org:LogstonEducation/pdl-advanced-sql-material-prep.git ~/pdl-advanced-sql-material-prep

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt update
sudo apt -y install postgresql-12 postgresql-client-12
systemctl status postgresql.service

sudo /bin/bash -c "cat > /etc/postgresql/12/main/pg_hba.conf" <<EOF
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
EOF

sudo systemctl restart postgresql.service
sleep 5
psql -U postgres -c "CREATE DATABASE airline"

sudo apt install -y python3-venv
cd ~/pdl-advanced-sql-material-prep
python3 -m venv env
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
