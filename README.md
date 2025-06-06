# Miniedit-IBLLM

This repository contains a fork of the Miniedit GUI application, part of the Mininet framework. It provides an LLM-based Intent-Based Networking (IBN) framework that enables the creation and modification of Mininet networks using natural language intent. It utilizes the Ollama framework as the backend for LLM functionality. The framework accepts both text and image inputs, allowing users to recreate images directly within the Miniedit GUI.

This work is based on a research project done by Dani Termaat and Dr. M. (Marios) Avgeris from the University of Amsterdam. The paper of the work will be posted here as soon as we release it.

## Default Models

By default, the Miniedit-IBLLM framework uses the Mistral-Nemo 12B, Gemma3 12B, and Gemma3 4B models. Each model plays a specific role in the toolkit’s multi-agent architecture. To modify the models used, update the constants in `modules/LLM/constants.py`.

## Installation

Automated scripts are provided to simplify installation and usage. Note that the installation script is designed for Nvidia-based systems and includes installation of the NVIDIA Container Toolkit. To begin installation, run:

```console
chmod +x docker-installation.sh
sudo ./docker-installation.sh
```

This installs the necessary components for Docker and the NVIDIA Container Toolkit. Once complete, you can set up the Miniedit-IBLLM Docker container using:

```console
chmod +x docker-post_install.sh
sudo ./docker-post_install.sh
```

This script prepares the container environment for Docker Compose and includes the Miniedit-IBLLM GUI.

## Starting Miniedit-IBLLM

After installation, launch the framework with the following command:

```console
chmod +x start_miniedit-IBLLM.sh
sudo ./start_miniedit-IBLLM.sh
```

This will start the GUI and launch Ollama via Docker Compose.

## Updating the Docker Image

If you make changes to the framework, be sure to refresh the Docker container to apply them. A script is provided to streamline this process:

```console
chmod +x clean_docker.sh
sudo ./clean_docker.sh
```

## GUI usage
In the bottom left of the GUI, users can enter textual prompts; when pressing enter or the submit button, the framework will interact with the local models and execute tasks. The status of each step is displayed in the button as state updates.

### Multi-modal functionality
As for the usage of images to recreate topology, we have included two drawn examples. These can be selected in the Miniedit-IBLLM GUI by clicking on 'Upload image'. After, the user can enter a textual prompt and press enter or submit.
