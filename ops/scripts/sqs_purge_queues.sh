#!/bin/bash

set -o errexit
set -o pipefail

ENDPOINT=http://localhost:4566
REGION=us-east-1

RESPONSE=$(aws sqs list-queues --endpoint "$ENDPOINT" --region "$REGION" | jq -r ".QueueUrls[]")
QUEUE_URLS=($RESPONSE)

for queue in "${QUEUE_URLS[@]}"; do
  echo "----------------------------------------------------------------------------------------------------"
  echo "Queue: $queue"
  aws sqs purge-queue --queue-url "$queue" --endpoint "$ENDPOINT" --region "$REGION"
  echo Done
done
