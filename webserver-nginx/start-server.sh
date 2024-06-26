#!/bin/bash

mv images /usr/src/app/webserver/static/ || true
mv favicon.ico /usr/src/app/webserver/static/ || true
nginx -g "daemon off;"