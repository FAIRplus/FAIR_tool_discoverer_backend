import configparser
from pymongo import MongoClient
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import csv
import bibtexparser
import json

parser = bibtexparser.bparser.BibTexParser(common_strings=True)


config = configparser.ConfigParser()
config.read('config.ini')
DBHOST = config['MONGO_DETAILS']['DBHOST']
DBPORT = config['MONGO_DETAILS']['DBPORT']
DATABASE = config['MONGO_DETAILS']['DATABASE']
COLLECTION = config['MONGO_DETAILS']['COLLECTION']
DISCOV_COLLECTION = config['MONGO_DETAILS']['DISCOV_COLLECTION']


connection = MongoClient(DBHOST, int(DBPORT))
collection = connection[DATABASE][COLLECTION]
tools_discov_collection = connection[DATABASE][DISCOV_COLLECTION]

edam_df = pd.read_csv('EDAM_1.25.csv')
edam_dict = dict(zip(edam_df['Class ID'], edam_df['Preferred Label']))

with open('fairplus_tools.csv','r') as annot:
    """
    Adds curation annotation to tools
    """
    csvreader = csv.reader(annot)
    curated_tools = []
    for row in csvreader:
        d = {'tool':row[0], 'category':row[1]}
        curated_tools.append(d)

def match_edam_label(uri):
    # following id changed in last version
    if uri == 'http://edamontology.org/topic_3557':
        uri = 'http://edamontology.org/operation_3557'

    return(edam_dict[uri])

def clean_text(text):
    # split into words
    tokens = word_tokenize(text)
    # convert to lower case
    tokens = [w.lower() for w in tokens]
    # remove punctuation from each word
    import string
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    # remove remaining tokens that are not alphabetic
    words = [word for word in stripped if word.isalpha()]
    # filter out stop words
    stop_words = set(stopwords.words('english'))
    n2grams = [f"{ngram[0]} {ngram[1]}" for ngram in nltk.ngrams(words,2)]
    n3grams = [f"{ngram[0]} {ngram[1]} {ngram[2]}" for ngram in nltk.ngrams(words,3)]
    words = [w for w in words if not w in stop_words]
    return(words, n2grams, n3grams)

def remove_dupe_dicts(l):
  list_of_strings = [
    json.dumps(d, sort_keys=True)
    for d in l
  ]
  list_of_strings = set(list_of_strings)
  return [
    json.loads(s)
    for s in list_of_strings
  ]

def extract_citations(tool):
        #print('Extracting citations ...')
        ids = {}
        ids_tuples = []
        other_titles = []
        citations = []
        final_cits = []
        final_citations = []
        other_citations = []
        pubs_titles = []
        if tool['publication']:
            publications =remove_dupe_dicts(tool['publication'])
            for pub in publications:
                new_entry = pub
                new_trace = {'x':[], 'y':[]}
                if 'citations' in pub.keys():
                    for item in pub['citations']:
                        new_trace['x'].append(item['year'])
                        new_trace['y'].append(item['count'])
                    new_entry['trace'] = new_trace
                
                citations.append(new_entry)

                new_tuple = set()
                seen = False
                for ID in ['doi', 'pmcid', 'pmid']:
                    if pub.get(ID) != None:
                        new_tuple.add(pub.get(ID))

                if new_tuple:
                    ids_tuples.append(new_tuple)
                else:
                    if new_entry.get('title') not in [p.get('title') for p in citations]:
                        other_titles.append(new_entry)

            print(f'Ids tuples: {ids_tuples}')
            if ids_tuples:
                clean_tuples = []
                for tup in ids_tuples:
                    same = [list(tup)]
                    for other_tup in ids_tuples:
                        inter = [x for x in other_tup if x in tup]
                        if inter != [] and other_tup != tup:
                            same.append(list(other_tup))
                            ids_tuples.remove(other_tup)
                    ids_tuples.remove(tup)
                    clean_tuples.append(max(same,key=len))
                
                print(f'Clean tuples: {clean_tuples}')
                
                ids_dict = {}
                tuples_map = []
                N = 0
                for t in clean_tuples:
                    ids_dict[N] = []
                    tuples_map.append([N, t])
                    N += 1
                
                print(tuples_map)
                print(f'Ids dict: {ids_dict}')

                print(f'Citations: {citations}')
                for pub_ in citations:
                    flag = False
                    for ID in ['doi', 'pmcid', 'pmid']:
                        print(f'Ids dict: {ids_dict}')
                        if pub_.get(ID) != None:
                            if flag == False:
                                for item in tuples_map:
                                    if pub_.get(ID) in item[1]:
                                        pub_N = item[0]
                                        ids_dict[pub_N].append(pub_)
                                        print('hey')
                                        flag = True

                print(f'Ids dict: {ids_dict}')
                final_citations = [] 
                for unique_pub in ids_dict.keys():
                    max_complete_pub = max(ids_dict[unique_pub], key=len)
                    final_citations.append(max_complete_pub)
            else:
                final_citations = other_titles
                                                
            print(f'Final citations: {final_citations}')

            titles_final = {}
            final_cits = []
            for citation in final_citations:
                if citation.get('title') not in titles_final.keys():
                    titles_final[str(citation.get('title'))] = [citation]
                else:
                    titles_final[str(citation.get('title'))].append(citation)

            for tit in titles_final.keys():
                final_cits.append(max(titles_final[tit], key=len))
                
          

            for citation in final_cits:
                try:
                    if 'title' in citation.keys():
                        if citation['title']:
                            pubs_titles.append(citation['title'])
                except Exception as er:
                    print(tool['@id'])
                    print(tool['publication'])
                    raise

        return(final_cits, other_citations, pubs_titles)


def extract_citations_old(tool):
        #print('Extracting citations ...')
        ids = set()
        citations = []
        citations_other = []
        pubs_titles = []
        if tool['publication']:
            for pub in tool['publication']:
                new_trace = {'x':[], 'y':[]}
                remain_pubs=[]
                if type(pub) == dict:
                    if 'entries' in pub.keys():
                        for entry in pub['entries']:
                            new_entry=entry
                            if 'citations' in entry.keys():
                                if True not in [entry.get(ID) in ids for ID in ['doi', 'pmcid', 'pmid']]:
                                    for item in entry['citations']:
                                        new_trace['x'].append(item['year'])
                                        new_trace['y'].append(item['count'])
                                        [ids.add(entry.get(ID)) for ID in ['doi', 'pmcid', 'pmid'] if entry.get(ID) != None]
                                    new_entry['trace'] = new_trace
                                    citations.append(new_entry)
                            else:
                                citations.append(new_entry)
                    else:
                        remain_pubs.append(pub)

                if type(pub) == list:
                    for entry in pub:
                        if entry.get('type') == 'bibtex':
                            try:
                                bibtexdb = bibtexparser.loads(entry.get('citation'), parser=parser)
                                for entry in bibtexdb.entries:
                                    if entry['ENTRYTYPE'].lower() != 'misc':
                                        single_entry = {}
                                        single_entry['url'] = entry.get('url')
                                        single_entry['title'] = entry.get('title')
                                        single_entry['year'] = entry.get('year')
                                        citations_other.append(single_entry)
                            except Exception as err:
                                print(err)
                                print(entry)


            for pub in remain_pubs:
                if type(pub) == dict:
                    if 'entries' not in pub.keys():
                        if pub == {'url':None, 'title':''}:
                            break
                        if True not in [pub.get(ID) in ids for ID in ['doi', 'pmcid', 'pmid','url', 'citation']]:
                            new_entry = {}
                            if 'doi' in pub.keys():
                                new_entry['doi'] = pub['doi']
                            if 'pmcid' in pub.keys():
                                new_entry['pmcid'] = pub['pmcid']
                            if 'pmid' in pub.keys():
                                new_entry['pmid'] = pub['pmid']
                            if 'citation' in pub.keys():
                                if 'error occured' not in pub['citation']:
                                    new_entry['title'] = pub['citation']
                                else:
                                   break

                            [ids.add(pub.get(ID)) for ID in ['doi', 'pmcid', 'pmid', 'url', 'citation'] if pub.get(ID) != None]
                            citations_other.append(new_entry)
        for citation in citations:
            if 'title' in citation.keys():
                if citation['title']:
                    pubs_titles.append(citation['title'])
        return(citations, citations_other, pubs_titles)


def aggregate_sources_labels(tool):
        #print('Aggregating sources labels ...')
        labels = set()
        if 'biotools' in tool['source']:
            labels.add('biotools')
        if 'bioconductor' in tool['source']:
            labels.add('bioconductor')
        if 'github' in tool['source']:
            labels.add('github')
        if 'galaxy' in tool['source'] or 'toolshed' in tool['source']:
            labels.add('galaxy')
        if 'bioconda' in tool['source']:
            labels.add('bioconda')
        if 'bioconda_conda' in tool['source'] or 'bioconda_recipes' in tool['source']:
            labels.add('bioconda')
        if 'sourceforge' in tool['source']:
            labels.add('sourceforge')
        if 'bitbucket' in tool['source']:
            labels.add('bitbucket')
       
        labels_links = {label:'' for label in labels}
        valid = {'github':['github'],
                'biotools':['bio.tools'],
                'bitbucket':['bitbucket'],
                'sourceforge':['sourceforge'],
                'galaxy':['galaxy','toolshed'],
                'bioconda':['bioconda'],
                'bioconductor':['bioconductor']}
        if tool['links']:
            hit = False
            for label in labels:
                labels_links[label] = ''
                for link in tool['links']:
                    for valid_label in valid[label]:
                        if valid_label in link:
                            labels_links[label] = link
                            hit =True
                            break
            if hit == False:
                labels_links['other'] = tool['links'][0]

        if 'biotools' in labels:
            link = f"https://bio.tools/{tool['name']}"
            labels_links['biotools'] = link
            
        return(labels_links)

def searchable_data_prep():
    for tool in collection.find():
        discoverer_tool = tool
        discoverer_tool['description_words'] = []
        discoverer_tool['description_n2gram'] = []
        discoverer_tool['description_n3gram'] = []
        if tool['description']:
            for description in tool['description']:
                words, n2grams, n3grams = clean_text(description)
                words = list(set(words))
                n2grams = list(set(n2grams))
                n3grams = list(set(n3grams))
                for w in words:                                                             
                    discoverer_tool['description_words'].append(w)
                for ng in n2grams:
                    discoverer_tool['description_n2gram'].append(ng)
                for n3g in n3grams:
                    discoverer_tool['description_n3gram'].append(n3g)
        
        discoverer_tool['edam'] = []
        edam_topics = []
        edam_operations = []
        if tool['semantics']: #only entries from bio.tools have this field    
            if tool['semantics']['topics']:
                [edam_topics.append({'uri':item, 'label':match_edam_label(item)}) for item in tool['semantics']['topics']]
                [discoverer_tool['edam'].append(item) for item in tool['semantics']['topics']]
            discoverer_tool['edam_topics'] = edam_topics

            if tool['semantics']['operations']:
                [edam_operations.append({'uri':item, 'label':match_edam_label(item)}) for item in tool['semantics']['operations']]
                [discoverer_tool['edam'].append(item) for item in tool['semantics']['operations']]
            discoverer_tool['edam_operations'] = edam_operations

        for data_inout in ['input','output']:
            if tool.get(data_inout):

                tool[f"{data_inout}_formats"] = set()
                tool[f"{data_inout}_format_labels"] = []

                for input in tool.get(data_inout):
                    if input.get('formats'):
                        for f in input.get('formats'):
                            tool[f"{data_inout}_formats"].add(match_edam_label(f))
                            tool[f"{data_inout}_format_labels"].append({
                                'uri':f,
                                'label':match_edam_label(f)
                            })

                    if input.get('format'):
                        if input['format'].get('term'):
                            tool[f"{data_inout}_formats"].add(input['format'].get('term'))
                            if input['format'].get('uri'):
                                uri = input['format'].get('uri')
                            else:
                                uri = ''
                            tool[f"{data_inout}_format_labels"].append({
                                'uri':uri,
                                'label':input['format'].get('term')
                            })

                tool[f"{data_inout}_formats"] = list(tool[f"{data_inout}_formats"])


        discoverer_tool['curation'] = curated(tool)
        discoverer_tool['citations'], discoverer_tool['citations_other'], discoverer_tool['pubs_titles'] = extract_citations(tool)
        discoverer_tool['sources_labels'] = aggregate_sources_labels(tool)
        tools_discov_collection.update_one({'@id':discoverer_tool['@id']}, { '$set': discoverer_tool }, upsert=True)
        #tools_discov_collection.insert_one(discoverer_tool)

def index():
    tools_discov_collection.create_index('edam_operations')
    tools_discov_collection.create_index('edam_topics')
    tools_discov_collection.create_index([('description','text'), ('pubs_titles','text')])


def curated(tool):
    curated =[]
    for tool_entry in curated_tools:
        if tool['name'] == tool_entry['tool'].lower():
            curated.append(tool_entry['category'])
    return(curated)
    
   

if __name__ == "__main__":
    # Preapare
    searchable_data_prep()
    # Then build inverted indexes in Mongo
    index()
