from pymongo import MongoClient

# Credentials to connect to the MongoDB Database
MONGO_URI = "mongodb://root:root@localhost:27017/"
DATABASE_NAME = "incident_db"
COLLECTION_NAME = "incident_collection"

def get_industries():
    """
    Retrieves a list of unique industry types from the MongoDB collection.
    
    Connects to the MongoDB server, accesses the specified database and collection,
    and retrieves all distinct values of the 'industry_type' field.
    
    Returns:
        list: A list of distinct industry types retrieved from the 'industry_type' field in the collection.
        If an error occurs, returns an empty list.
    """
    try:
        # Establish a connection to the MongoDB server.
        client = MongoClient(MONGO_URI)
        # Access the specific database within MongoDB.
        db = client[DATABASE_NAME]
        # Access the specific collection within the database.
        collection = db[COLLECTION_NAME]

        # Retrieve all unique values for the 'industry_type' field.
        industries = collection.distinct('industry_type')
        return industries
    except Exception as e:
        # Handle any exceptions that occur during the database query.
        print(f"Erreur lors de la récupération des industries : {e}")
        return []
    finally:
        # Ensure that the MongoDB client is closed after the operation.
        client.close()
