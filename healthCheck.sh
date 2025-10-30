#! /bin/bash

setTZ="America/New_York"
setServiceName="ibkr-dashboard-1"
dashboardConName="ibkr-dashboard-nginx"

echo -e "**** IBKR Health Check *****\n"
logger -t "IBKR-Health" "**** IBKR Health Check *****"
logger -p user.info "Informational IBKR health check message"

docConDate=$(docker exec -e TZ=$setTZ $dashboardConName stat -c %y /usr/src/app/webserver/static/index.html | cut -d'.' -f1)
if [ $? -ne 0 ]; then
   echo "Command substituion to acquire last modified date of Index.html failed, restarting IBKR service"
   logger -t "IBKR-Health" "Command substituion to acquire last modified date of Index.html failed, restarting IBKR service"
   logger -p user.info "Informational IBKR health check message"
   sudo systemctl restart $setServiceName
fi

currDate=$(TZ=$setTZ date +"%Y-%m-%d %H:%M:%S")

echo "IBKR Dashboard last modified date for Index.html: $docConDate"
logger -t "IBKR-Health" "IBKR Dashboard last modified date for Index.html: $docConDate"
logger -p user.info "Informational IBKR health check message"
echo "Current date: $currDate"
logger -t "IBKR-Health" "Current date: $currDate"
logger -p user.info "Informational IBKR health check message"

TSdocCon=$(date -d "$docConDate" +%s)
TScurr=$(date -d "$currDate" +%s)

DIFF_SECONDS=$((TScurr - TSdocCon))

echo -e "\nIndex.html last update is $DIFF_SECONDS seconds behind"
logger -t "IBKR-Health" "Index.html last update is $DIFF_SECONDS seconds behind"
logger -p user.info "Informational IBKR health check message"

TWELVE_HOURS=$((12 * 60 * 60))

if [ "$DIFF_SECONDS" -gt "$TWELVE_HOURS" ]; then
    echo -e "\nThe dates are more than 12 hours apart, restarting IBKR serivce"
    logger -t "IBKR-Health" "The dates are more than 12 hours apart, restarting IBKR serivce"
    logger -p user.info "Informational IBKR health check message"
    sudo systemctl restart $setServiceName
else
    echo -e "\nThe dates are not more than 12 hours apart, service healthy"
    logger -t "IBKR-Health" "The dates are not more than 12 hours apart, service healthy"
    logger -p user.info "Informational IBKR health check message"
fi

exit 0
