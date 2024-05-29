#!/bin/bash

success=false
retrySeconds=$1

if [ -z "${retrySeconds}" ]; then
    echo "No retry in seconds set, defaulting to 60 seconds (1 minute)"
    retrySeconds=10
fi


while [ $success = "false" ]; do
    python ./rest-parse-createWebsite.py $retrySeconds
    curent_date_time=$(date)
    echo "Retrying rest-parse program. Check IBeam Gateway container and it's open port. Timestampe: $current_date_time"
    sleep 5
done