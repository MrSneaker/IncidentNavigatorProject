import pandas as pd
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
from pymongo import MongoClient
from html import unescape

MONGO_URI = "mongodb://root:root@localhost:27017/"
DATABASE_NAME = "incident_db"
COLLECTION_NAME = "incident_collection"
weaviate_client = weaviate.connect_to_local()
embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-large", cache_folder="./embedding_model")

def preprocess_row(row):
    renamed_row = {
        'accident_id': row.get('Accident ID'),
        'event_type': row.get('Event Type'),
        'industry_type': row.get('Industry Type'),
        'accident_title': row.get('Accident Title'),
        'start_date': row.get('Start Date'),
        'finish_date':row.get('Finish Date'),
        'accident_description': row.get('Accident Description'),
        'causes_of_accident': row.get('Causes of the accident'),
        'consequences': row.get('Consequences'),
        'emergency_response': row.get('Emergency response'),
        'lesson_learned': unescape(row.get('Lesson Learned'))
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

if __name__ == "__main__":
    # Load an clean the data
    raw_data = pd.read_excel("data/eMARS.xlsx")
    keep = ["Accident ID", "Event Type", "Industry Type", "Accident Title", "Start Date", "Finish Date", "Accident Description", "Causes of the accident", "Consequences", "Emergency response", "Lesson Learned"]
    keep_data = raw_data.copy()[keep]
    cleaned_data = keep_data.dropna().reset_index(drop=True)

    # Populate the Weaviate Vector Database
    weaviate_docs = []

    for row in cleaned_data.iterrows():
        data = row[1]
        weaviate_docs.append(
            Document(
                page_content = data['Accident Title'] + "\n" + data['Accident Description'],
                metadata = {
                    "incident_id": data["Accident ID"],
                    "industry": data["Industry Type"],
                    "event": data["Event Type"]
                }
            )
        )
    db = WeaviateVectorStore.from_documents(weaviate_docs, embeddings, client=weaviate_client, index_name="incident")

    # Create and populate Mongo Database
    mongo_docs = [preprocess_row(row) for row in cleaned_data.to_dict(orient="records")]
    connect_and_insert(mongo_docs)