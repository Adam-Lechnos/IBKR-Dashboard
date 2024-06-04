#!/bin/bash
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

python3 ./auth_gen_token.py

if [ ! -f ./mycreds.txt ]; then
    echo "Auth did not succeed, exting"
    exit 1
else
    echo "Token file already exists, proceeding"
fi

docker compose pull && docker compose up -d