# connect to MongoDB
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def connectMongo():
    # variables come from .env file
    mongoHost = os.getenv('MONGO_HOST', default='localhost')
    mongoPort = os.getenv('MONGO_PORT', default='27017')
    mongoUser = os.getenv('MONGO_USER')
    mongoPass = os.getenv('MONGO_PWD')
    mongoAuthSrc = os.getenv('MONGO_AUTH_SRC', default='admin')
    mongoDb = os.getenv('MONGO_DB', default='oeb-research-software')
    discovCollection = os.getenv('DISCOV_COLLECTION', default='tools_discoverer_w_index')
    resultsCollection = os.getenv('RESULTS_COLLECTION', default='tools_discoverer_results')

    # Connect to MongoDB
    mongoClient = MongoClient(
        host=mongoHost,
        port=int(mongoPort),
        username=mongoUser,
        password=mongoPass,
        authSource=mongoAuthSrc,
    )
    db = mongoClient[mongoDb]
    discovCollection = db[discovCollection]
    resultsCollection = db[resultsCollection]

    return discovCollection, resultsCollection
