#!/bin/bash

gdrive_push_enabled="${1,,}"
target_string_gdrive="nogdrive"

# entry point and dependency check for starting the ibkr-dashboard

echo "Performing dependency checks.."

if [ ! -f ./env.list.ibeam ]; then
    echo "IBeam 'env.list.ibeam' environment file missing. Generate an encrypted password and key using 'gen_key_pw.py' then add to env.list.ibeam file."
    echo """Example:
            IBEAM_ACCOUNT=ibkr_user
            IBEAM_PASSWORD=ibkr_password
            IBEAM_KEY=ibkr_password_key
    """
    exit 1
fi

if [ ! -f ./env.list.gdrive ]; then
    echo "push-to-gdrive 'env.list.gdrive' environment file missing. Grab the desired Google Drive folder ID then add to env.list.gdrive file."
    echo """Example:
                folderId=FDGFDD45435DSFGDFSGD45
                refreshPushSeconds=60

            The folder ID is embedded within the URL within the target Google Drive folder. i.e., ../folders/{Folder ID}?resourceky
    """
    exit 1
fi

if [ ! -f ./env.list.parser ]; then
    echo "push-to-gdrive 'env.list.parser' environment file missing."
    echo """Example:
                sleepTimeSeconds=60

            'sleepTimeSeconds' specifies the api-parser refresh interval
    """
    exit 1
fi

if [ ! -f ./client_secrets.json ]; then
    echo "Client secrets file from Google OAuth Console not found, 'client_secrets.json, exiting'"
    exit 1
fi

if [ "$gdrive_push_enabled" != "$target_string_gdrive" ]; then
	
	python3 ./auth_gen_token.py

	if [ ! -f ./mycreds.txt ]; then
    		echo "Auth did not succeed, exting"
    		exit 1
	else
    		echo "Token file exists, proceeding"
	fi
fi

if [ ! -f ./.htpasswd ]; then
    echo "nginx basic auth file does not exist, creating"
    read -p "Enter Username: " userName
    htpasswd -c /.htpasswd $userName
else
    echo "basic auth file exists, proceeding"
fi

echo "PASSED"

# stop all running docker container for IBKR

echo "Stopping all running IBKR services.."                                                                             docker stop $(docker ps -q)

echo "STOPPED"


#start the containers depending on user argument

if [ "$gdrive_push_enabled" == "$target_string_gdrive" ]; then
	echo "Executing all services except GDrive Push service"
	docker compose pull && docker compose up ibeam -d ibkr-create-website -d ibkr-dashboard-nginx -d
else
	echo "Executing all services.."
	docker compose pull && docker compose up -d
fi

echo "IBKR Dashboard now running"

exit 0
