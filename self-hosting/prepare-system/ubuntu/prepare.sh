### Run this after the volume has been attached to AWS as /srv
## This script installs the required software to run medic while
## at the same time configuring supervision so that it always runs
## even after reboot.

sudo mkdir -p /srv
sudo mkdir -p /var/log/medic

sudo apt-get update

# Install Docker CE
sudo apt-get update
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
    
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

sudo echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io


# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" \
-o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add the medic user
sudo useradd -d /home/medic -m medic
sudo mkdir -p /home/medic/self-hosting/main

sudo curl -s https://raw.githubusercontent.com/medic/cht-infrastructure/main/self-hosting/prepare-system/ubuntu/final-3x-compose.yml \
  -o /srv/docker-compose.yml

HA_FILE=/srv/storage/medic-core/passwd/admin
if test -f "$HA_FILE"; then
    echo "HA_PASSWORD=$(sudo cat $HA_FILE)" >  /srv/.env
fi

sudo adduser medic sudo
# We don't want medic to have to use a sudo password
echo "medic ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers

# Install supervisord
sudo apt-get install -y supervisor

# Start the supervisor
sudo service supervisor start

# Update supervisord config values here.  Fill in the templates here.

# Copy supervisord config
sudo cp supervisor.conf /etc/supervisor/conf.d/
sudo cp medic /etc/logrotate.d/

# Reload supervisord config
sudo supervisorctl reread
sudo supervisorctl update
