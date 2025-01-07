from pymongo import MongoClient
from datetime import datetime
from langchain_weaviate.vectorstores import WeaviateVectorStore
from weaviate.classes.query import Filter
from utils.reranker import CustomReranker
from langchain.retrievers import ContextualCompressionRetriever
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import weaviate
import json


MONGO_URI = "mongodb://root:root@localhost:27017/"
DATABASE_NAME = "incident_db"
COLLECTION_NAME = "incident_collection"

http_host = "localhost"
http_port = 8081
http_secure = False
grpc_host = "localhost"
grpc_port = 50051
grpc_secure = False

weaviate_client = weaviate.connect_to_custom(http_host, http_port, http_secure, grpc_host, grpc_port, grpc_secure)
embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2", cache_folder="./embedding_model")

def get_documents_ids(retrieved_docs):
    if retrieved_docs:
        return [int(doc.metadata['incident_id']) for doc in retrieved_docs]
    else:
        return None

def get_documents_by_ids(ids):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]        
        documents = list(collection.find({"accident_id": {"$in": ids}}))
        return documents
    except Exception as e:
        return []
    finally:
        client.close()

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def retrieve(data):
    industries = data['industries']
    query = data['question']
    retriever = create_retriever(industries)
    docs = retriever.invoke(query)
    ids = get_documents_ids(docs)
    retrieved_docs = get_documents_by_ids(ids)
    for document in retrieved_docs:
        document.pop("_id", None)
    data['context'] = "\n\n".join(json.dumps(document, cls=CustomJSONEncoder) for document in retrieved_docs)
    data.pop("industries")
    return data

def create_retriever(industries):
    compressor = CustomReranker()
    filters = None
    if not industries == 'all':
        filters = Filter.any_of([Filter.by_property("industry").equal(industry) for industry in industries])
    db = WeaviateVectorStore(client=weaviate_client, index_name="incident", text_key="text", embedding=embeddings)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor = compressor,
        base_retriever = db.as_retriever(search_type="mmr", search_kwargs={"fetch_k": 20, 'filters': filters})
    )
    return compression_retriever