#!/bin/bash
# Deploy to AWS from your local
set -o errexit
set -o pipefail
set -o nounset

# STAGE
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
  BRANCH=develop
  PROFILE=denaribot_dev
elif [[ "$choice" == stg ]]; then
  STAGE=stg
  BRANCH=staging
  PROFILE=denaribot_stg
elif [[ "$choice" == prod ]]; then
  STAGE=prod
  BRANCH=main
  PROFILE=denaribot_prod
else
  echo "'${choice}' Invalid choice."
  exit 1
fi

# pull the latest source code
echo
read -rp "Pull the latest source code y/n [n]: " choice
choice=${choice:-n}
if [[ "$choice" =~ ^[Yy]$ ]]; then
  git stash && git checkout "$BRANCH" && git reset "origin/${BRANCH}"
elif [[ "$choice" =~ ^[Nn]$ ]]; then
  echo "Skip pulling the latest source code."
else
  echo "'${choice}' Invalid choice."
  exit 1
fi

# Confirm the summary
echo
cat <<EOF
Summary:
STAGE - $STAGE
PROFILE - $PROFILE
BRANCH - $(git branch --show-current)
EOF
# Deploy to AWS
echo
read -rp "Continue to deploy? y/n [y]: " choice
choice=${choice:-y}
if [[ "$choice" =~ ^[Yy]$ ]]; then
  npx serverless deploy --stage "$STAGE" --aws-profile "$PROFILE"
elif [[ "$choice" =~ ^[Nn]$ ]]; then
  git status
else
  echo "'${choice}' Invalid choice."
  exit 1
fi
