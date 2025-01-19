import os
import pandas as pd
# import mysql.connector
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
from pymongo import MongoClient
from html import unescape
import weaviate.client_base
from werkzeug.security import generate_password_hash
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import warnings
warnings.filterwarnings("ignore")

WORKING_DIR = os.path.dirname(__file__)
os.chdir(WORKING_DIR)


DATABASE_NAME = "incident_db"
COLLECTION_NAME = "incident_collection"


# Data details
DATAFRAME_PATH = "data/cleaned.csv"

# Embeddings model details
EMBEDDINGS_MODEL = "intfloat/e5-large-v2"
EMBEDDINGS_PATH = "embedding_model"

# Weaviate connection details
HTTP_HOST = "localhost"
HTTP_PORT = 8081
HTTP_SECURE = False
GRPC_HOST = "localhost"
GRPC_PORT = 50051
GRPC_SECURE = False

# Mongo connection details
MONGO_URI = "mongodb://root:root@localhost:27017/"


def load_data():
    print("Reading dataset from", DATAFRAME_PATH, end="\r")
    try:
        cleaned_data = pd.read_csv(os.path.join(os.path.dirname(__file__), DATAFRAME_PATH))
    except Exception as e:
        print("Failed to read dataset")
        raise e
    
    txt = f"Dataset read successfully (shape: {cleaned_data.shape})"
    print(txt + "." * (80 - len(txt)) + '\x1b[6;30;42m' + "Done" + '\x1b[0m')
    return cleaned_data

def create_weaviate_docs(df: pd.DataFrame):
    print("Creating Weaviate Documents...", end="\r")
    try:
        weaviate_docs = []
        for row in df.iterrows():
            data = row[1]
            weaviate_docs.append(
                Document(
                    page_content=data['Accident Title'] + "\n" + data['Accident Description'],
                    metadata={
                        "incident_id": data["Accident ID"],
                        "industry": data["Industry Type"],
                        "event": data["Event Type"],
                        'source': data['url']
                    }
                )
            )
    except Exception as e:
        print("Failed to create Weaviate Documents")
        raise e
    
    txt = f"Weaviate Documents created successfully ({len(weaviate_docs)} documents)"
    print(txt + "." * (80 - len(txt)) + '\x1b[6;30;42m' + "Done" + '\x1b[0m')
    return weaviate_docs

def convert_to_weaviate_vector_store(
        client: weaviate.WeaviateClient,
        embeddings_model: str,
        embeddings_path: str,
        docs: list,
        index_name: str): 
    print("Converting Weaviate Documents to Vector Store...", end="\r")
    embeddings = HuggingFaceEmbeddings(
        model_name=embeddings_model,
        cache_folder=embeddings_path,
        model_kwargs={"device": "cpu"}
    )
    try:
        vector_store = WeaviateVectorStore(
            client=client,
            embedding=embeddings,
            index_name=index_name,
            text_key="page_content",
        )
        for i, doc in enumerate(docs):
            vector_store.aadd_documents([doc])
            print(f"Added document {i + 1}/{len(docs)}", end="\r")
    except Exception as e:
        print("Failed to convert Weaviate Documents to Vector Store")
        raise e
    
    txt = f"Weaviate Documents converted to Vector Store successfully ({len(docs)} documents)"
    print(txt + "." * (80 - len(txt)) + '\x1b[6;30;42m' + "Done" + '\x1b[0m')
    return vector_store

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

def connect_mongodb(uri):
    print("Connecting to MongoDB...", end="\r")
    try:
        client = MongoClient(uri)
    except Exception as e:
        print("\x1b[1;31;40m" + "Failed to connect to MongoDB" + '\x1b[0m')
        raise e
    
    txt = "Connected to MongoDB successfully"
    print(txt + "." * (80 - len(txt)) + '\x1b[6;30;42m' + "Done" + '\x1b[0m')
    return client

def insert_mongodb(client, database_name, collection_name, docs):
    print("Inserting documents into MongoDB...", end="\r")
    try:
        db = client[DATABASE_NAME]
        if COLLECTION_NAME in db.list_collection_names():
            txt = f"Collection '{COLLECTION_NAME}' already exists. Exiting."
            print(txt + "." * (80 - len(txt)) + '\x1b[6;30;42m' + "Done" + '\x1b[0m')
            return
        collection = db[COLLECTION_NAME]
        result = collection.insert_many(docs)
        txt = f"Multiple documents inserted (count: {len(result.inserted_ids)})"
        print(txt + "." * (80 - len(txt)) + '\x1b[6;30;42m' + "Done" + '\x1b[0m')
    except Exception as e:
        print("\x1b[1;31;40m" + "Failed to connect to database" + '\x1b[0m')
        raise e
    finally:
        client.close()
        
        
if __name__ == "__main__":
    # Load and preprocess data
    cleaned_data = load_data()
    docs = create_weaviate_docs(cleaned_data)
    
    weaviate_client = weaviate.connect_to_custom(
        http_host=HTTP_HOST,
        http_port=HTTP_PORT,
        http_secure=HTTP_SECURE,
        grpc_host=GRPC_HOST,
        grpc_port=GRPC_PORT,
        grpc_secure=GRPC_SECURE
    )

    vector_store = convert_to_weaviate_vector_store(
        client=weaviate_client,
        embeddings_model=EMBEDDINGS_MODEL,
        embeddings_path=os.path.join(os.path.dirname(__file__), EMBEDDINGS_PATH),
        docs=docs,
        index_name="incident_index"
    )
    
    # Connect to MongoDB
    client = connect_mongodb(MONGO_URI)
    
    # Create and populate Mongo Database
    mongo_docs = [preprocess_row(row[1]) for row in cleaned_data.iterrows()]
    insert_mongodb(client, DATABASE_NAME, COLLECTION_NAME, mongo_docs)
    
    client.close()
    exit()
