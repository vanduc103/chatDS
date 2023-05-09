import json
def read_code(prompt_list, cell_idx):
        code = ""
        for i in range(cell_idx+1):
            code += prompt_list[i]['generated_code']
        return code

import openai
def response(prefix, codex_name="text-davinci-003", 
                         max_tokens=1024,
                         temperature=0.0,
                         top_p=1.0):

        key = "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"
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
    
def update_prompt(prompt_list, cell_idx, instruction, problem, ans, prompt, 
                      generated_code, pre_prompt_idx=None, prompt_source='', data_source=''):

    # add to prompt list
    prompt_list[cell_idx] = {
                            'instruction': instruction,
                            'problem': problem,
                            'ans': ans,
                            'prompt': prompt,
                            'generated_code': generated_code,
                            'prompt_source': prompt_source,
                            'data_source': data_source,
                            'pre_prompt_idx': pre_prompt_idx,
                            }
    