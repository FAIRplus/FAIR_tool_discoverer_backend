import configparser
from pymongo import MongoClient
import pandas as pd

config = configparser.ConfigParser()
config.read('config.ini')
DBHOST = config['MONGO_DETAILS']['DBHOST']
DBPORT = config['MONGO_DETAILS']['DBPORT']
DATABASE = config['MONGO_DETAILS']['DATABASE']
COLLECTION = config['MONGO_DETAILS']['DISCOV_COLLECTION']

edam_df = pd.read_csv('EDAM_1.25.csv')
edam_dict = dict(zip(edam_df['Class ID'], edam_df['Preferred Label']))

class query(object):
    def __init__(self, edam_terms, free_terms):
        self.edam_terms = edam_terms
        self.free_terms = free_terms
        self.results = pd.DataFrame(columns =['_id',
                                              '@id', 
                                              'authors',
                                              'bioschemas',
                                              'curation',
                                              'description',
                                              'documentation', 
                                              'download', 
                                              'https', 
                                              'input', 
                                              'inst_instr', 
                                              'license', 
                                              'links', 
                                              'name', 
                                              'operational', 
                                              'os', 
                                              'output',
                                              'repository', 
                                              'semantics', 
                                              'source', 
                                              'src', 
                                              'ssl', 
                                              'termsUse', 
                                              'test', 
                                              'type', 
                                              'version',
                                              'edam_topics',
                                              'edam_operations',
                                              'matches',
                                              'citations',
                                              'citations_other',
                                              'sources_labels',
                                              'input_formats',
                                              'output_formats',
                                              'input_format_labels',
                                              'output_format_labels'])
        self.results.set_index('@id')
  

    def match_edam_label(self, uri):
        print('Matching EDAM label')
        if uri == 'http://edamontology.org/topic_3557':
            uri = 'http://edamontology.org/operation_3557'
        try:
            label = edam_dict[uri]
        except:
            label = uri
        return(label)

    def match_data(self, doc, td):
        print('Data types matching ...')
        newd = []
        if td in doc.keys():
            for data in doc[td]:
                if type(data)==dict:
                    newdict = {'datatype':'', 'formats':[]}
                    if 'datatype' in data.keys():
                        newdict['datatype'] = self.match_edam_label(data['datatype'])
                    if 'formats' in data.keys():
                        for i in data['formats']:
                            newdict['formats'].append(self.match_edam_label(str(i)))
                    newd.append(newdict)
        return(newd)


    def add_to_results(self, matches, topic):
        print(f'Adding to results ...')
        for doc in matches:
            #print(f"- {doc['name']}")
            doc['_id'] = str(doc['_id'])
            if '@id' in doc.keys():
                if doc['@id'] in self.results_ids:
                    self.results.loc[doc['@id'],'matches'].append(topic)
                else:
                    doc['matches'] = [topic]
                    doc_id = doc['@id']
                    doc.pop('@id')
                    self.results.loc[doc_id] = doc
                    self.results_ids.add(doc_id)
            else:
                print('hey')

    def query_edam(self):
        for term in self.edam_terms:
            print(f'Querying EDAM term {term} ...')
            if 'operation' in term:
                matches = self.collection.find({
                    'edam_operations.uri' : term
                })

            elif 'topic' in term:
                matches = self.collection.find({
                    'edam_topics.uri' : term
                })

            else:
                matches=[]
            self.add_to_results(matches, term)

    def full_text_query(self, term):
        #print('Full text query ...')
        matches = []
        description_docs = self.collection.find({
            'description' : {'$gt' : [] }
        })
        for doc in description_docs:
            for description in doc['description']:
                if term in description.lower():
                    matches.append(doc)
                    break

        return(matches)

    def query_description(self):
        for term in self.free_terms:
            print(term)
            term = term.lower()
            l = len(term.split(' '))
            if l==1:
                matches = self.collection.find({'description_words':term})
            elif l==2:
                matches = self.collection.find({'description_n2gram':term})
            elif l==3:
                matches = self.collection.find({'description_n3gram':term})
            else:
                matches =  self.full_text_query(term)
            
            if matches:
                self.add_to_results(matches, term)
      
    
    def connect_mongo(self):
        connection = MongoClient(DBHOST, int(DBPORT))
        self.collection = connection[DATABASE][COLLECTION]

    def getData(self):
        self.connect_mongo()
        self.results_ids = set()
        self.query_edam()
        self.query_description()

'''
edam_terms = ['http://edamontology.org/topic_0797']
free_terms = ['ontology annotation', 'semantic annotation']
mquery = query(edam_terms, free_terms)
mquery.getData()
print(mquery.results)
'''