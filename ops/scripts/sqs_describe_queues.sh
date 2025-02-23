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
  attributes=$(
    aws sqs get-queue-attributes \
      --queue-url "$queue" \
      --endpoint "$ENDPOINT" \
      --region "$REGION" \
      --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible ApproximateNumberOfMessagesDelayed
  )
  echo ApproximateNumberOfMessages: "$(jq -r ".Attributes .ApproximateNumberOfMessages" <<<"$attributes")"
  echo ApproximateNumberOfMessagesNotVisible: "$(jq -r ".Attributes .ApproximateNumberOfMessagesNotVisible" <<<"$attributes")"
  echo ApproximateNumberOfMessagesDelayed: "$(jq -r ".Attributes .ApproximateNumberOfMessagesDelayed" <<<"$attributes")"
done
