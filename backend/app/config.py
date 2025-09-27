import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "distributor_db")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
