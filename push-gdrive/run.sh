#!/bin/bash

if [ -z "${refreshPushSeconds}" ]; then
    refreshPushSeconds=60
fi

echo "Refresh seconds: ${refreshPushSeconds}"

# convert seconds specified to minutes in crontab file
let minutes=${refreshPushSeconds}/60
sed -i 's/\/1/\/'${minutes}'/' crontab

# apply crontab file
crontab crontab
crond -f