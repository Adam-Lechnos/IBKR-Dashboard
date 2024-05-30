#!/bin/bash

# sleep 5
# mv /var/data-ref/ibkr/client_secrets.json /usr/src/app/client_secrets.json || true

echo "Refresh seconds: $refreshPushSeconds"
python push-to-gdrive.py $refreshPushSeconds