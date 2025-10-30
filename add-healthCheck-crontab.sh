#!/bin/bash

# Define the full path to your script
SCRIPT_PATH="/home/opc/repos/IBKR-Dashboard/healthCheck.sh"

# Validate if the script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

# Get the current crontab entries
CURRENT_CRONTAB=$(crontab -l 2>/dev/null)

# Define the new cron entry (every hour at minute 0)
CRON_ENTRY="0 * * * * $SCRIPT_PATH"

# Check if the entry already exists to avoid duplication
if echo "$CURRENT_CRONTAB" | grep -Fq "$CRON_ENTRY"; then
    echo "Cron job for $SCRIPT_PATH already exists."
else
    # Add the new cron entry
    (echo "$CURRENT_CRONTAB"; echo "$CRON_ENTRY") | crontab -
    echo "Cron job added for $SCRIPT_PATH to run every hour."
fi

exit 0
