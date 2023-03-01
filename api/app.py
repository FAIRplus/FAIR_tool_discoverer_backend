from os import path
from flask import Flask, request, jsonify, make_response
import pandas as pd
import uuid
from flask_cors import CORS,cross_origin

import biotools_API_querying as bAq
import db_results


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
        print('Parsing input...')
        try:
            for term in self.request.json['data']['textarea_content']:
                w=float(term['weight'])
                inputs_kw.append({
                    'keyword':term['label'].lower(), 
                    'classId':term['ClassId'],
                    'weight': w 
                    })
                weights.add(w)
            if len(weights)>1:
                self.diff_weights = True
            else:
                self.diff_weights = False
            
        except Exception as err:
                print(err)
                raise
        else:
            print(f"Input terms: {inputs_kw}")
            return(inputs_kw)

    def run_tool_discoverer_query(self):
        ## run tool:
        print('running tool')
        self.tools_discov = bAq.tools_discoverer(self.request_ID,
                                            self.inputs_kw,
                                            'temp',#output directory
                                            None, #default score 
                                            self.diff_weights, # True is any custom weight entered
                                            True) #verbosity

        self.tools_discov.run_pipeline()
        self.data['tools'] = self.tools_discov.generate_outputs()
        self.data['result_found'] = self.tools_discov.result_found
        self.data['run_id'] = self.request_ID.hex
        
        print('pushing to db')
        db_results.push(self.data)

def fetch_from_db(run_id):
    results = db_results.query_by_id(run_id)
    results.pop('_id')
    return(results)


app = Flask(__name__,
            static_url_path='',
            static_folder='assets',
            template_folder='templates')

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# CORS
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'



@app.route('/',methods = ['POST'])
@cross_origin(origin='*', headers=['Content-Type'], methods=['POST'])
def run_discoverer():
    print('request received')
    if request.method == 'POST':
        try:
            # run query
            # print(request.json)
            this_run = unique_run(request)
            this_run.run_tool_discoverer_query()
            
        except Exception as err:
            data = {'message': str(err), 'code': 'ERROR'}
            resp = make_response(jsonify(data), 400)
            print(err)
            return(resp)
        else:
            #prepare response
            data = {'message': this_run.data, 'code': 'SUCCESS'}
            resp = make_response(jsonify(data), 201)

            return resp
    else:
      return(make_response('not post', 400))

@app.route('/result/fetch', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def send_misc():
    run_id = request.args.get('id')
    try:
        data = fetch_from_db(run_id)
    except Exception as err:
        data = {'message': "something went wrong", 'code': 'ERROR'}
        resp = make_response(jsonify(data), 400)
        print(err)
    else:
        data = {'message': data, 'code': 'SUCCESS'}
        resp = make_response(jsonify(data), 201)
    finally:

        return resp


if __name__ == '__main__':
    load_dotenv()
    app.run(debug=True)
