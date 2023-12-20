from os import path
from fastapi import FastAPI, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Union

from dotenv import load_dotenv

import pandas as pd
import uuid

import biotools_API_querying as bAq
import db_results

import logging

root_logger= logging.getLogger()
root_logger.setLevel(logging.DEBUG) # or whatever
handler = logging.FileHandler('logs/api.log', 'w', 'utf-8') # or whatever
root_logger.addHandler(handler)

class unique_run(object):

    def __init__(self, request):
        self.request = request
        self.request_ID = self.generate_request_id()
        self.inputs_kw = self.parse_input()
        self.data={
            'run_id':None,
            'input_parameters':self.parse_input(),
            'tools':None,
            'result_found':None
        }

        self.parse_input()

    def generate_request_id(self):
        new_id = uuid.uuid4()
        return new_id

    def parse_input(self):
        inputs_kw = []
        weights = set()
        diff_weights_n = 0
        logging.info('Parsing input...')
        try:
            for term in self.request:
                print(term.weight)
                w=float(term.weight)
                inputs_kw.append({
                    'keyword':term.label.lower(), 
                    'classId':term.id,
                    'weight': w 
                    })
                weights.add(w)
            if len(weights)>1:
                self.diff_weights = True
            else:
                self.diff_weights = False
            
        except Exception as err:
                logging.error(err)
                raise
        else:
            logging.info(f"Input terms: {inputs_kw}")
            return(inputs_kw)

    def run_tool_discoverer_query(self):
        ## run tool:
        logging.info('Running tool')
        self.tools_discov = bAq.tools_discoverer(self.request_ID,
                                            self.inputs_kw,
                                            'temp',#output directory
                                            None, #default score 
                                            self.diff_weights # True is any custom weight entered
                                            ) 

        self.tools_discov.run_pipeline()
        self.data['tools'] = self.tools_discov.generate_outputs()
        self.data['result_found'] = self.tools_discov.result_found
        self.data['run_id'] = self.request_ID.hex
        
        logging.info('Pushing to db')
        db_results.push(self.data)

def fetch_from_db(run_id):
    results = db_results.query_by_id(run_id)
    results.pop('_id')
    return(results)

app = FastAPI(
    title="FAIR Tool Discoverer API",
    description="API for the FAIR Tool Discoverer",
    version="0.1.0",
    contact={
        "name": "Eva Martin",
        "email": "eva.martin@bsc.es",
        },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    root_path="/api"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class termWeight(BaseModel):
    label: str = Field(..., example="Proteomics")
    id: Optional[str] = Field(None, example="http://edamontology.org/topic_0091")
    #weight can be float or integer
    weight: Optional[Union[int, float, str]] = Field(..., example=1.0)

class termsWeights(BaseModel):
    data: List[termWeight]

@app.post('/')
def run_discoverer(data: termsWeights):
    logging.info('Request received')
    try:
        this_run = unique_run(data.data)
        this_run.run_tool_discoverer_query()
        
    except Exception as err:
        logging.error(err)
        data = {'message': 'An error ocurred', 'status': 'ERROR'}
    else:
        data = {'message': this_run.data, 'status': 'SUCCESS'}
    finally:
        return data


@app.get('/result/fetch')
def send_results(id: str):
    try:
        data = fetch_from_db(id)
    except Exception as err:
        logging.error(err)
        data = {'message': "An error ocurred", 'status': 'ERROR'}
    else:
        data = {'message': data, 'status': 'SUCCESS'}
    finally:
        return data


if __name__ == '__main__':
    load_dotenv()
    app.run(debug=True)
