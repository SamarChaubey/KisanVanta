from pymongo import MongoClient

from config import DATABASE_NAME, MONGODB_URI

client = MongoClient(MONGODB_URI)
database = client[DATABASE_NAME]
