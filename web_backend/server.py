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
from utils import read_code, response, update_prompt, update_prompt_code, prompt_list_len

from argparse import ArgumentParser


app = Flask(__name__, static_url_path="")
app.config['SECRET_KEY'] = 'Snu2022!'
app.config['UPLOAD_FOLDER'] = upload_folder
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)

    
prompt_list = [None] * 100

instruction = '''You are the python code generation for a data science problem.
Please always generate the full training code given the previous code and the prompt.
'''

problem = '''Problem Description:
'''

ans = '''
A:
<code>
'''

data_file = ''

initial_templates = []

def prompt_preprocessing(prompt):
    dataset_metadata = '\nDataset Information:\n'
    data_values = '\nData Values:\n'
    global data_file
    
    prompt_support = ''
    if "@problem" in prompt:
        prompt = prompt.replace("@problem", "").strip()
        prompt_support += problem
        
    if "@datafile" in prompt:
        prompt = prompt.replace("@datafile", "").strip()
        prompt_support += 'Data file name: {}.\n'.format(data_file)
        
    if "@metadata" in prompt:
        prompt = prompt.replace("@metadata", "").strip()
        dataset_metadata += get_dataset_metadata(data_file)
        prompt_support += dataset_metadata + '\n------------\n'
        
    if "@data-values" in prompt:
        instr = prompt[prompt.index("@data-values"):]
        prompt = prompt.replace(instr, "").strip()
        col_name = instr.split("/")[1]
        col_names = [col for col in col_name.split(",")]
        col_names = [col.replace('\'', "").replace('\"', "") for col in col_names]
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
    values = df[col_name].to_numpy()
    # get random 10 elements
    values = values[np.random.choice(values.shape[0], 10, replace=False), :]
    return str(values)

def allowed_file(filename):
    return not allowed_extensions or ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions)

def exec_code(code):
    import warnings
    warnings.filterwarnings("ignore")
    import sys
    from io import StringIO
    from contextlib import redirect_stdout
    
    code = '''{}'''.format(code)

    f = StringIO()
    with redirect_stdout(f):
        exec(code)

    out_value = f.getvalue()
    print(out_value)
    return out_value


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
        global data_file
        global problem
        
        email = args['email']
        #openai_key = args['openai_key']
        problem += args['problem_description'] + "\n"
        data_file = args['file_path']
        print(data_file)
        # get file name
        file_name = os.path.splitext(os.path.basename(data_file))[0]
        #nb_file = os.path.join(os.path.dirname(data_file), file_name + '.ipynb')
        #print(nb_file)
        
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
        #email = data.get('email','')
        prompt_content = prompt_content.replace("##","").replace("Prompt", "").strip()
        if len(prompt_content) == 0:
            return [{"code": ""}]
        
        global prompt_list
        
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
        # write code
        #write_code(nb_file, prompt_list, prompt_id)
        
        return res
    
class UserFeedbackAPI(Resource):
    def __init__(self):
        super(UserFeedbackAPI, self).__init__()
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
        #email = data.get('email','')
        prompt_content = prompt_content.replace("##","").replace("Prompt", "").strip()
        if len(prompt_content) == 0:
            return [{"id": prompt_id, "prompt": prompt_content, "code": ""}]
        
        global prompt_list
        
        res = []
        promptlist_len = prompt_list_len(prompt_list)
        code = read_code(prompt_list, max(0, promptlist_len-1))
        code += '\n----------\n'
        
        # add datafile and data metadata to prompt content (at the first time)
        if promptlist_len == 0:
            prompt_content += "@datafile.@metadata"
        # get data file and data metadata information
        prompt_content, prompt_support = prompt_preprocessing(prompt_content)
        
        # create prompt for chatgpt
        prompt =  prompt_support + '\n' + code + instruction + prompt_content + ans
        print(prompt)
        
        # call openai api
        if open_api_mode:
            out = response(openai_key, prompt)
        else:
            out = "print('test code of prompt {}')".format(prompt_id)
        print('>>', out)
        
        # execute code
        out_value = exec_code(out)
        
        # return result
        res.append({"id": prompt_id, "prompt": prompt_content, "code": out})
        # update prompt list
        update_prompt(prompt_list, prompt_id, instruction, problem, ans, prompt_content, out)
        # write code
        #write_code(nb_file, prompt_list, prompt_id)
        
        return res
    
class PromptUpdateAPI(Resource):
    def __init__(self):
        super(PromptUpdateAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("prompt_id", type=str, location='json', required=True, default='')
        self.reqparse.add_argument("code", type=str, location='json', required=True, default='')
        self.reqparse.add_argument("email", type=str, location='json', required=False, default='')


    def post(self):
        """Update new code for prompt list
        """
        args = self.reqparse.parse_args()
        data = args['prompt']
        print(data)
        prompt_id = int(data['prompt_id'])
        prompt_code = data['code']
        #email = data.get('email', '')
        print(prompt_code)
        
        global prompt_list
        # update prompt list
        update_prompt_code(prompt_list, prompt_id, prompt_code)
        # write code
        #write_code(nb_file, prompt_list, prompt_id)
            
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
api.add_resource(UserFeedbackAPI, '/api/v1/user_feedback', endpoint='user_feedback')
api.add_resource(PromptUpdateAPI, '/api/v1/prompt_update', endpoint='prompt_update')
api.add_resource(TestAPI, '/api/v1/test', endpoint='test')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--port", type=int, default=38500)
    args = parser.parse_args()
    app.run(debug=True, host='0.0.0.0', port=args.port)
