from pymongo import MongoClient
from datetime import datetime
from langchain_weaviate.vectorstores import WeaviateVectorStore
from weaviate.classes.query import Filter
from langchain.retrievers import ContextualCompressionRetriever
from langchain_huggingface.embeddings import HuggingFaceEmbeddings 
import weaviate
import json
from .reranker import CustomReranker

# MongoDB connection settings
MONGO_URI = "mongodb://root:root@localhost:27017/"
DATABASE_NAME = "incident_db"
COLLECTION_NAME = "incident_collection"

# Weaviate connection settings
http_host = "localhost"
http_port = 8081
http_secure = False
grpc_host = "localhost"
grpc_port = 50051
grpc_secure = False

# Weaviate client setup
weaviate_client = weaviate.connect_to_custom(http_host, http_port, http_secure, grpc_host, grpc_port, grpc_secure)

# HuggingFace embeddings setup for generating vector representations of text
embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2", cache_folder="./embedding_model")

# Function to extract incident IDs from the retrieved documents
def get_documents_ids(retrieved_docs):
    if retrieved_docs:
        # Extract and return incident IDs from the metadata of retrieved documents
        return [int(doc.metadata['incident_id']) for doc in retrieved_docs]
    else:
        return None

# Function to retrieve documents from MongoDB based on a list of IDs
def get_documents_by_ids(ids):
    try:
        # Establish MongoDB connection
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]        
        # Fetch documents with matching 'accident_id' from the collection
        documents = list(collection.find({"accident_id": {"$in": ids}}))
        return documents
    except Exception as e:
        # Return an empty list in case of any error
        return []
    finally:
        client.close()  # Ensure the client is closed after the operation

# Custom JSON encoder to handle datetime objects when encoding to JSON
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Main function to retrieve and process documents based on the input data
def retrieve(data):
    industries = data['industries']
    query = data['question']
    retriever = create_retriever(industries)
     # Retrieve documents based on the query
    docs = retriever.invoke(query)
    ids = get_documents_ids(docs)
     # Fetch the actual documents from the database
    retrieved_docs = get_documents_by_ids(ids)
    for document in retrieved_docs:
        document.pop("_id", None) 
    # Convert the retrieved documents to JSON format and store it in the data dictionary
    data['context'] = "\n\n".join(json.dumps(document, cls=CustomJSONEncoder) for document in retrieved_docs)
    data.pop("industries")
    return data

# Function to create a retriever for semantic search based on the industries
def create_retriever(industries):
    # Use a custom re-ranker to adjust the relevance of the documents
    compressor = CustomReranker()
    filters = None 
    # If industries is not 'all', apply filters to the search query based on industries
    if not industries == 'all':
        filters = Filter.any_of([Filter.by_property("industry").equal(industry) for industry in industries])
    # Create a Weaviate vector store for indexing and retrieving incident data
    db = WeaviateVectorStore(client=weaviate_client, index_name="incident", text_key="text", embedding=embeddings)
    # Set up the contextual compression retriever, combining the base retriever with a compression model
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=db.as_retriever(search_type="mmr", search_kwargs={"fetch_k": 20, 'filters': filters})
    )
    return compression_retriever
