#!/bin/bash
##
TAG=""
##
# Exit on every error
set -e

#########################

# Updates hier einfügen #

# Neue Schwachstellenlöschung einpflegen
sudo cp -f /home/amadmin/box4s/main/home/actions.yml /home/amadmin/actions.yml

#Volume für elastalert anlegen
sudo mkdir -p /var/lib/elastalert/rules
sudo chown root:root /var/lib/elastalert/rules
sudo chmod -R 777 /var/lib/elastalert/rules
sudo docker volume create --driver local --opt type=none --opt device=/var/lib/elastalert/rules --opt o=bind varlib_elastalert_rules
sudo cp /home/amadmin/box4s/docker/elastalert/rules/* /var/lib/elastalert/rules/
# Apply new crontab
su - amadmin -c "crontab /home/amadmin/box4s/main/crontab/amadmin.crontab"

# Stop des Services
echo "Stopping BOX4s Service. The BOX4s service will automatically restart after the update is complete. Please wait."
sleep 8
sudo systemctl stop box4security.service

sudo docker-compose -f /home/amadmin/box4s/docker/box4security.yml pull


# Start des Services
echo "Starting BOX4s Service. Please wait."
sudo systemctl restart box4security.service

# Waiting for healthy containers before continuation
sudo /home/amadmin/box4s/scripts/System_Scripts/wait-for-healthy-container.sh elasticsearch
sudo /home/amadmin/box4s/scripts/System_Scripts/wait-for-healthy-container.sh logstash || sleep 30
sudo /home/amadmin/box4s/scripts/System_Scripts/wait-for-healthy-container.sh kibana || sleep 30
sudo /home/amadmin/box4s/scripts/System_Scripts/wait-for-healthy-container.sh nginx || sleep 30
# Update Suricata
sudo docker exec suricata /root/scripts/update.sh