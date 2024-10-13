from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            return result.inserted_ids
        except OperationFailure as e:
            logging.error(f"An error occurred while inserting documents: {e}")
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
