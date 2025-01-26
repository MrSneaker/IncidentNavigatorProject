#!/bin/bash

cd $(dirname $0)
WORKDIR=$(pwd)
echo -e "\e[1;34m[INFO]\e[0m Working directory: $WORKDIR"

# REMOVE VIRTUAL ENVIRONMENT
if [ -d ".env" ]; then
    echo -e "\e[1;34m[INFO]\e[0m Removing virtual environment..."
    rm -rf .env
else
    echo -e "\e[1;33m[WARNING]\e[0m Virtual environment not found."
fi

# DOCKER
## Check if docker-compose is installed
if [ -x "$(command -v docker-compose)" ]; then
    echo -e "\e[1;34m[INFO]\e[0m Stopping and removing Docker containers..."
    sudo docker-compose down
else
    echo -e "\e[1;33m[WARNING]\e[0m Docker-compose is not installed."
fi

list_install_folders=('embedding_model' 'instance' 'mongo_data' 'weaviate_data')
for folder in ${list_install_folders[@]}; do
    if [ -d "$folder" ]; then
        echo -e "\e[1;34m[INFO]\e[0m Removing $folder..."
        rm -rf $folder
    else
        echo -e "\e[1;33m[WARNING]\e[0m $folder not found."
    fi
done

echo -e "\e[1;32m[SUCCESS]\e[0m Uninstallation complete!"