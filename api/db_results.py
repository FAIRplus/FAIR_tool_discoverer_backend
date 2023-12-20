from dotenv import load_dotenv
import logging
from utils import connectMongo


load_dotenv()

def connect_mongo():
    discovCollection, collection = connectMongo()
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


