from pymongo import MongoClient

MONGO_URI = "mongodb://root:root@localhost:27017/"
DATABASE_NAME = "incident_db"
COLLECTION_NAME = "incident_collection"

def get_industries():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        industries = collection.distinct('industry_type')
        return industries
    except Exception as e:
        print(f"Erreur lors de la récupération des industries : {e}")
        return []
    finally:
        client.close()
        
if __name__ == "__main__":
    res = get_industries()
    print(res)
        
