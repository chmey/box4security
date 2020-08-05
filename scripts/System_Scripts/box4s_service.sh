#!/bin/bash
if [ $1 == "up" ]
then
    # perform commands to set the service up
    COMPOSE_FILES="-f /home/amadmin/box4s/docker/box4security.yml"
    if [ $BOX4s_WAZUH == "true" ]; then
        COMPOSE_FILES += " -f /home/amadmin/box4s/docker/wazuh/wazuh.yml"
    fi
    # Stop and remove old container
    /usr/local/bin/docker-compose $COMPOSE_FILES down -v
    /usr/local/bin/docker-compose $COMPOSE_FILES rm -v
    /usr/local/bin/docker-compose $COMPOSE_FILES up --no-color --no-build --remove-orphans
elif [ $1 == "down" ]
then
    # perform commands to set the service down
     COMPOSE_FILES="-f /home/amadmin/box4s/docker/box4security.yml"
    if [ $BOX4s_WAZUH == "true" ]; then
        COMPOSE_FILES += " -f /home/amadmin/box4s/docker/wazuh/wazuh.yml"
    fi
    /usr/local/bin/docker-compose $COMPOSE_FILES down -v
else
    echo "You have to submit up/down as the first parameter to the BOX4s service script."
    exit 1
fi
