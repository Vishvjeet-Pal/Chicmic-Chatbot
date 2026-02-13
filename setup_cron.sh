#!/bin/bash

PROJECT_DIR="/home/chicmic/Desktop/chatbot/Chicmic-Chatbot"
PYTHON="$PROJECT_DIR/.venv/bin/python3"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"

CRON_JOBS=$(cat <<EOF
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Leave policy 
43 14 * * * cd $PROJECT_DIR && $PYTHON background-jobs/leave_policy_job.py >> $LOG_DIR/leave_policy.log 2>&1

# Leave calculation 
43 14 * * * cd $PROJECT_DIR && $PYTHON background-jobs/leave_calculation_job.py >> $LOG_DIR/leave_calc.log 2>&1

# Holiday 
43 14 * * * cd $PROJECT_DIR && $PYTHON background-jobs/holiday_job.py >> $LOG_DIR/holiday.log 2>&1

# Referral 
43 14 * * * cd $PROJECT_DIR && $PYTHON background-jobs/referral_job.py >> $LOG_DIR/referral.log 2>&1

# Timesheet 
43 14 * * * cd $PROJECT_DIR && $PYTHON background-jobs/timesheet_job.py >> $LOG_DIR/timesheet.log 2>&1
EOF
)

# Install cron jobs
echo "$CRON_JOBS" | crontab -

echo "✅ Cron jobs installed successfully!"
crontab -l
