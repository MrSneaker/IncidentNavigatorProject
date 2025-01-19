# IncidentNavigatorProject

## Installation

### Prerequisites

Ensure you have the following installed on your system:

- [Python 3.12.4+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/)

### Install Python Dependencies

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/MrSneaker/IncidentNavigatorProject.git
   cd IncidentNavigatorProject
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

   This command reads the `requirements.txt` file and installs all the listed dependencies into your virtual environment.

4. Verify the installation:

   ```bash
   python -m pip list
   ```

---

### Install the required frameworks

Docker allows you to build and run services along with its dependencies in a containerized environment making it so you do not need to install them locally. As our applications need Weaviate, MongoDB and Redis we thus provide a docker-compose file to make it easier to install and use them.

1. Build and start the services using the `docker-compose.yml` file:

   ```bash
   docker compose up -d
   ```

2. To stop the services, press `CTRL+C` in the terminal, and then run:

   ```bash
   docker-compose down
   ```

   This command stops and removes all the containers created by Docker Compose.

#### Note: If you encounter permission issues with Docker on Linux, try running the commands with `sudo` or ensure your user is added to the Docker group.

---

##  Getting started

###  Fill the databases (Weaviate and Mongo)

Before starting you will need to have filled the Weaviate and Mongo Databases wuth the necessary data as such we have provided a script which performs said operation.
    ```
    python create_dbs.py
    ```

###   Start servers locally

You will have to start two componant locally.

#### The flask server

To start the flask server, run the following in a terminal:

   ```bash
   cd app && python3 app.py
   ```

The server should start without any problem.

####  The npm server

To start the npm server, run the following in a terminal:

   ```bash
   cd incident-nav-react && npm install && npm run start
   ```

Then the npm server should start and open the app in your default browser on this default adress: <http://localhost:3000/>.

#### User evaluation

To perform an empirical evaluation based on user satisfaction, we ask used a survey which can be accessed by clicking this [link](https://docs.google.com/forms/d/e/1FAIpQLSeJjsLwA0piXQqG0LpePXWf8MYUIZXKDx7mvkezLxrdCmWIYQ/viewform?usp=header)