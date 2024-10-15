from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from bson import ObjectId
import logging
import json
from bson.json_util import dumps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class DatabaseManager:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            logging.info("Successfully connected to the database.")
        except ConnectionFailure:
            logging.error("Server not available. Failed to connect to the database.")
            raise

    def get_database(self, db_name):
        if not self.client:
            self.connect()
        self.db = self.client[db_name]
        return self.db

    def get_collection(self, db_name, collection_name):
        db = self.get_database(db_name)
        return db[collection_name]

    def insert_many(self, db_name, collection_name, documents):
        collection = self.get_collection(db_name, collection_name)
        try:
            result = collection.insert_many(documents)
            logging.info(f"Successfully inserted {len(result.inserted_ids)} documents.")
            return [str(id) for id in result.inserted_ids]  # Convert ObjectIds to strings
        except OperationFailure as e:
            logging.error(f"An error occurred while inserting documents: {e}")
            raise

    def get_listings(self, db_name, collection_name, query=None, limit=10):
        collection = self.get_collection(db_name, collection_name)
        try:
            cursor = collection.find(query or {}).limit(limit)
            return json.loads(dumps(list(cursor)))  # Convert to JSON-serializable format
        except OperationFailure as e:
            logging.error(f"An error occurred while fetching listings: {e}")
            raise

    def get_listing_by_id(self, db_name, collection_name, listing_id):
        collection = self.get_collection(db_name, collection_name)
        try:
            result = collection.find_one({"_id": ObjectId(listing_id)})
            return json.loads(dumps(result))  # Convert to JSON-serializable format
        except OperationFailure as e:
            logging.error(f"An error occurred while fetching the listing: {e}")
            raise

    def close_connection(self):
        if self.client:
            self.client.close()
            logging.info("Database connection closed.")

# Usage example
CONNECTION_STRING = "mongodb://192.168.1.71:27017/?retryWrites=true&loadBalanced=false&serverSelectionTimeoutMS=5000&connectTimeoutMS=10000"
DB_NAME = "airbnb"
COLLECTION_NAME = "listings"

db_manager = DatabaseManager(CONNECTION_STRING)

def insert_many_into_collection(places):
    try:
        db_manager.connect()
        inserted_ids = db_manager.insert_many(DB_NAME, COLLECTION_NAME, places)
        return inserted_ids
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        db_manager.close_connection()

def get_listings(db_name, collection_name, query=None, limit=10):
    try:
        db_manager.connect()
        return db_manager.get_listings(db_name, collection_name, query, limit)
    except Exception as e:
        logging.error(f"An error occurred while fetching listings: {e}")
        return []
    finally:
        db_manager.close_connection()

def get_listing_by_id(db_name, collection_name, listing_id):
    try:
        db_manager.connect()
        return db_manager.get_listing_by_id(db_name, collection_name, listing_id)
    except Exception as e:
        logging.error(f"An error occurred while fetching the listing: {e}")
        return None
    finally:
        db_manager.close_connection()