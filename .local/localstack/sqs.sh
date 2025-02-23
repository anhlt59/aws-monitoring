#!/usr/bin/env bash

set -euo pipefail

# enable debug
# set -x

echo "configuring s3"
echo "==================="
AWS_REGION=us-east-1
VISIBILITY_TIMEOUT=30

# https://docs.aws.amazon.com/cli/latest/reference/sqs/create-queue.html
create_queue() {
  local QUEUE_NAME=$1
  local ENABLE_FIFO=${2:-false}

  if [ "$ENABLE_FIFO" == false ]; then
    local ATTRIBUTES="VisibilityTimeout=${VISIBILITY_TIMEOUT}"
  else
    local ATTRIBUTES="VisibilityTimeout=${VISIBILITY_TIMEOUT},FifoQueue=true"
  fi

  awslocal sqs create-queue \
    --queue-name "$QUEUE_NAME" \
    --attributes "$ATTRIBUTES" \
    --region "$AWS_REGION"
}

# IOT streams
create_queue denaribots-local-IOTStreams.fifo true
create_queue denaribots-local-IOTStreamDLQ.fifo true
# DynamoDB streams
create_queue denaribots-local-DynamoStreamDLQ
# Monitoring
create_queue denaribots-local-MonitorCase123
create_queue denaribots-local-MonitorCase4
create_queue denaribots-local-MonitorCase5
create_queue denaribots-local-MonitorCase6
create_queue denaribots-local-MonitorCase7
create_queue denaribots-local-MonitorDLQ
# Notification
create_queue denaribots-local-Notifications
create_queue denaribots-local-NotificationsDLQ
