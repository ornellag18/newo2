import os
import urllib
from pymongo import MongoClient

def get_mongo_client():
    username = "ornellag"
    pwd = "Ornella01"
    uri = (
        f"mongodb+srv://{urllib.parse.quote_plus(username)}:" \
        f"{urllib.parse.quote_plus(pwd)}" \
        "@cluster0.9dpllap.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )
    return MongoClient(uri)

def get_mongo_collections():
    client = get_mongo_client()
    db = client["NW-db"]
    return db["workover"], db["historial_consultas"]