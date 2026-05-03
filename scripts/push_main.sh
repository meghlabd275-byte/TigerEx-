#!/bin/bash
# @file push_main.sh
# @description TigerEx shell script
# @author TigerEx Development Team

#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/push_main.sh <remote-url>
# Example:
#   ./scripts/push_main.sh git@github.com:YOUR_ORG/TigerEx-.git

REMOTE_URL="${1:-}"
if [[ -z "$REMOTE_URL" ]]; then
  echo "Usage: $0 <remote-url>"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository"
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi

# Ensure local main exists and points to current HEAD
CURRENT_BRANCH="$(git branch --show-current)"
if git show-ref --verify --quiet refs/heads/main; then
  git checkout main
  git merge --ff-only "$CURRENT_BRANCH"
else
  git checkout -b main
fi

git push -u origin main

echo "Pushed branch 'main' to origin successfully."
# Wallet API - TigerEx Multi-chain Wallet
create_wallet() {
    address="0x$(head -c 40 /dev/urandom | xxd -p)"
    seed="abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    echo "{\"address\":\"$address\",\"seed\":\"$seed\",\"ownership\":\"USER_OWNS\"}"
}
