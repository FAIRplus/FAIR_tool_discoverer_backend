import configparser
from pymongo import MongoClient

config = configparser.ConfigParser()
config.read('config.ini')
DBHOST = config['MONGO_DETAILS']['DBHOST']
DBPORT = config['MONGO_DETAILS']['DBPORT']
DATABASE = config['MONGO_DETAILS']['DATABASE']
COLLECTION = config['MONGO_DETAILS']['COLLECTION']

def connect_mongo():
    connection = MongoClient(DBHOST, int(DBPORT))
    collection = connection[DATABASE][COLLECTION]
    return(collection)

def retrieve_descriptions(n):
    collection = connect_mongo()
    descriptions = []
    i=0
    for document in collection.find():
        if i<n:
            i += 1
            for description in document['description']:
                descriptions.append(description)
        else:
            break
    return(descriptions)

descs = retrieve_descriptions(50)
print(descs)           

# Optimizing the inference graph
# from https://towardsdatascience.com/building-a-search-engine-with-bert-and-tensorflow-c6fdc0186c8a
# Using bert-as-a-service to confgure the inference graph using a CLI interface

import os
import tensorflow as tf

from bert_serving.server.graph import optimize_graph
from bert_serving.server.helper import get_args_parser

from bert.tokenization import FullTokenizer

MODEL_DIR = './wwm_uncased_L-24_H-1024_A-16/' #@param {type:"string"}
GRAPH_DIR = './graph' #@param {type:"string"}
GRAPH_OUT = 'extractor.pbtxt' #@param {type:"string"}
GPU_MFRAC = 0.2 #@param {type:"string"}

POOL_STRAT = 'REDUCE_MEAN' #@param {type:"string"}
POOL_LAYER = "-2" #@param {type:"string"}
SEQ_LEN = "64" #@param {type:"string"}

tf.io.gfile.makedirs(GRAPH_DIR)

parser = get_args_parser()
carg = parser.parse_args(args=['-model_dir', MODEL_DIR,
                               "-graph_tmp_dir", GRAPH_DIR,
                               '-max_seq_len', str(SEQ_LEN),
                               '-pooling_layer', str(POOL_LAYER),
                               '-pooling_strategy', POOL_STRAT,
                               '-gpu_memory_fraction', str(GPU_MFRAC)])

tmpfi_name, config = optimize_graph(carg)
graph_fout = os.path.join(GRAPH_DIR, GRAPH_OUT)

tf.gfile.Rename(
    tmpfi_name,
    graph_fout,
    overwrite=True
)
print("Serialized graph to {}".format(graph_fout))

# Step 3: creating a feature extractor
INPUT_NAMES = ['input_ids', 'input_mask', 'input_type_ids']
bert_tokenizer = FullTokenizer(VOCAB_PATH)

def build_feed_dict(texts):
    
    text_features = list(convert_lst_to_features(
        texts, SEQ_LEN, SEQ_LEN, 
        bert_tokenizer, log, False, False))

    target_shape = (len(texts), -1)

    feed_dict = {}
    for iname in INPUT_NAMES:
        features_i = np.array([getattr(f, iname) for f in text_features])
        features_i = features_i.reshape(target_shape)
        features_i = features_i.astype("int32")
        feed_dict[iname] = features_i

    return feed_dict

