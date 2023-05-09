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
from config import upload_folder, allowed_extensions
from utils import read_code, response, update_prompt


app = Flask(__name__, static_url_path="")
app.config['SECRET_KEY'] = 'Snu2022!'
app.config['UPLOAD_FOLDER'] = upload_folder
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)

    
prompt_list = [None] * 100
openai_key = ''

instruction = '''Instruction: You are a code generation assistant for data science problem. 
Code is in Python. Please import all required libraries.
The data science problem is in the "Problem Description" part.
The dataset information is in the "Dataset Information" part.
The data values information is in the "Data Values" part.
Please follow carefully each sentence in the prompt after the "Q:".
'''

problem = '''Problem Description:
'''

prompt_content = ''

ans = '''A:
<code>'''

data_file = ''

initial_templates = [
    'Imports various libraries and modules to perform data preprocessing, data analysis and data visualization.',
    'Reading the dataset in {} file into a DataFrame and Show first 5 rows.',
    'Show dataset information.',
    'Check null values.',
]

def get_dataset_metadata(data_file):
    df = pd.read_csv(data_file)
    import io
    buf = io.StringIO()
    df.info(buf=buf)
    metadata = buf.getvalue()
    return metadata

def get_dataset_values(data_file, col_name):
    df = pd.read_csv(data_file)
    values = df[col_name].count_values()
    return str(values)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

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
        email = args['email']
        openai_key = args['openai_key']
        problem += args['problem_description']
        data_file = args['file_path']
            
        return {"result": "ok"}
    

class PromptInitAPI(Resource):
    def __init__(self):
        super(PromptInitAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()

    def post(self):
        """Fill in the template to create initial DS program
        """
        args = self.reqparse.parse_args()
        res = []
        for idx in range(len(initial_templates)):
            template = initial_templates[idx]
            code = read_code(prompt_list, idx-1)
            prompt_content = 'Q:' + template.format(data_file)
            prompt = instruction + problem + prompt_content + ans
            
            #out = response(prompt)
            out = "print('test code')"
            res.append({"prompt_id": idx, "prompt": prompt_content.replace("Q:",""),
                   "code": out})
            # update prompt list
            update_prompt(prompt_list, idx, instruction, problem, ans, prompt_content, out)
            
        return res

class CodeGenerationAPI(Resource):
    def __init__(self):
        super(CodeGenerationAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()
        #self.reqparse.add_argument("prompt_id", type=int, location='json', default=0)
        self.reqparse.add_argument("prompt", type=json, required=True)

    def post(self):
        """Code generation for a user prompt
        """
        args = self.reqparse.parse_args()
        user_prompt = json.loads(args['prompt'])
        prompt_id = user_prompt['prompt_id']
        prompt_content = user_prompt['prompt']
        
        need_dataset_metadata = False
        need_data_values = False
        dataset_metadata = '''Dataset Information:
        '''
        data_values = '''Data Values:
        '''
        
        if need_dataset_metadata:
            dataset_metadata += get_dataset_metadata(data_file)
        if need_data_values:
            col_name = ['']
            data_values += get_dataset_values(data_file, col_name)
        
        res = []
        code = read_code(prompt_list, prompt_id)
        prompt_content = "Q:" + prompt_content
        prompt = instruction + dataset_metadata + data_values + prompt_content + ans
            
        #out = response(prompt)
        out = "print('test code')"
        res.append({"prompt_id": prompt_id, "prompt": prompt,
                   "code": out})
        # update prompt list
        update_prompt(prompt_list, prompt_id, instruction, problem, ans, prompt_content, out)
            
        return res
    
class PromptSaveAPI(Resource):
    def __init__(self):
        super(PromptSaveAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("prompt_list", type=json, required=True)

    def post(self):
        """Save prompt list from web
        """
        args = self.reqparse.parse_args()
        prompts = jsons.load(args['prompt_list'])
        
        for user_prompt in prompts:
            prompt_content = "Q:" + user_prompt['prompt']
            prompt_id = user_prompt['prompt_id']
            prompt_list[prompt_id]['prompt'] = prompt_content
            
        return {"result": "ok"}

    
api.add_resource(ProgramInitAPI, '/api/v1/init', endpoint='init')
api.add_resource(PromptInitAPI, '/api/v1/prompt_init', endpoint='prompt_init')

api.add_resource(CodeGenerationAPI, '/api/v1/code_generate', endpoint='code_generate')
api.add_resource(PromptSaveAPI, '/api/v1/prompt_save', endpoint='prompt_save')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=38500)
