#!/bin/bash

cd $(dirname $0)
WORKDIR=$(pwd)
echo -e "\e[1;34m[INFO]\e[0m Working directory: $WORKDIR"  

# INSTALL DEPENDENCIES
echo -e "\e[1;34m[INFO]\e[0m Creating virtual environment..."
python3 -m venv .install_venv
echo -e "\e[1;34m[INFO]\e[0m Activating virtual environment..."
source .install_venv/bin/activate
echo -e "\e[1;34m[INFO]\e[0m Installing dependencies..."
pip install -r requirements.txt --quiet

# DOCKER
## Check if docker is installed
if ! [ -x "$(command -v docker)" ]; then
    echo -e "\e[1;31m[ERROR]\e[0m Docker is not installed. Please install docker and try again."
    exit 1
fi
## Check if docker-compose is installed
if ! [ -x "$(command -v docker-compose)" ]; then
    echo -e "\e[1;31m[ERROR]\e[0m Docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi
## Check if container is running
echo -e "\e[1;34m[INFO]\e[0m Stopping any running containers..."
sudo docker-compose down
echo -e "\e[1;34m[INFO]\e[0m Starting containers..."
sudo docker-compose up -d
# wait for the container to start
echo -e "\e[1;34m[INFO]\e[0m Waiting for containers to start..."
sleep 5

# DATABASE
echo -e "\e[1;34m[INFO]\e[0m Creating databases..."
python3 create_dbs.py
echo -e "\e[1;32m[SUCCESS]\e[0m Setup complete!"