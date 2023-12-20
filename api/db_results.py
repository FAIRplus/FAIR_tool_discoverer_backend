import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import logging


load_dotenv()
DBHOST = os.getenv('DBHOST')
DBPORT = os.getenv('DBPORT')
DATABASE = os.getenv('DATABASE')
COLLECTION = os.getenv('RESULTS_COLLECTION')

def connect_mongo():
    connection = MongoClient(DBHOST, int(DBPORT))
    collection = connection[DATABASE][COLLECTION]
    return(collection)

def query_by_id(identifier):
    collection = connect_mongo()
    result = collection.find_one({'run_id':identifier})
    if result:
        logging.info('Result found')
    else:
        logging.warning('No result found')
    return(result)

def push(data):
    collection = connect_mongo()
    try:
        collection.insert_one(data)
        data.pop('_id')
    except Exception as err:
        logging.warning('Could not insert in collection')
        raise(err)
    else:
        logging.info('Inserted in collection') 


