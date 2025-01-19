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

#### Note: If you encounter permission issues with Docker on Linux, try running the commands with `sudo` or ensure your user is added to the Docker group

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

## Evaluation

### BEIR Benchmark for embeddings models

| **Model**                       | **NDCG@3** | **MAP@3** | **Recall@3** | **Precision@3** | **NDCG@10** | **MAP@10** | **Recall@10** | **Precision@10** | **NDCG@30** | **MAP@30** | **Recall@30** | **Precision@30** |
|-----------------------------------|------------|-----------|--------------|-----------------|-------------|------------|---------------|------------------|-------------|------------|---------------|-------------------|
| BAAI/bge-small-en-v1.5            | 0.38766    | 0.0847    | 0.09833      | 0.37255         | 0.3361      | 0.11749    | 0.15986       | 0.25325          | 0.30161     | 0.13719    | 0.22052       | 0.15294           |
| BAAI/bge-large-en                 | 0.39825    | 0.09866   | 0.10807      | 0.37564         | 0.34273     | 0.13283    | 0.16902       | 0.25077          | 0.31692     | 0.15491    | 0.23701       | 0.15542           |
| sentence-transformers/all-mpnet-base-v2 | 0.38528 | 0.08685   | 0.09944      | 0.37049         | 0.33366     | 0.12104    | 0.16199       | 0.25201          | 0.30722     | 0.1425     | 0.23177       | 0.15624           |
| intfloat/e5-large                 | **0.42656**| **0.10532**| **0.11589**  | **0.40248**     | **0.37556** | **0.14489**| **0.18625**   | **0.27709**      | **0.3455**  | **0.16929**| **0.25686**   | **0.17069**       |
| sentence-transformers/all-MiniLM-L6-v2 | 0.35476 | 0.07489   | 0.08583      | 0.33746         | 0.31425     | 0.11007    | 0.15886       | 0.24025          | 0.28666     | 0.12801    | 0.21727       | 0.14737           |
| sentence-transformers/gtr-t5-large| 0.39043    | 0.09262   | 0.10317      | 0.36739         | 0.32691     | 0.12083    | 0.15619       | 0.23406          | 0.29553     | 0.13804    | 0.21242       | 0.1418            |
| BAAI/bge-large-zh-v1.5            | 0.26704    | 0.05119   | 0.06084      | 0.24665         | 0.22158     | 0.06966    | 0.10174       | 0.16223          | 0.19627     | 0.07918    | 0.14605       | 0.09649           |

### User evaluation

To perform an empirical evaluation based on user satisfaction, we ask used a survey which can be accessed by clicking this [link](https://docs.google.com/forms/d/e/1FAIpQLSeJjsLwA0piXQqG0LpePXWf8MYUIZXKDx7mvkezLxrdCmWIYQ/viewform?usp=header)
