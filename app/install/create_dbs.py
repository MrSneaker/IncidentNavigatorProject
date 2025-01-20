import os
import pandas as pd
import uuid
from html import unescape
import warnings
import argparse
from pymongo import MongoClient
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import weaviate
from weaviate.collections import Collection
from langchain_weaviate.vectorstores import WeaviateVectorStore

# Supprimer les warnings inutiles
warnings.filterwarnings("ignore")

# Configuration
WORKING_DIR = os.path.dirname(__file__)
os.chdir(WORKING_DIR)

DATABASE_NAME = "incident_db"
COLLECTION_NAME = "incident_collection"
DATAFRAME_PATH = "data/cleaned.csv"
EMBEDDINGS_MODEL = "intfloat/e5-large-v2"
EMBEDDINGS_PATH = "embedding_model"
HTTP_HOST = "localhost"
HTTP_PORT = 8081
HTTP_SECURE = False
MONGO_URI = "mongodb://root:root@localhost:27017/"
GRPC_HOST = "localhost"
GRPC_PORT = 50051
GRPC_SECURE = False

# ================== UTILITAIRES DE LOG ================== #
def log_info(message, end="\n"):
    print(f"\x1b[1;34m[INFO]\x1b[0m {message}", end=end)

def log_success(message, end="\n"):
    print(f"\x1b[1;32m[SUCCESS]\x1b[0m {message}", end=end)

def log_warning(message, end="\n"):
    print(f"\x1b[1;33m[WARNING]\x1b[0m {message}", end=end)

def log_error(message, end="\n"):
    print(f"\x1b[1;31m[ERROR]\x1b[0m {message}", end=end)

# ================== DATA ================== #
def load_data():
    log_info(f"Reading dataset from {DATAFRAME_PATH}...\r", end="")
    try:
        cleaned_data = pd.read_csv(os.path.join(os.path.dirname(__file__), DATAFRAME_PATH))
        log_success(f"Dataset read successfully (shape: {cleaned_data.shape})")
        return cleaned_data
    except Exception as e:
        log_error("Failed to read dataset")
        raise e

def preprocess_row(row):
    return {
        'accident_id': row.get('Accident ID'),
        'event_type': row.get('Event Type'),
        'industry_type': row.get('Industry Type'),
        'accident_title': row.get('Accident Title'),
        'start_date': row.get('Start Date'),
        'finish_date': row.get('Finish Date'),
        'accident_description': row.get('Accident Description'),
        'causes_of_accident': row.get('Causes of the accident'),
        'consequences': row.get('Consequences'),
        'emergency_response': row.get('Emergency response'),
        'lesson_learned': unescape(row.get('Lesson Learned')),
        'url': row.get('url'),
    }

def load_embeddings_model(model_name, cache_folder, **model_kwargs):
    log_info("Loading embeddings model...\r", end="")
    return HuggingFaceEmbeddings(
        model_name=model_name, cache_folder=cache_folder, **model_kwargs
    )

# ================== MONGODB ================== #
def connect_mongodb(uri):
    log_info("Connecting to MongoDB...\r", end="")
    try:
        client = MongoClient(uri)
        log_success("Connected to MongoDB successfully")
        return client
    except Exception as e:
        log_error("Failed to connect to MongoDB")
        raise e

def clear_mongodb(client, database_name, collection_name):
    log_info("Clearing MongoDB collection...\r", end="")
    try:
        client[database_name].drop_collection(collection_name)
        log_success("MongoDB collection cleared successfully")
    except Exception as e:
        log_error("Failed to clear MongoDB collection")
        raise e

def insert_mongodb(client, database_name, collection_name, docs):
    log_info("Inserting documents into MongoDB...\r", end="")
    try:
        db = client[database_name]
        collection = db[collection_name]
        inserted_count = 0
        for idx, doc in enumerate(docs):
            log_info(f"Inserting document {idx + 1}/{len(docs)}...\r", end="")
            if not collection.find_one({"accident_id": doc["accident_id"]}):
                collection.insert_one(doc)
                inserted_count += 1
        log_success(f"Inserted {inserted_count} documents into MongoDB")
    except Exception as e:
        log_error("Failed to insert documents into MongoDB")
        raise e

# ================== WEAVIATE ================== #
def connect_weaviate(http_host, http_port, http_secure, grpc_host, grpc_port, grpc_secure):
    log_info("Connecting to Weaviate...\r", end="")
    try:
        client = weaviate.connect_to_custom(
            http_host=http_host,
            http_port=http_port,
            http_secure=http_secure,
            grpc_host=grpc_host,
            grpc_port=grpc_port,
            grpc_secure=grpc_secure

        )
        log_success("Connected to Weaviate successfully")
        return client
    except Exception as e:
        log_error("Failed to connect to Weaviate")
        raise e

def clear_weaviate(client: weaviate.Client, class_name: str):
    log_info("Clearing Weaviate collection...\r", end="")
    try:
        client.collections.delete(class_name)
        log_success("Weaviate collection cleared successfully")
    except Exception as e:
        log_error("Failed to clear Weaviate collection")
        raise e

def insert_weaviate(client: weaviate.Client, class_name: str, embeddings, docs: dict):
    try:
        for idx, (key, doc) in enumerate(docs.items()):
            log_info(f"Inserting document {idx + 1}/{len(docs)}...\r", end="")
            WeaviateVectorStore.from_documents([doc], embeddings, ids=[key], client=client, index_name=class_name)
        log_success("All documents inserted into Weaviate successfully")
    except Exception as e:
        log_error("Failed to insert documents into Weaviate")
        raise e

def exist_weaviate(client: weaviate.Client, class_name: str, doc_id: str):
    collection = client.collections.get(class_name)
    return collection.data.exists(doc_id)


# ================== MAIN PROCESS ================== #
def process(clear=False):
    log_info("Starting data processing...\r", end="")
    data = load_data()
    mongo_data = [preprocess_row(row) for row in data.to_dict(orient="records")]
    weaviate_data = {
        uuid.uuid5(uuid.NAMESPACE_DNS, str(doc["accident_id"])): Document(
            page_content=doc["accident_title"] + "\n" + doc["accident_description"],
            metadata={
                "incident_id": doc["accident_id"],
                "industry": doc["industry_type"],
                "event": doc["event_type"],
                "source": doc["url"]
            }
        )
        for doc in mongo_data
    }

    client_mongo = connect_mongodb(MONGO_URI)
    client_weaviate = connect_weaviate(HTTP_HOST, HTTP_PORT, HTTP_SECURE, GRPC_HOST, GRPC_PORT, GRPC_SECURE)

    if clear:
        clear_mongodb(client_mongo, DATABASE_NAME, COLLECTION_NAME)
        clear_weaviate(client_weaviate, "incident")

    log_info("Checking for new documents...\r", end="")
    if new_mongo_data := [
        doc
        for doc in mongo_data
        if not client_mongo[DATABASE_NAME][COLLECTION_NAME].find_one(
            {"accident_id": doc["accident_id"]}
        )
    ]:
        log_info(f"Inserting {len(new_mongo_data)} new documents into MongoDB...\r", end="")
        insert_mongodb(client_mongo, DATABASE_NAME, COLLECTION_NAME, new_mongo_data)
    else:
        log_success("All documents already exist in MongoDB")


    log_info("Checking for new documents...\r", end="")
    import concurrent.futures

    def check_new_documents_weaviate(client_weaviate, weaviate_data):
        new_weaviate_data = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_doc = {
                executor.submit(exist_weaviate, client_weaviate, "incident", str(key)): (key, doc)
                for key, doc in weaviate_data.items()
            }
            for future in concurrent.futures.as_completed(future_to_doc):
                key, doc = future_to_doc[future]
                if not future.result():
                    new_weaviate_data[key] = doc
        return new_weaviate_data

    new_weaviate_data = check_new_documents_weaviate(client_weaviate, weaviate_data)
    if new_weaviate_data:
        insert_weaviate(client_weaviate, "incident", load_embeddings_model(EMBEDDINGS_MODEL, EMBEDDINGS_PATH), new_weaviate_data)
    else:
        log_success("All documents already exist in Weaviate")
    log_success("Data processing completed successfully")

# ================== EXECUTION ================== #
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and insert data into MongoDB and Weaviate")
    parser.add_argument("-c", "--clear", action="store_true", help="Clear existing data before inserting new data")
    args = parser.parse_args()
    
    process(clear=args.clear)
