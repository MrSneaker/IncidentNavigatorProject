#!/bin/bash

cd $(dirname $0)
WORKDIR=$(pwd)
echo -e "\e[1;34m[INFO]\e[0m Working directory: $WORKDIR"

# START DOCKER CONTAINERS
echo -e "\e[1;34m[INFO]\e[0m Checking if Docker is installed..."
if ! [ -x "$(command -v docker)" ]; then
    echo -e "\e[1;31m[ERROR]\e[0m Docker is not installed. Please install Docker and try again."
    exit 1
fi

echo -e "\e[1;34m[INFO]\e[0m Checking if Docker Compose is installed..."
if ! [ -x "$(command -v docker-compose)" ]; then
    echo -e "\e[1;31m[ERROR]\e[0m Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo -e "\e[1;34m[INFO]\e[0m Starting Docker containers..."
sudo docker-compose start
if [ $? -ne 0 ]; then
    echo -e "\e[1;31m[ERROR]\e[0m Failed to start Docker containers."
    exit 1
fi

# ACTIVATE PYTHON ENVIRONMENT
echo -e "\e[1;34m[INFO]\e[0m Activating Python virtual environment..."
if [ ! -d ".env" ]; then
    echo -e "\e[1;31m[ERROR]\e[0m Python virtual environment not found. Please run the installation script first."
    exit 1
fi

source .env/bin/activate
if [ $? -ne 0 ]; then
    echo -e "\e[1;31m[ERROR]\e[0m Failed to activate Python virtual environment."
    exit 1
fi

# START FLASK APPLICATION
echo -e "\e[1;34m[INFO]\e[0m Starting Flask application..."
cd ../.. # Needed because of the restart of the application during initialisation.
nohup python3 app/app.py > app/flask.log 2>&1 &
if [ $? -ne 0 ]; then
    echo -e "\e[1;31m[ERROR]\e[0m Failed to start Flask application."
    exit 1
fi

echo -e "\e[1;32m[SUCCESS]\e[0m Application started successfully! Navigate to http://localhost:5000. You can read log in the app/flask.log file."
