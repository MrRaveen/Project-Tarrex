import os
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


