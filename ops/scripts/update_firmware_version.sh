#!/bin/bash

set -o errexit
set -o pipefail

# --------------------------------------------------------------------------------------------
# STAGE & FIRMWARE_VERSION
cat <<EOF
Select a stage:
- dev
- stg
- prod
EOF
read -rp "Choose from dev, stg, prod [dev]: " choice
choice=${choice:-dev}
if [[ "$choice" == dev ]]; then
    STAGE=dev
    PROFILE=denaribot_dev
elif [[ "$choice" == stg ]]; then
    STAGE=stg
    PROFILE=denaribot_stg
elif [[ "$choice" == prod ]]; then
    STAGE=prod
    PROFILE=denaribot_prod
else
    echo "'${choice}' Invalid choice."
    exit 1
fi
read -rp "Enter firmware_version [0.0.019]: " FIRMWARE_VERSION
FIRMWARE_VERSION=${FIRMWARE_VERSION:-0.0.019}
if ! [[ $FIRMWARE_VERSION =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
    echo "Invalid firmware version format. Example: 1.1.0"
    exit 1
fi
read -rp "Enter download_url [denaribots-stg-firmware.s3.ap-northeast-1.amazonaws.com]: " DOWNLOAD_URL
DOWNLOAD_URL=${DOWNLOAD_URL:-denaribots-stg-firmware.s3.ap-northeast-1.amazonaws.com}
if [[ -z "$DOWNLOAD_URL" ]]; then
    echo "Download URL cannot be empty"
    exit 1
fi

# Review and confirm inputs
clear
cat <<EOF
Summary:
STAGE - $STAGE
FIRMWARE VERSION - $FIRMWARE_VERSION
DOWNLOAD URL - $DOWNLOAD_URL
EOF

echo
read -rp "Continue to update firmware? (y/n) [y]: " choice
choice=${choice:-y}
if [[ "$choice" != "y" ]]; then
    echo "Aborting..."
    exit 1
fi

# --------------------------------------------------------------------------------------------
trigger_start_firmware_update() {
    # Triggers the StartFirmwareUpdate Lambda function
    response=$(aws lambda invoke \
        --function-name "denaribots-${STAGE}-StartFirmwareUpdate" \
        --invocation-type RequestResponse \
        --cli-binary-format raw-in-base64-out \
        --payload "{\"version\": \"${FIRMWARE_VERSION}\", \"url\": \"${DOWNLOAD_URL}\"}" \
        --profile "$PROFILE" \
        --query 'StatusCode' \
        --output text /dev/null)

    if [ "$response" -eq 200 ]; then
        return 0
    else
        echo "Error triggering StartFirmwareUpdate: Status code $response"
        return 1
    fi
}

trigger_check_firmware_update() {
    # Triggers the CheckFirmwareUpdate Lambda function
    response=$(aws lambda invoke \
        --function-name "denaribots-${STAGE}-CheckFirmwareVersion" \
        --invocation-type RequestResponse \
        --profile "$PROFILE" \
        --query 'StatusCode' \
        --output text /dev/null)

    if [ "$response" -eq 200 ]; then
        return 0
    else
        echo "Error triggering CheckFirmwareUpdate: Status code $response"
        return 1
    fi
}
# --------------------------------------------------------------------------------------------

# First trigger StartFirmwareUpdate
echo "Starting firmware update for '${FIRMWARE_VERSION}' on ${STAGE}"
if ! trigger_start_firmware_update; then
    echo "Failed to start firmware update"
    exit 1
fi

# Check firmware update
for i in {1..2}; do
    # Wait 15 minutes before next check
    sleep 900
    if trigger_check_firmware_update; then
        echo "Check firmware update triggered at $(date)"
    else
        echo "Failed to trigger check firmware update at $(date)"
    fi
done
