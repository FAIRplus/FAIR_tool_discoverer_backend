import configparser
from pymongo import MongoClient
import pandas as pd
import uuid

config = configparser.ConfigParser()
config.read('config.ini')
DBHOST = config['MONGO_DETAILS']['DBHOST']
DBPORT = config['MONGO_DETAILS']['DBPORT']
DATABASE = config['MONGO_DETAILS']['DATABASE']
COLLECTION = config['MONGO_DETAILS']['RESULTS_COLLECTION']

def connect_mongo():
    connection = MongoClient(DBHOST, int(DBPORT))
    collection = connection[DATABASE][COLLECTION]
    return(collection)

def query_by_id(identifier):
    collection = connect_mongo()
    result = collection.find_one({'run_id':identifier})
    if result:
        print('Result found')
    else:
        print('No result found')
    return(result)

def push(results, raw_input, result_found):
    collection = connect_mongo()
    id_ = uuid.uuid1()
    try:
        collection.insert_one({'run_id':id_.hex,'input_parameters':raw_input, 'result':results, 'result_found':result_found})
    except Exception as err:
        print('Could not insert in collection')
        raise(err)
    else:
        return(id_.hex)
