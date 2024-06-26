#!/bin/bash

if [ -z "${sleepTimeSeconds}" ]; then
    sleepTimeSeconds=60
fi

echo "Refresh seconds: ${sleepTimeSeconds}"

# convert seconds specified to minutes in crontab file
let minutes=${sleepTimeSeconds}/60
sed -i 's/\/1/\/'${minutes}'/' crontab

# apply crontab file
crontab crontab
crond -f