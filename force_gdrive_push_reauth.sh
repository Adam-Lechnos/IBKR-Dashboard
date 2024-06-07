#!/bin/bash

# re-creates both auth token and container when access token witihn a running ibkr-push-gdrive container expires and cannot be renewed due to expired refresh token
# must be executed interactively to allow for command line OAuth flow to Google and return of access token

python3 ./auth_gen_token.py

if [ ! -f ./mycreds.txt ]; then
    echo "Auth did not succeed, exting"
    exit 1
else
    echo "Token file exists, proceeding"
fi

docker compose up -d --force-recreate ibkr-push-gdrive