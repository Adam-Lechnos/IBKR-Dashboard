#!/bin/bash

docker stop $(docker ps -q --filter name=ibeam) && docker stop $(docker ps -q --filter name=ibkr)

exit 0
