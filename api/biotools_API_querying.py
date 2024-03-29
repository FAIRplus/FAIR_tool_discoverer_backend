import json
import pandas as pd
import logging

import db_retrieval
import zooma_api as za

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class tools_discoverer(object):

    def __init__(self, label, kw_w, out_path, default_unspecified_keyword_score, custom_weights):
        self.label = label
        self.custom_weights = custom_weights

        logging.info(f"Loading input files...")    

        self.terms_input = kw_w # list(dict('keyword', 'ClassId','weight'))
        logging.debug(self.terms_input)
        # keywords in:
        self.keywords_weights = []
        # zooma terms in:
        self.edam_terms = []
        # terms stored here
        self.free_terms = []
        self.terms_label = {}

        self.query_zooma()

        self.default_score = default_unspecified_keyword_score
        if self.default_score == None:
            self.default_score = 0.7
        else:
            self.default_score = 1.0

        self.out_path = out_path

        # results will be here
        self.results = []

    def run_pipeline(self):
        self.query_terms()
        logging.info('Query done')
        if self.results.empty:
            logging.info('No tools found')
            self.result_found = False
        else:
            self.rank_tools()
            logging.info('Tools ranked')
            self.result_found = True
            

    def query_zooma(self):
        '''
        keywords is a set of strings to look up in zooma
        '''
        logging.info("Looking up terms in ZOOMA")

        for term in self.terms_input:
            keyword = term['keyword']
            # If edam term, directly add to edam list
            # print(keyword)
            if term['classId']:
                self.edam_terms.append(term['classId'])
                term['weight']= term['weight'] + 1
                self.keywords_weights.append(term)

                self.keywords_weights.append({'keyword':keyword, 'classId':None, 'weight':term['weight']})
                self.free_terms.append(keyword)
            else:
                confident_matches = za.zooma_single_lookup(keyword)
                w = term['weight']
                if confident_matches:
                    logging.debug(f"Matches found in EDAM:")
                    [logging.debug(f"{match['label']} - {match['confidence']} - {match['edam_term']}") for match in confident_matches]
                    
                    for match in confident_matches:
                        term_id = match['edam_term'].strip('\n')
                        self.edam_terms.append(term_id)
                        #self.terms_label[match] = str(match['label']).strip('\n')
                        self.keywords_weights.append({'keyword':match['label'] , 'classId': term_id, 'weight':w+1})
                        
                        self.free_terms.append(keyword)
                        self.keywords_weights.append({'keyword':keyword, 'classId':None, 'weight':w})

                    self.free_terms.append(keyword)
                else:
                    self.keywords_weights.append({'keyword':keyword, 'classId':None, 'weight':w})
                    self.free_terms.append(keyword)

        self.keywords_weights = pd.DataFrame(self.keywords_weights)
        logging.info('Zooma lookup done')


    def query_terms(self):
        logging.info('edam terms: ' + str(self.edam_terms))
        logging.info('free terms: ' + str(self.free_terms))
        query = db_retrieval.query(self.edam_terms, self.free_terms)
        query.getData() # perform db search
        self.results = query.results

    def rank_tools(self):
        promp_text = 'Ranking results...'
        logging.info(f'{promp_text}')

        # sorting
        # print(self.results)
        self.results['raw_score'] = self.results.apply (lambda row: self.compute_score(row), axis=1)
        max_score = max(self.results['raw_score'])
        self.results['score'] = self.results.apply (lambda row: row['raw_score']/max_score, axis=1)
        self.results = self.results.sort_values('score', ascending=False)    
        logging.debug(self.results)

    def compute_score(self, row):
        if self.custom_weights == False:
            return(float(len([x for x in row['matches']])))
        else:
            scores = []
            [self.keywords_weights['keyword']]
            for match in list(row['matches']):

                if 'edamontology.org' in match:
                    w = self.keywords_weights.loc[self.keywords_weights['classId']==match]['weight'].values[0]
                else:
                    w = self.keywords_weights.loc[self.keywords_weights['keyword']==match]['weight'].values[0]
                
                scores.append(float(w))
            summ = sum(scores)
            return(float(summ))


    def generate_outputs(self):
        try:
            result = self.results.head(100).to_json(orient="records")
            self.json_result_parsed = json.loads(result)
            return(self.json_result_parsed)

        except Exception as err:
            logging.error(err)

        

