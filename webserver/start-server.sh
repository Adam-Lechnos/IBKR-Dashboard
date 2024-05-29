#!/bin/bash

mv images webserver/static/ || true
mv favicon.ico webserver/static || true
python serve-html.py