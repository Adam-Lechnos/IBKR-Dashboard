#!/bin/bash

# injection commands here
hostname -i > ${SRC_ROOT}/util-data/ip-addr.txt

# execute headless gateway
/bin/bash ${SRC_ROOT}/run.sh