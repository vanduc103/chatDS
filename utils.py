import openai
import json
import uuid
import sqlite3

class Utils:
    def __init__(self, user_id, file_id):
        self.user_id = user_id
        self.file_id = file_id

    def response(self, prefix, codex_name="text-davinci-003", 
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
        return response['choices'][0]['text']

    def read_code(self, prompt_list, cell_idx):
        code = ""
        for i in range(cell_idx+1):
            code += prompt_list[i]['generated_code']
        return code

    def write_code(self, nb_file, code, out, cell_idx):
        # open notebook as json
        nb_code = json.load(open(nb_file))
        cells = nb_code['cells']
        if len(cells) < (cell_idx + 1):
            for c in range((cell_idx + 1) - len(cells)):
                new_cell = {
                   "cell_type": "code",
                   "execution_count": None,
                   "id": str(uuid.uuid4()).split('-')[0],
                   "metadata": {},
                   "outputs": [],
                   "source": []
                  }
                cells.append(new_cell)
        # write the code to notebook
        nb_code['cells'][cell_idx]['source'] = out
        #nb_code['cells'][cell_idx]['outputs'][0]['text'] = ''
        with open(nb_file, 'w', encoding='UTF-8') as f:
            json.dump(nb_code, f)
    
    def write_code1(self, code_file, nb_file, code, out, cell_idx):
        # write the code to file
        #with open(code_file, 'w', encoding='UTF-8') as credit_code:
        #    credit_code.write(code)

        # open notebook as json
        nb_code = json.load(open(nb_file))
        cells = nb_code['cells']
        if len(cells) < (cell_idx + 1):
            for c in range((cell_idx + 1) - len(cells)):
                new_cell = {
                   "cell_type": "code",
                   "execution_count": None,
                   "id": str(uuid.uuid4()).split('-')[0],
                   "metadata": {},
                   "outputs": [],
                   "source": []
                  }
                cells.append(new_cell)
        # write the code to notebook
        nb_code['cells'][cell_idx]['source'] = out
        #nb_code['cells'][cell_idx]['outputs'][0]['text'] = ''
        with open(nb_file, 'w', encoding='UTF-8') as f:
            json.dump(nb_code, f)

    def sqlite3_db(self):
        con = sqlite3.connect("promptbase.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE prompt(rid INTEGER PRIMARY KEY, user_id, file_id, prompt_id INTEGER, instruction, problem, ans,\
                    prompt_task, prompt_what, prompt_how, prompt, generated_code, prompt_source, data_source, pre_id)")
        cur.execute("CREATE TABLE prompt_his(rid INTEGER PRIMARY KEY, user_id, file_id, prompt_id INTEGER, prompt, generated_code, prompt_source, data_source)")
        con.commit()
        con.close()

        
    def update_prompt(self, prompt_list, cell_idx, instruction, problem, ans, prompt_task, prompt_what, prompt_how, 
                      generated_code, pre_prompt_idx=None, prompt_source='', data_source=''):

        user_id=self.user_id
        file_id=self.file_id
        # create data to update/insert db
        pre_id = ''
        if pre_prompt_idx is not None:
            if isinstance(pre_prompt_idx, list):
                pre_id = ','.join(pre_prompt_idx)
            else:
                pre_id = str(pre_prompt_idx)

        # open db
        con = sqlite3.connect("promptbase.db")
        c = con.cursor()

        # check if prompt existed
        data = tuple((cell_idx, user_id, file_id))
        res = c.execute("SELECT COUNT(*) FROM prompt WHERE prompt_id = ? AND user_id = ? AND file_id = ?", data)
        if res.fetchall()[0][0] > 0:
            # get prompt his
            data = tuple((cell_idx, user_id, file_id))
            prompt_his = c.execute("SELECT prompt_id, prompt, generated_code, prompt_source, data_source FROM prompt \
                                    WHERE prompt_id = ? AND user_id = ? AND file_id = ?", data)
            prompt_his = prompt_his.fetchall()[0]
            data = tuple((prompt_his[0], prompt_his[1], prompt_his[2], 
                          prompt_his[3], prompt_his[4], user_id, file_id))
            #print(data)
            # save to prompt_his
            c.execute("INSERT INTO prompt_his(prompt_id, prompt, generated_code, prompt_source, data_source, user_id, file_id)\
                        VALUES (?, ?, ?, ?, ?, ?, ?)", data)
            con.commit()

            # prepare data to update db
            prompt = '{} {} {}'.format(prompt_task, prompt_what, prompt_how)
            data = tuple((prompt_task, prompt_what, prompt_how, prompt, generated_code, prompt_source, data_source, 
                          pre_id, cell_idx, user_id, file_id))
            #print(data)
            # update into db
            c.execute("UPDATE prompt SET prompt_task=?, prompt_what=?, prompt_how=?, prompt=?, generated_code=?,\
                        prompt_source=?, data_source=?, pre_id=? \
                        WHERE prompt_id=? AND user_id=? AND file_id=?", data)
            con.commit()
        else:
            # prepare data to insert into db
            prompt = '{} {} {}'.format(prompt_task, prompt_what, prompt_how)
            data = tuple((cell_idx, instruction, problem, ans, prompt_task, prompt_what, prompt_how, prompt, generated_code,
                          prompt_source, data_source, pre_id, user_id, file_id))
            # save to db
            c.execute("INSERT INTO prompt(prompt_id, instruction, problem, ans, prompt_task, prompt_what, prompt_how, prompt,\
                       generated_code, prompt_source, data_source, pre_id, \
                       user_id, file_id) \
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
            con.commit()
        con.close()

        # add to prompt list
        prompt = '{} {} {}'.format(prompt_task, prompt_what, prompt_how)
        prompt_list[cell_idx] = {
                                'instruction': instruction,
                                'problem': problem,
                                'ans': ans,
                                'prompt_task': prompt_task,
                                'prompt_what': prompt_what,
                                'prompt_how': prompt_how,
                                'prompt': prompt,
                                'generated_code': generated_code,
                                'prompt_source': prompt_source,
                                'data_source': data_source,
                                'pre_prompt_idx': pre_prompt_idx,
                                }

    # back up
    def update_prompt1(self, prompt_list, cell_idx, instruction, problem, ans, prompt, generated_code, 
                      pre_prompt_idx=None, prompt_type='Auto', prompt_source=''):

        user_id=self.user_id
        file_id=self.file_id
        # create data to update/insert db
        pre_id = ''
        if pre_prompt_idx is not None:
            if isinstance(pre_prompt_idx, list):
                pre_id = ','.join(pre_prompt_idx)
            else:
                pre_id = str(pre_prompt_idx)

        # open db
        con = sqlite3.connect("promptbase1.db")
        c = con.cursor()

        # update prompt_his
        if prompt_list[cell_idx] != None:
            # get prompt his
            prompt_his = prompt_list[cell_idx]
            data = tuple((cell_idx, prompt_his['prompt'], prompt_his['generated_code'], user_id, file_id))
            #print(data)
            # save to prompt_his
            c.execute("INSERT INTO prompt_his(prompt_id, prompt, generated_code, user_id, file_id) VALUES (?, ?, ?, ?, ?)", data)
            con.commit()

            # prepare data to update db
            data = tuple((prompt, generated_code, prompt_type, prompt_source, pre_id, cell_idx, user_id, file_id))
            #print(data)
            # update into db
            c.execute("UPDATE prompt SET prompt=?, generated_code=?, prompt_type=?, prompt_source=?, pre_id=? \
                        WHERE id=? AND user_id=? AND file_id=?", data)
            con.commit()
        else:
            # prepare data to insert into db
            data = tuple((cell_idx, instruction, problem, ans, prompt, generated_code, prompt_type, prompt_source, pre_id, user_id, file_id))
            # save to db
            c.execute("INSERT INTO prompt(id, instruction, problem, ans, prompt, generated_code, prompt_type, prompt_source, pre_id, \
                       user_id, file_id) \
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
            con.commit()
        con.close()

        # add to prompt list
        prompt_list[cell_idx] = {
                                'instruction': instruction,
                                'problem': problem,
                                'ans': ans,
                                'prompt': prompt,
                                'generated_code': generated_code,
                                'prompt_type': prompt_type,
                                'prompt_source': prompt_source,
                                'pre_prompt_idx': pre_prompt_idx,
                                }

