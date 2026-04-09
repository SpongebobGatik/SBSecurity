#!/bin/bash

echo "Starting Minecraft Bot..."

if [ -z "$TELEGRAM_TOKEN" ]; then
    echo "ERROR: TELEGRAM_TOKEN not set!"
    exit 1
fi

mkdir -p /app/cryptomine

cd /app
if [ -f /app/serversbs.js ]; then
    node /app/serversbs.js &
    sleep 5
fi

export TELEGRAM_TOKEN="$TELEGRAM_TOKEN"
export PROXY_URL="$PROXY_URL"
python3 /app/bottelegram.py