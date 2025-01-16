import chromadb
from openai import OpenAI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os


# Create a new client and connect to the server
class client_connections:
    def __init__(self):
        self._chromadb_client = chromadb.PersistentClient(path="db/")
        self._openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._mongodb_client = MongoClient(
            os.getenv("MONGO_CONNECTION_URI"), server_api=ServerApi("1")
        )

    def get_openai_client(self):
        return self._openai_client

    def get_chromadb_client(self):
        return self._chromadb_client

    def get_mongodb_database(self):
        return self._mongodb_client["chat_assistant"]
