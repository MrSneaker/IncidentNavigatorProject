<h1 align="center">IncidentNavigatorProject</h1>

**An intelligent solution for efficient incident resolution using LLM and RAG.**

# Table of Contents

1. [📖 Introduction](#📖-introduction)
2. [🛠️ Installation](#🛠️-installation)
   - [Clone Repository](#clone-repository)
   - [Quick Install/Uninstall](#quick-installuninstall)
   - [Manual Setup](#manual-setup)
3. [🔧 Launch Server](#🔧-launch-server)
   - [Quick Launch](#quick-launch)
   - [Manual Launch](#manual-launch)
4. [🔒 Default Admin Credentials](#🔒-default-admin-credentials)
5. [📝 User Evaluation](#📝-user-evaluation)

---

# 📖 Introduction

**IncidentNavigator** is a solution designed to streamline recurring incident resolution. Using a Large Language Model (LLM) and Retrieval-Augmented Generation (RAG), it offers:

- Dynamic interaction for clarifying queries.
- Transparent, fact-based responses.
- Adaptability to structured and unstructured data.

# 🛠️  Installation

Ensure the following are installed on your system:

- [Python 3.12.4+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/)

## Clone Repository

```bash
git clone https://github.com/MrSneaker/IncidentNavigatorProject.git
cd IncidentNavigatorProject
```

## Quick install/uninstall

### Install

   This script will handle the creation of the virtual environment, installation of required Python packages, and any other necessary setup steps.

   ```bash
   sudo ./app/install/install.sh
   ```

### Uninstall

   This script is used to uninstall the application.It performs the necessary steps to remove the application and its associated files from the system.

   ```bash
   sudo ./app/install/uninstall.sh
   ```

---

## Manual Setup

1. **Navigate to the installation directory:**

   ```bash
   cd app/install
   ```

2. **Docker services:**

   Docker allows you to build and run services along with its dependencies in a containerized environment making it so you do not need to install them locally. As our applications need **Weaviate**, **MongoDB** and **Redis** we thus provide a [docker-compose.yml](app/install/docker-compose.yml) file to make it easier to install and use them.

   - **Start :**

      ```bash
      docker compose up -d
      ```

   - **Stop :**

      ```bash
      docker compose down
      ```

   ***Note:*** *If you encounter permission issues with Docker on Linux, try running the commands with sudo or ensure your user is added to the Docker group (`sudo usermod -aG docker $USER`)*

3. **Set up a Python environment:**

   ```bash
   python -m venv .env
   source .env/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

4. Populate databases:

   ```bash
   python3 create_dbs.py  # Use [-c | --clear] to reset databases.
   ```

---

# 🔧 Lauch Server

## Quick Launch

```bash
sudo ./app/install/start.sh
```

This script will start all components for you. Navigate to [http://localhost:5000](http://localhost:5000) to access the homepage.

```bash
sudo ./app/install/stop.sh
```

This script will stop all running components.
  
## Manual Launch

  1. **Navigate to the project root directory:**

      Ensure you are in the root directory of the project before proceeding with the following steps.

      ```bash
      cd /path/to/IncidentNavigatorProject
      ```

  2. **Set up the Python environment:**

      Activate the installed environment:

      ```bash
      source app/install/.env/bin/activate  # Linux/macOS
      ```

  3. **Launch the Flask application:**

      ```bash
      python3 app/app.pySimplifiez les phrases pour les rendre plus fluides en français. Par exemple :lhost:5000, you will be directed to the homepage.

# 🔒 Default Admin Credentials

The application comes with a default admin account for initial use:

- **Email:** `admin@example.com`
- **Password:** `admin`

> **Important:** It is highly recommended to change the password after the first login to secure the application.

---

## 📝 User Evaluation

Participate in our user evaluation by filling out this [survey](https://docs.google.com/forms/d/e/1FAIpQLSeJjsLwA0piXQqG0LpePXWf8MYUIZXKDx7mvkezLxrdCmWIYQ/viewform?usp=header).
