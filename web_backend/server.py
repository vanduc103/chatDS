#!flask/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""
import os
from flask import Flask, jsonify, abort, make_response, g, request, url_for, session
from flask_restful import Api, Resource, reqparse, marshal
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

import numpy as np
import pandas as pd
import json

from database import Database
from config import upload_folder, allowed_extensions, open_api_mode, jupyter_url, openai_key
from utils import read_code, response, update_prompt, update_prompt_code

from argparse import ArgumentParser


app = Flask(__name__, static_url_path="")
app.config['SECRET_KEY'] = 'Snu2022!'
app.config['UPLOAD_FOLDER'] = upload_folder
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)

    
prompt_list = [None] * 100
openai_key = ''

instruction = '''Instruction: You are the code generation assistant for a data science problem. 
Code is in Python. Please import all required libraries.
The data science problem is in the "Problem Description" part.
The dataset information is in the "Dataset Information" part.
The data values information is in the "Data Values" part.
Please follow carefully each sentence in the prompt after the "Q:".
'''

problem = '''Problem Description:
'''

dataset_metadata = '''Dataset Information:
'''
data_values = '''Data Values:
'''

prompt_content = ''

ans = '''
A:
<code>
'''

data_file = ''

initial_templates = [
    'Imports various libraries and modules to perform data preprocessing, data analysis and data visualization.@problem',
    'Reading the dataset in {} file into a DataFrame and Show first 5 rows.',
    'Show dataset information.',
    'Check null values.',
]

def prompt_preprocessing(prompt):
    global dataset_metadata
    global data_values
    
    prompt_support = ''
    if "@problem" in prompt:
        prompt = prompt.replace("@problem", "").strip()
        prompt_support += problem
    if "@metadata" in prompt:
        prompt = prompt.replace("@metadata", "").strip()
        dataset_metadata += get_dataset_metadata(data_file)
        prompt_support += dataset_metadata
    if "@data-values" in prompt:
        instr = prompt[prompt.index("@data-values"):]
        prompt = prompt.replace(instr, "").strip()
        col_name = instr.split("/")[1]
        col_names = [col for col in col_name.split(",")]
        data_values += get_dataset_values(data_file, col_names)
        prompt_support += data_values
        
    return prompt, prompt_support

def get_dataset_metadata(data_file):
    df = pd.read_csv(data_file)
    import io
    buf = io.StringIO()
    df.info(buf=buf)
    metadata = buf.getvalue()
    return metadata

def get_dataset_values(data_file, col_name):
    df = pd.read_csv(data_file)
    values = df[col_name].value_counts()
    return str(values)

def allowed_file(filename):
    return not allowed_extensions or ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions)

@app.route('/api/v1/upload_file', methods=['POST'])
#@cross_origin()
#@auth.login_required
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'status' : 'error', 'msg': 'No File Part'})
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({'status' : 'error', 'msg': 'No Selected File'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        return jsonify({'status': 'success', 'file_path': path})
    return jsonify({'status': 'error', 'msg': 'Cannot save file'})


class ProgramInitAPI(Resource):
    def __init__(self):
        super(ProgramInitAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("email", type=str, location='json', default='')
        self.reqparse.add_argument("openai_key", type=str, location='json', default='')
        self.reqparse.add_argument("problem_description", type=str, location='json', default='')
        self.reqparse.add_argument("file_path", type=str, location='json', default='')

    def post(self):
        """Check if user exists in DB
        """
        args = self.reqparse.parse_args()
        global email
        global openai_key
        global problem
        global data_file
        email = args['email']
        #openai_key = args['openai_key']
        problem += args['problem_description'] + "\n"
        data_file = args['file_path']
        print(data_file)
        
        # create a new folder for a user
        user_folder = email.split('@')[0]
            
        return {"url": jupyter_url}
    

class PromptInitAPI(Resource):
    def __init__(self):
        super(PromptInitAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()

    def post(self):
        """Fill in the template to create initial DS program
        """
        args = self.reqparse.parse_args()
        res = []
        global prompt_list
        for idx in range(len(initial_templates)):
            template = initial_templates[idx]
            code = read_code(prompt_list, idx-1)
            prompt_content = 'Q:' + template.format(data_file)
            prompt_content, prompt_support = prompt_preprocessing(prompt_content)
            prompt = instruction + prompt_support + prompt_content + ans + code
            print(prompt)
            
            if open_api_mode:
                out = response(openai_key, prompt)
            else:
                out = "print('test code " + str(idx) + "')"
            print(out)
            res.append({"prompt_id": idx, "prompt": prompt_content.replace("Q:",""),
                   "code": out})
            # update prompt list
            update_prompt(prompt_list, idx, instruction, problem, ans, prompt_content, out)
            
        return res

class CodeGenerationAPI(Resource):
    def __init__(self):
        super(CodeGenerationAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("prompt", type=dict, required=True)

    def post(self):
        """Code generation for a user prompt
        """
        args = self.reqparse.parse_args()
        data = args['prompt']
        print(data)
        prompt_id = int(data['prompt_id'])
        prompt_content = data['prompt']
        email = data.get('email','')
        prompt_content = prompt_content.replace("##","").replace("Prompt", "").strip()
        if len(prompt_content) == 0:
            return [{"code": ""}]
        
        promptlist_len = 0
        global prompt_list
        for i in range(len(prompt_list)):
            if prompt_list[i] is not None:
                promptlist_len += 1
        print('promptlist:', promptlist_len)
        
        res = []
        code = read_code(prompt_list, prompt_id-1)
        prompt_content = "Q:" + prompt_content
        prompt_content, prompt_support = prompt_preprocessing(prompt_content)
        prompt = instruction + prompt_support + prompt_content + ans + code
        print(prompt)
        
        if open_api_mode:
            out = response(openai_key, prompt)
        else:
            out = "print('test code')"
        print('>>', out)
        res.append({"code": out})
        # update prompt list
        update_prompt(prompt_list, prompt_id, instruction, problem, ans, prompt_content, out)
        return res
    
class PromptUpdateAPI(Resource):
    def __init__(self):
        super(PromptSaveAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("prompt", type=dict, required=True)

    def post(self):
        """Update new code for prompt list
        """
        args = self.reqparse.parse_args()
        data = args['prompt']
        print(data)
        prompt_id = int(data['prompt_id'])
        prompt_code = data['code']
        email = data['email']
        print(prompt_code)
        # update prompt list
        update_prompt_code(prompt_list, prompt_id, prompt_code)
            
        return {"result": "ok"}

class TestAPI(Resource):
    def __init__(self):
        super(TestAPI, self).__init__()

    def get(self):
        """Save prompt list from web
        """
        return {"url": "http://147.47.236.89:8888/tree"}
    
api.add_resource(ProgramInitAPI, '/api/v1/init', endpoint='init')
api.add_resource(PromptInitAPI, '/api/v1/prompt_init', endpoint='prompt_init')

api.add_resource(CodeGenerationAPI, '/api/v1/code_generate', endpoint='code_generate')
api.add_resource(PromptUpdateAPI, '/api/v1/prompt_update', endpoint='prompt_update')
api.add_resource(TestAPI, '/api/v1/test', endpoint='test')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--port", type=int, default=38500)
    args = parser.parse_args()
    app.run(debug=True, host='0.0.0.0', port=args.port)
