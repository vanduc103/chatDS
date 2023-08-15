import psycopg2 as db
import hashlib
from config import *

class Database:
    def __init__(self):
        self.con = db.connect(host=host, port=port, user=user, password=password, database=dbname)
        self.cur = self.con.cursor()

    def close(self):
        self.cur.close()
        self.con.close()

    """
    for kernel table
    """
    def get_kernel_by_ref(self, kernel_ref):
        self.cur.execute("SELECT k.id FROM kernels as k WHERE ref = %s", (kernel_ref,))
        result = self.cur.fetchall()
        self.close()
        kernel_id = 0
        if result and len(result) > 0:
            kernel_id = result[0][0]
        return kernel_id
        
    """
    for workflow table
    """
    def list_workflow(self):
        self.cur.execute("SELECT k.ref AS kernel, w.* FROM workflow as w INNER JOIN kernels as k ON w.kernel_id = k.id ORDER BY w.step")
        result = self.cur.fetchall()
        self.close()
        return result
    
    def list_workflow_by_kernel(self, kernel_id):
        self.cur.execute("SELECT k.ref AS kernel, w.* FROM workflow as w INNER JOIN kernels as k ON w.kernel_id = k.id WHERE w.kernel_id=%s ORDER BY w.step", (kernel_id,))
        result = self.cur.fetchall()
        self.close()
        return result
    
    def insert_workflow(self, kernel_id, workflow):
        # check kernel_id
        self.cur.execute("SELECT id FROM kernels WHERE id = %s", (kernel_id,))
        result = self.cur.fetchall()
        if result and len(result) > 0:
            # build data with kernel_id
            data = []
            for task in workflow:
                step = task['Step']
                task_name = task['Task Name']
                column_names = task['Column Names']
                method = task['Method']
                reason = task['Reason']
                data.append((kernel_id, step, task_name, column_names, method, reason))
            # insert code
            self.cur.executemany("INSERT INTO workflow(kernel_id, step, task_name, column_names, method, reason, version) VALUES (%s, %s, %s, %s, %s, %s, 0)", data)
            self.con.commit()
            self.close()
            return self.cur.rowcount
        else:
            print('Kernel {} does not exist!'.format(kernel_id))
            return 0

    def insert_or_update_task(self, kernel_id, version, task):
        # check task existed
        step = task['Step']
        self.cur.execute("SELECT COUNT(*) FROM workflow WHERE kernel_id=%s AND version=%s AND step=%s", (kernel_id, version, step))
        result = self.cur.fetchall()
        count = result[0][0]
        if count > 0:
            # update
            step = task['Step']
            task_name = task['Task Name']
            column_names = task['Column Names']
            method = task['Method']
            reason = task['Reason']
            # update task
            self.cur.execute("UPDATE workflow SET task_name=%s, column_names=%s, method=%s, reason=%s WHERE kernel_id=%s AND version=%s AND step=%s", (task_name, column_names, method, reason, kernel_id, version, step))
            self.con.commit()
            self.close()
            return self.cur.rowcount
        else:
            # insert
            step = task['Step']
            task_name = task['Task Name']
            column_names = task['Column Names']
            method = task['Method']
            reason = task['Reason']
            # insert new task with version
            self.cur.execute("INSERT INTO workflow(kernel_id, step, task_name, column_names, method, reason, version) VALUES (%s, %s, %s, %s, %s, %s, %s)", (kernel_id, step, task_name, column_names, method, reason, version))
            self.con.commit()
            self.close()
            return self.cur.rowcount 
    
    """
    for generation table (workflow generation)
    """
    def list_gen(self):
        self.cur.execute("SELECT k.ref AS kernel, g.* FROM generation as g INNER JOIN kernels as k ON g.kernel_id = k.id ORDER BY g.version, g.step")
        result = self.cur.fetchall()
        self.close()
        return result
    
    def list_gen_by_kernel(self, kernel_id):
        self.cur.execute("SELECT k.ref AS kernel, g.* FROM generation as g INNER JOIN kernels as k ON g.kernel_id = k.id WHERE g.kernel_id=%s ORDER BY g.version, g.step", (kernel_id,))
        result = self.cur.fetchall()
        self.close()
        return result
    
    def insert_or_update_gen(self, kernel_id, version, gen_data):
        # check gen existed
        prompt_id = gen_data['prompt_id']
        self.cur.execute("SELECT COUNT(*) FROM generation WHERE kernel_id=%s AND version=%s AND step=%s", (kernel_id, version, prompt_id))
        result = self.cur.fetchall()
        count = result[0][0]
        if count > 0:
            prompt_id = gen_data['prompt_id']
            prompt = gen_data['prompt']
            code = gen_data['code']
            output = gen_data['output']
            # update gen
            self.cur.execute("UPDATE generation SET prompt=%s, code=%s, output=%s WHERE kernel_id=%s AND version=%s AND step=%s", (prompt, code, output, kernel_id, version, prompt_id))
            self.con.commit()
            self.close()
            return self.cur.rowcount
        else:
            prompt_id = gen_data['prompt_id']
            prompt = gen_data['prompt']
            code = gen_data['code']
            output = gen_data['output']
            # insert gen
            self.cur.execute("INSERT INTO generation(kernel_id, version, step, prompt, code, output) VALUES (%s, %s, %s, %s, %s, %s)", (kernel_id, version, prompt_id, prompt, code, output))
            self.con.commit()
            self.close()
            return self.cur.rowcount

    