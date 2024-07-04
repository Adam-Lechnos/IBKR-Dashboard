#!/bin/bash

mv images /usr/src/app/webserver/static/ || true
mv favicon.ico /usr/src/app/webserver/static/ || true

dateTime = $(date)
if [ ! -f /usr/src/app/webserver/static/index.html ]; then
    echo "No parsing has occured yet. Is the api-parser container running? (${dateTime})" > /usr/src/app/webserver/static/index.html
fi

nginx -g "daemon off;"