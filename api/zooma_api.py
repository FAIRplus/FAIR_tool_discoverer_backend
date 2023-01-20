import requests
import json

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

### ZOOMA

def build_url():
    call_template = ""
    url = call_template.format()
    return(url)

def get_url(URL):
    try:
        response = requests.get(URL)
    except Exception as err:
        error_text = f"ERROR: Something went wrong while making a request for URL: {URL}."
        print(f"{bcolors.FAIL}{error_text}{bcolors.ENDC}")
        raise(err)
    else:
        try:
            response = json.loads(response.text)
        except Exception as err:
            error_text = f"ERROR: Something went wrong while parsing the JSON file after requesting {URL}."
            print(f"{bcolors.FAIL}{error_text}{bcolors.ENDC}")
            raise(err)
        else:   
            return(response)

def filter_by_confifence(match, confident_matches, confidence=['GOOD','HIGH']):
    #print(f"{match['annotatedProperty']['propertyValue']} - {match['confidence']}")
    if match['confidence'] in confidence:
        summary_result = {'edam_term':match['semanticTags'][0],'label':match['annotatedProperty']['propertyValue'],'confidence':match['confidence']}
        confident_matches.append(summary_result)
    return(confident_matches)

def zooma_single_lookup(keyword):
    # build URL
    url=f"https://www.ebi.ac.uk/spot/zooma/v2/api/services/annotate?propertyValue={keyword}&filter=required:[none],ontologies:[edam]"
    # get JSON
    zooma_result = get_url(url)
    print(json.dumps(zooma_result, indent=4, sort_keys=False))
    confident_matches = []
    for match in zooma_result:
        confident_matches = filter_by_confifence(match, confident_matches)
    return(confident_matches)
    

def query_zooma(keywords):
    '''
    keywords is a set of strings to look up in zooma
    '''
    results = {}
    for keyword in keywords:
        results[keyword]=[]
        print(f"{bcolors.BOLD}{keyword}{bcolors.ENDC}")
        confident_matches = zooma_single_lookup(keyword)
        if confident_matches:
            [print(f"\t{match['label']} - {match['confidence']} - {match['edam_term']}") for match in confident_matches]
            results[keyword] = confident_matches
    
    return(results)

