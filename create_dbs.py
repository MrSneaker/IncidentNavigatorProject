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

MONGO_URI = "mongodb://root:root@localhost:27017/"
DATABASE_NAME = "incident_db"
COLLECTION_NAME = "incident_collection"
# weaviate_client = weaviate.connect_to_local()

http_host = "localhost"
http_port = 8081
http_secure = False
grpc_host = "localhost"
grpc_port = 50051
grpc_secure = False

weaviate_client = weaviate.connect_to_custom(http_host, http_port, http_secure, grpc_host, grpc_port, grpc_secure)

embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2", cache_folder="./embedding_model", model_kwargs={"device": "cpu"})

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "incident_nav_auth",
    "port": 3306
}

def hash_password(password):
    return generate_password_hash(password)

def setup_mysql_users():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS incident_nav_auth")
        cursor.execute("USE incident_nav_auth")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user VARCHAR(255) NOT NULL UNIQUE,
            pwd VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            industries JSON
        )
        """)  
        
        users_data = [
            ("massamba", "password", "admin", None),
            ("mateo", "password", "manager", '["processing of metal", "Wood treatment and furniture"]'),
            ("axel", "password", "manager", '["Fuel storage"]')
        ]
        
        cursor.executemany("""
        INSERT INTO users (user, pwd, role, industries)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        user = VALUES(user)
        """, users_data)
        
        connection.commit()
        print("Users table created and data inserted successfully.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()
        print("Connection closed")

def preprocess_row(row):
    renamed_row = {
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
        'url': row.get('url')
    }
    return renamed_row

def connect_and_insert(docs):
    try:
        client = MongoClient(MONGO_URI)
        print("Connected to MongoDB successfully")
        db = client[DATABASE_NAME]
        if COLLECTION_NAME in db.list_collection_names():
            print(f"Collection '{COLLECTION_NAME}' already exists. Exiting.")
            return
        collection = db[COLLECTION_NAME]
        result = collection.insert_many(docs)
        print(f"Multiple documents inserted with IDs: {result.inserted_ids}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()
        print("Connection closed")

def update_with_urls(dataframe):
    driver = webdriver.Chrome()
    urls = []
    try:
        driver.get("https://emars.jrc.ec.europa.eu/en/emars/accident/search")
        for index, row in dataframe.iterrows():
            accident_id = row['Accident ID']
            input_element = WebDriverWait(driver, 600).until(
                EC.presence_of_element_located((By.ID, "appendedInputButton"))
            )
            input_element.clear()
            input_element.send_keys(str(accident_id).zfill(6))
            button = WebDriverWait(driver, 600).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "search")]'))
            )
            button.click()
            anchor_element = WebDriverWait(driver, 600).until(
                EC.presence_of_element_located((By.XPATH, f"//a[text()='{str(accident_id).zfill(6)}']"))
            )
            href = anchor_element.get_attribute('href')
            urls.append(href)
            print(f"Row {index}, Redirect URL: {href}")
    except Exception as e:
        print(e)
    finally:
        dataframe['url'] = urls
        driver.quit()
    return dataframe


if __name__ == "__main__":
    # Set up MySQL users table and data
    # setup_mysql_users()

    # Load and clean the data
    raw_data = pd.read_excel("data/eMARS.xlsx")
    keep = ["Accident ID", "Event Type", "Industry Type", "Accident Title", "Start Date", "Finish Date", "Accident Description", "Causes of the accident", "Consequences", "Emergency response", "Lesson Learned"]
    keep_data = raw_data.copy()[keep]
    cleaned_data = keep_data.dropna().reset_index(drop=True)
    cleaned_data = update_with_urls(cleaned_data)
    cleaned_data = pd.read_csv("data/cleaned.csv")

    # Populate the Weaviate Vector Database
    weaviate_docs = []

    for row in cleaned_data.iterrows():
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
    db = WeaviateVectorStore.from_documents(weaviate_docs, embeddings, client=weaviate_client, index_name="incident")

    # Create and populate Mongo Database
    mongo_docs = [preprocess_row(row) for row in cleaned_data.to_dict(orient="records")]
    connect_and_insert(mongo_docs)
