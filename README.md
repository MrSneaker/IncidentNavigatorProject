# IncidentNavigatorProject

## Table of Contents

1. [Installation](#1-installation)
   - [Prerequisites](#prerequisites)
   - [Clone repository](#clone-repository)
   - [Automated Installation](#automated-installation)
   - [Manual Installation](#manual-installation)
2. [Launch the server](#2-launch-the-server)
   - [Automated launch](#automated-launch)
   - [Manual launch](#manual-launch)
3. [Stop the server](#3-stop-the-server)
   - [Automated stop](#automated-stop)
   - [Manual stop](#manual-stop)

## 1. Installation

### Prerequisites

Ensure you have the following installed on your system:

- [Python 3.12.4+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/)

### Clone repository

```bash
   git clone https://github.com/MrSneaker/IncidentNavigatorProject.git
   cd IncidentNavigatorProject
```

### Automated Installation

   ```bash
   sudo ./app/install/install.sh
   ```

   This script will handle the creation of the virtual environment, installation of required Python packages, and any other necessary setup steps.

### Manual Installation

If you prefer to manually set up the project, follow these steps:

1. **Navigate to the installation directory**

   ```bash
   cd app/install
   ```

2. **Install the required frameworks**

   Docker allows you to build and run services along with its dependencies in a containerized environment making it so you do not need to install them locally. As our applications need **Weaviate**, **MongoDB** and **Redis** we thus provide a [docker-compose.yml](app/install/docker-compose.yml) file to make it easier to install and use them.

   ```bash
   docker compose up -d
   ```

   To stop and remove the containers, you can use the following command (from the `app/install` directory):

   ```bash
   docker compose down
   ```

   ***Note:***
   *If you encounter permission issues with Docker on Linux, try running the commands with `sudo` or ensure your user is added to the Docker group (`sudo usermod -aG docker $USER`)*

3. **Setup Python environment and install requirements**

   In this step, you will create a Python virtual environment and install the script's dependencies from the [requirements.txt](app/install/requirements.txt) file

   ```bash
   python -m venv .installenv
   source .installenv/bin/activate  # linux & macos
   # .installenv\Scripts\activate  # windows
   pip install -r requirements.txt
   ```

4. **Fill the databases (Weaviate and Mongo)**

   Before starting, you will need to fill the Weaviate and Mongo databases with the necessary data. We have provided a script to perform this operation. You can also use the `-c` or `--clear` option to clear the databases before filling them.

   ```bash
   python3 create_dbs.py # [-c | --clear]
   ```

## 2. Launch the server

###  Automated launch

   ```bash
   sudo ./app/install/start.sh
   ```

   This script will start every components for you.

### Manual launch

1. **Navigate to the project root directory**

   Ensure you are in the root directory of the project before proceeding with the following steps.

   ```bash
   cd /path/to/IncidentNavigatorProject
   ```

2. **Setup Python environment and install requirements**

   In this step, you will create a Python virtual environment and install the script's dependencies from the [requirements.txt](app/requirements.txt) file

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # linux & macos
   # .venv\Scripts\activate  # windows
   pip install -r app/requirements.txt
   ```

3. **Start the Flask application**

   To start the flask server, run the following cmd:

   ```bash
   python3 app/app.py
   ```

   You can then navigate to [http://localhost:5000](http://localhost:5000), you will be directed to the homepage.

## 3. Stop the server

###  Automated stop

   ```bash
   sudo ./app/install/stop.sh
   ```

   This script will stop every components for you.

### Manual stop

1. **Stop the Flask application**

   If the Flask server is running in your terminal, press `Ctrl+C` to stop it.

2. **Stop the Docker containers**

   Navigate to the `app/install` directory and use the following command to stop and remove the containers:

   ```bash
   docker compose down
   ```

   ***Note:*** If you encounter permission issues on Linux, prepend the command with `sudo`.

## User evaluation

To perform an empirical evaluation based on user satisfaction, we ask users a survey which can be accessed by clicking this [link](https://docs.google.com/forms/d/e/1FAIpQLSeJjsLwA0piXQqG0LpePXWf8MYUIZXKDx7mvkezLxrdCmWIYQ/viewform?usp=header)
