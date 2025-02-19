#!/bin/bash

echo "Waiting for redpanda_script to stop..."
while docker ps --format '{{.Names}}' | grep -q "redpanda_script"; do
    sleep 5
done

echo "Starting Python script..."
exec "$@"