# import os
# from pymongo import MongoClient
# from dotenv import load_dotenv
# from pymongo.errors import BulkWriteError

# load_dotenv()

# class MongoDB:
#     def __init__(self):
#         self.client = MongoClient(os.getenv("MONGO_URI"))
#         self.db = self.client[os.getenv("DB_NAME")]

#     def insert_many(self, collection, documents):
#         if not documents:
#             return
#         try:
#             self.db[collection].insert_many(documents, ordered=False)
#         except BulkWriteError:
#              pass  # ignore duplicate key errors

import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import BulkWriteError

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client[os.getenv("DB_NAME")]

    def insert_many(self, collection, documents):
        if not documents:
            return
        try:
            self.db[collection].insert_many(documents, ordered=False)
        except BulkWriteError:
             pass  # ignore duplicate key errors
    
    def find_last_n_minutes(self, collection_name, minutes=30):
        """
        Find documents from the last N minutes in a collection
        """
        collection = self.db[collection_name]
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        return collection.find({
            "timestamp": {"$gte": cutoff_time}
        })
    
    # Optional: Add more helper methods
    def insert_one(self, collection, document):
        """Insert a single document"""
        return self.db[collection].insert_one(document)
    
    def find(self, collection, query=None):
        """Find documents in a collection"""
        if query is None:
            query = {}
        return self.db[collection].find(query)
    
    def find_one(self, collection, query=None):
        """Find one document in a collection"""
        if query is None:
            query = {}
        return self.db[collection].find_one(query)
