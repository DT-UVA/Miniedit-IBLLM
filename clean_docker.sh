#!/bin/bash

# This script is used to clean up Docker containers and images related to Mininet.
echo "Cleaning up Docker containers and images..."
docker rm llm-mininet-mininet-1
docker image rm mininet

echo "Building the Docker image..."
docker build -t mininet .