#!/bin/bash 

echo "Building Docker image for Mininet"
# Create the mininet container
docker build -t mininet .

echo "Pulling required Ollama models"

## Pull the required images
# Vision model
docker exec -it ollama ollama pull mistral-nemo:12b

# Tool model
docker exec -it ollama ollama pull gemma3:12b

# Response model
docker exec -it ollama ollama pull gemma3:4b

echo "The Docker environment is set up. You can now run the following command to start the Mininet GUI:"
echo "bash start_gui.sh"