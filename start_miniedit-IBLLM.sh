#!/bin/bash 

# Start the containers
echo "Starting Mininet-IBLLM and Ollama containers..."
docker compose up -d

# This script launches the GUI for the Mininet LLM project. It also forwards the port 11434 from the Mininet container to the ollama container.
docker exec -ti llm-mininet-mininet-1 bash -c "socat tcp-listen:11434,reuseaddr,fork tcp:ollama:11434 & source venv/bin/activate && python miniedit_IBLLM.py"

# Once the GUI is closed, stop the containers
echo "GUI closed. Stopping Mininet and Ollama containers..."
docker compose down