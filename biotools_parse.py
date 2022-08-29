global webTypes
webTypes = ['Web API', 'Web application', 'Web service', 'Suite', 'Workbench', 'Database portal']


def getFormats(instances):
    inputs = [a.input for a in instances]
    inputs_ = [a for a in inputs]
    inputsNames = []

    nonSFormats = ['txt', 'text', 'csv', 'tsv', 'tabular', 'xml', 'json', 'nucleotide', 'pdf', 'interval' ]
    for List in inputs_:
        for eachD in List:
            if 'format' in eachD.keys():
                if ' format' not in eachD['format']['term'] and eachD['format']['term'].lstrip() not in nonSFormats:
                    if '(text)' not in eachD['format']['term']:
                        if eachD['format']['term'].lstrip() not in inputsNames:
                            inputsNames.append(eachD['format']['term'].lstrip())
    return(inputsNames)

class instance(object):

    def __init__(self, name):

        # TODO: restrict the format of properties

        # TODO: include @id
        self.name = name
        self.name_fanvy = None
        self.description = None # string
        self.version = None
        self.super_type = None
        self.type = None
        self.links =[]
        self.publication =  0 # number of related publications [by now, for simplicity]
        self.download = []  # list of lists: [[type, url], [], ...]
        self.inst_instr = False # boolean // FUTURE: uri or text
        self.test = False # boolean // FUTURE: uri or text
        self.src = [] # string
        self.os = [] # list of strings
        self.input = [] # list of dictionaries biotools-like {'format' : <format> , 'uri' : <uri> , 'data' : <data> , 'uri': <uri>}
        self.output = [] # list of dictionaries biotools-like {'format' : <format> , 'uri' : <uri> }
        self.dependencies = [] # list of strings
        self.documentation = [] # list of lists [[type, url], [type, rul], ...]
        self.license = False # string
        self.termsUse = False #
        self.contribPolicy = False
        self.authors = [] # list of strings
        self.repository = []
        self.source = [] #string
        self.bioschemas = False
        self.https = False
        self.operational = False
        self.ssl = False
        self.topic = False
        self.operation = None
        self.biotoolsid = None


def cleanVersion(version):
    if version != None:
        if '.' in version:
            return(version.split('.')[0]+'.'+ version.split('.')[1])
        else:
            return(version)
    else:
        return(version)

def lowerInputs(listInputs):
    newList = []
    if len(listInputs)>0:
        for format in listInputs:
            newFormat = {}
            for a in format.keys():
                newInner = {}
                if format[a] != []:
                    if type(format[a]) == list:
                        for eachdict in format[a]:
                            for e in eachdict.keys():
                                newInner[e] = eachdict[e].lower()
                            newFormat[a] = newInner
                    else:
                        for e in format[a].keys():
                            newInner[e] = format[a][e].lower()
                        newFormat[a] = newInner
        newList.append(newFormat)
    else:
        return([])
    return(newList)

def parse_type(tool):
    types = tool.get("toolType")
    types_web  = []
    types_noweb = []
    if types:
        for t in types:
            if t in webTypes:
                types_web.append(t)
            else:
                types_noweb.append(t)
    return(types_web, types_noweb)

class biotoolsToolsGenerator(object):

    def __init__(self, tools, source = 'biotools'):

        self.tools = tools
        self.source = source
        self.instances = []

        for tool in self.tools:
            if tool.get("toolType"):
                types_web, types_noweb = parse_type(tool)
                if types_web:
                    self.build_instance(tool, types_web, 'web')
                if types_noweb:
                    self.build_instance(tool, types_noweb, 'no_web')
            else:
                # if no type stated, we assume it is no-web since these are the most common
                self.build_instance(tool, None, 'no_web')


    def build_instance(self, tool, types, super_type):

            name = tool['name'].lower()
            

            newInst = instance(name)
            newInst.name_fancy = tool['name']
            newInst.super_type = super_type
            newInst.type = tool.get("toolType")
            newInst.version = self.parse_versions(tool)
            newInst.description = tool.get('description')
            newInst.homepage = tool.get('homepage')
            newInst.publication = tool['publication']
            newInst.download = self.parse_download(tool)
            newInst.src = self.parse_src(tool)
            newInst.os = tool.get('operatingSystem')
            newInst.input = self.parse_input(tool)
            newInst.output = self.parse_output(tool)
            newInst.documentation = self.parse_documentation(tool)
            newInst.inst_instr = self.parse_install_instr(tool, newInst)
            newInst.license = tool.get('license')
            newInst.authors = self.parse_authors(tool)
            newInst.repository = self.parse_repositories(tool)
            newInst.topic = tool.get('topic')
            newInst.operation = self.parse_operation(tool)
            newInst.links = tool.get('link')
            newInst.biotoolsID = tool.get('biotoolsID')
            newInst.source = ['biotools']

            self.instances.append(newInst)
    

    def parse_versions(self, tool):
        versions = []
        if type(tool.get("version")) == list:
            for v in tool.get("version"):
                versions.append(cleanVersion(v))
        return(versions)


    def parse_download(self, tool):
        links = [ [tol['type'], tol['url']] for tol in tool['download'] ]
        return(links)


    def parse_src(self, tool):
        src = []
        for down in [a for a in tool['download'] if a['type'] == 'Source package']:
            src.append(down['url'])
        for down in [a for a in tool['download'] if a['type'] == 'Source code']:
            src.append(down['url'])
        return(src)

    def parse_operation(self, tool):
        ops = []
        if len(tool['function'])>0:
            ops = [f['operation'] for f in tool['function']]
            return(ops[0])
        else:
            return(None)
    
    def parse_input(self, tool):
        inputs = []
        if len(tool['function'])>0:
            inputs = [f['input'] for f in tool['function']]
            return(lowerInputs(inputs[0]))
        else:
            return([])

    def parse_output(self, tool):
        outputs = []
        if len(tool['function'])>0:
            outputs = [f['output'] for f in tool['function']]
            return(lowerInputs(outputs[0]))
        else:
            return([])

    def parse_documentation(self, tool):
        doc = [ [tol['type'], tol['url']] for tol in tool['documentation'] ]
        return(doc)
    
    def parse_install_instr(self, tool, newInst):
        for d in newInst.documentation:
            if 'manual' in d[0][0].lower():
                return(True)
        else:
            return(False)
        
    def parse_authors(self, tool):
        newAuth = []
        for dic in tool['credit']:
            if dic['name'] not in newAuth and dic['name']!=None:
                newAuth.append(dic['name'])
        return(newAuth)
    
    def parse_repositories(self, tool):
        repos = []
        for link in tool['link']:
            if "Repository" in link['type']:
                repos.append(link['url'])
        return(repos)