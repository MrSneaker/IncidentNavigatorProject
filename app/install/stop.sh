#!/bin/bash

cd $(dirname $0)
WORKDIR=$(pwd)
echo -e "\e[1;34m[INFO]\e[0m Working directory: $WORKDIR"

# STOP FLASK APPLICATION
echo -e "\e[1;34m[INFO]\e[0m Stopping Flask application..."
kill -9 `lsof -i:5000 -t`
echo -e "\e[1;32m[SUCCCESS]\e[0m Flask application stopped!"

# STOP DOCKER CONTAINERS
echo -e "\e[1;34m[INFO]\e[0m Stopping Docker containers..."
if ! [ -x "$(command -v docker-compose)" ]; then
    echo -e "\e[1;31m[ERROR]\e[0m Docker Compose is not installed. Skipping container stop."
    exit 1
fi

sudo docker-compose stop
if [ $? -eq 0 ]; then
    echo -e "\e[1;32m[SUCCESS]\e[0m Docker containers stopped."
else
    echo -e "\e[1;31m[ERROR]\e[0m Failed to stop Docker containers."
    exit 1
fi

echo -e "\e[1;32m[SUCCESS]\e[0m All components stopped successfully!"
