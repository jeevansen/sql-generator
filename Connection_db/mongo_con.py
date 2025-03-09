from pymongo import MongoClient
from django.conf import settings

class MongoDBConnection:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        if not self.client:
            try:
                self.client = MongoClient(settings.MONGO_CLIENT)
                self.db = self.client[settings.MONGODB_NAME]
                print("✅ Connected to MongoDB")
            except Exception as e:
                print(f"Connection error: {e}")
                raise e

    def execute_query(self, collection_name, query):
        if not self.client:
            self.connect()
        
        try:
            collection = self.db[collection_name]
            return collection.find(query)
        except Exception as e:
            print(f"Query execution error: {e}")
            raise e

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            print("🔒 MongoDB connection closed")
