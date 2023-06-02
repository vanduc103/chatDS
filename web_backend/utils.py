import json
import os
import nbformat as nbf

def prompt_list_len(prompt_list):
    promptlist_len = 0
    for i in range(len(prompt_list)):
        if prompt_list[i] is not None:
            promptlist_len += 1
    return promptlist_len

def read_codev1(prompt_list, cell_idx):
    code = ""
    promptlist_len = prompt_list_len(prompt_list)
    for i in range(min(promptlist_len, cell_idx+1)):
        code += prompt_list[i]['generated_code']
    return code

def read_code(prompt_list, cell_idx):
    code = ""
    output = ""
    promptlist_len = prompt_list_len(prompt_list)
    # get the latest code idx
    code_idx = promptlist_len-1
    if code_idx >= 0:
        code += prompt_list[code_idx]['generated_code']
        output += prompt_list[code_idx]['output']
    return code, output

def write_code(nb_file, prompt_list, cell_idx):
    # create a nb_file if not existed
    if not os.path.isfile(nb_file):
        notebook = nbf.v4.new_notebook()
        nbf.write(notebook, nb_file)

    # check prompt_list
    if prompt_list_len(prompt_list) <= cell_idx:
        return ''

    # open notebook as json
    nb_code = json.load(open(nb_file))
    if len(nb_code['cells']) < (2*cell_idx + 2):
        for c in range((2*cell_idx + 2) - len(nb_code['cells'])):
            prompt_cell = {
               "cell_type": "markdown",
               "execution_count": None,
               "metadata": {},
               "outputs": [],
               "source": []
              }
            code_cell = {
               "cell_type": "code",
               "execution_count": None,
               "metadata": {},
               "outputs": [],
               "source": []
              }
            nb_code['cells'].append(prompt_cell)
            nb_code['cells'].append(code_cell)
    # write the prompt and code to cell
    nb_code['cells'][2*cell_idx]['source'] = prompt_list[cell_idx]['prompt']
    nb_code['cells'][2*cell_idx+1]['source'] = prompt_list[cell_idx]['generated_code']
    with open(nb_file, 'w', encoding='UTF-8') as f:
        json.dump(nb_code, f)
    
import openai
def responsev1(openai_key, prefix, codex_name="text-davinci-003", 
                         max_tokens=2048,
                         temperature=0.2,
                         top_p=1.0):

    #key = "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"
    key = openai_key
    try:
        response = openai.Completion.create(
                        engine=codex_name,
                        prompt=prefix,
                        suffix=None,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        api_key=key,
                        top_p=top_p,
                        frequency_penalty=0,
                        presence_penalty=0,
                        stop=["</code>", "# SOLUTION END"],
                        logprobs=1,
                        n=1,
                    )
    except (openai.error.RateLimitError, openai.error.APIConnectionError) as e:
            print(type(e), e)
            return 'Please check the Error!!!'
    return response['choices'][0]['text']
    
    
def response(openai_key, prefix, codex_name="gpt-3.5-turbo", 
                         max_tokens=2048,
                         temperature=0.2,
                         top_p=1.0):

    #key = "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"
    key = openai_key
    try:
        response = openai.ChatCompletion.create(
                        model=codex_name,
                        messages=[{'role': 'user', 'content': prefix}],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        api_key=key,
                        top_p=top_p,
                        frequency_penalty=0,
                        presence_penalty=0,
                        stop=["</code>"],
                    )
    except (openai.error.RateLimitError, openai.error.APIConnectionError) as e:
            print(type(e), e)
            return 'Please check the Error!!!'
    return response['choices'][0]['message']['content']
    
def update_prompt(prompt_list, cell_idx, instruction, problem, ans, prompt, 
                      generated_code, code_output):

    # add to prompt list
    promptlist_len = prompt_list_len(prompt_list)
    code_idx = min(promptlist_len, cell_idx)
    prompt_list[code_idx] = {
                            'instruction': instruction,
                            'problem': problem,
                            'ans': ans,
                            'prompt': prompt,
                            'generated_code': generated_code,
                            'output': code_output,
                            }

def update_promptv1(prompt_list, cell_idx, instruction, problem, ans, prompt, 
                      generated_code, pre_prompt_idx=None, prompt_source='', data_source=''):

    # add to prompt list
    promptlist_len = prompt_list_len(prompt_list)
    code_idx = min(promptlist_len, cell_idx)
    prompt_list[code_idx] = {
                            'instruction': instruction,
                            'problem': problem,
                            'ans': ans,
                            'prompt': prompt,
                            'generated_code': generated_code,
                            'prompt_source': prompt_source,
                            'data_source': data_source,
                            'pre_prompt_idx': pre_prompt_idx,
                            }

def update_prompt_code(prompt_list, cell_idx, code):
    if prompt_list_len(prompt_list) > cell_idx:
        prompt_list[cell_idx]['generated_code'] = code
    