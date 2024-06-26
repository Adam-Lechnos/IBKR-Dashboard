#!/bin/bash

read -p "This will destroy all users created within the htpasswd file, proceed? (Must enter 'proceed') " proceed

if [ $proceed != 'proceed' ]; then
    echo "Exiting, 'yes' not specified"
    exit 0
fi  

read -p "Enter Username: " userName
htpasswd -c ./.htpasswd $userName

docker compose up -d --force-recreate ibkr-dashboard-nginx