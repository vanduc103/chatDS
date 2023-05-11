BLOCK_PROMPT = false
BLOCK_REFRESH = false
REMOVE_ALL = false
prompt_increment = 0
current_selected = ""
prompts = {}
define([
    'base/js/namespace',
    'jquery',
    'base/js/events',
    'base/js/dialog'
], function (Jupyter, $, events, dialog) {
    var base_url = "http://147.47.236.89:39500/api/v1"
    console.log("loading ChatDS")
    // initial content
    var all_cells = Jupyter.notebook.get_cells()
    var mx = 0
    for (var i = 0; i < all_cells.length; i++) {
        if (all_cells[i].cell_type != 'markdown') continue
        var content = all_cells[i].get_text()
        content = content.trim()
        content = content.split(" ")
        if (content.length > 1) {
            var new_mx = parseInt(content[2])
            if (new_mx && mx < new_mx) mx = new_mx
        } 
    }
    prompt_increment = mx
    var temp = localStorage.getItem("PROMPT_ID_MAP")
    if (temp)
        prompts = JSON.parse(temp)
    console.log(prompts)

    var get_last_cell_index = function () {
        var last_cell_index = Jupyter.notebook.get_cells().length - 1
        if (last_cell_index <= 0)
            last_cell_index = 1
        return last_cell_index
    }
    var removeAll = function () {
        var cells = Jupyter.notebook.get_cells()
        REMOVE_ALL = true
        for (var i = 0; i < cells.length; i++) {
            Jupyter.notebook.delete_cell(cells[i].index)
        }
    }
    var initWorkingSpace = function (content) {
        for (var key in localStorage) {
            if (key.startsWith("current_text")) {
                localStorage.removeItem(key)
            }
        }
        removeAll()
        var last_cell_index = get_last_cell_index()
        if (!content) return
        for (var i = 0; i < content.length; i++) {
            var cell = content[i]
            prompt_increment = cell['prompt_id']
            var prompt_id = prompt_increment + 1
            var prompt = "## Prompt " + prompt_id + ": " + cell['prompt']
            var prompt_code = cell['code']
            insert_prompt_cell(prompt, last_cell_index, prompt_increment)
            last_cell_index += 1
            insert_code_cell(prompt_code, last_cell_index)
            last_cell_index += 1
        }
        REMOVE_ALL = false
        Jupyter.notebook.get_cells()[0].select()
        prompt_increment += 1
    }
    var load_init_prompt = function () {
        $.ajax({
            url: base_url + '/prompt_init',
            method: 'POST',
        }).done(initWorkingSpace)
    }

    var insert_prompt_cell = function (msg, new_cell_index, prompt_id) {
        var all_cells = Jupyter.notebook.get_cells()
        for (var i = 0; i < all_cells.length; i++) { 
            all_cells[i].unselect()
        }
        if (!msg) {
            msg = "## Prompt " + (prompt_id + 1)
        }
        var notebook = Jupyter.notebook
        var new_cell = notebook.insert_cell_below('markdown', new_cell_index)
        new_cell.set_text(msg)
        new_cell.execute()
        new_cell.select()
        new_cell.element[0].scrollIntoViewIfNeeded()
        new_cell.unselect()
        localStorage.setItem('NEW_PROMPT_CELL', new_cell.cell_id)
        prompts[new_cell.cell_id] = prompt_id
        localStorage.setItem("PROMPT_ID_MAP", JSON.stringify(prompts))
    }
    
    var insert_code_cell = function (content, index) {
        var new_cell = Jupyter.notebook.insert_cell_below('code', index)
        new_cell.set_text(content)
        new_cell.execute()
        new_cell.select()
        new_cell.element[0].scrollIntoViewIfNeeded()
        new_cell.unselect()
        // Jupyter.notebook.execute_cell_and_select_below()
    }
    // Add Toolbar button
    var addPromptButton = function () {
        Jupyter.toolbar.add_buttons_group([
            Jupyter.keyboard_manager.actions.register({
                'help': 'Add new prompt cell',
                'icon': 'fa-terminal',
                'handler': function () {
                    if (!BLOCK_PROMPT) {
                        BLOCK_PROMPT = true
                        var last_cell_index = get_last_cell_index()
                        insert_prompt_cell("", last_cell_index, prompt_increment)
                        prompt_increment += 1
                        setTimeout(function() {
                            BLOCK_PROMPT = false
                        }, 500)
                    } else {
                        alert ("You click too fast!")
                    }
                }
            }, 'addplanetjupyter-cell', 'Add a New Prompt')
        ])
    }

    var addResetButton = function () {
        Jupyter.toolbar.add_buttons_group([
            Jupyter.keyboard_manager.actions.register({
                'help': 'Reload Notebook',
                'icon': 'fa-refresh',
                'handler': function () {
                    console.log(BLOCK_REFRESH)
                    if (!BLOCK_REFRESH) {
                        BLOCK_REFRESH = true
                        load_init_prompt()
                        setTimeout(function() {
                            BLOCK_REFRESH = false
                        }, 500)
                    } else {
                        alert ("You click too fast!")
                    }
                }
            }, 'addplanetjupyter-cell', 'Reload Notebook')
        ])
    }
    
    var verifyPromptCell = function(data) {
        var cell_type = data['cell']['cell_type']
        var content = data.cell.get_text()
        var cell_code = content.substr(0, 9).toLowerCase()
        return cell_type == 'markdown' && cell_code == '## prompt'
    }
    // check if a cell is modified
    var selectCell = function(cell) {
        var content = cell.get_text()
        var cell_id = cell.cell_id
        current_selected = cell_id
        localStorage.setItem('current_text' + cell_id, content)
    }
    events.on('select.Cell', function(event, data) {
        selectCell(data.cell)
    })

    events.on('edit_mode.Cell', function(event, data) {
        if(verifyPromptCell(data)) {
            localStorage.setItem("EVEN_MP", "True")
        }            
    })

    $('[data-jupyter-action="jupyter-notebook:cut-cell"]').on('click', function() {
        if (!current_selected) {
            var focus_cell = Jupyter.notebook.get_cell(0)
            selectCell(focus_cell)
        }
    })

    // remove code cell corresponding to a markdown cell_index
    var remove_code_cell = function(cell_index) {
        var code_cell = Jupyter.notebook.get_cell(cell_index+1)
        if (code_cell.cell_type == 'code') 
            Jupyter.notebook.delete_cell(cell_index+1)
    }

    var submitPrompt = function(cell_index, prompt_id, prompt) {
        prompt = prompt.replace("## Prompt","")
        var content = 
        {
            'prompt': {
                'prompt_id': prompt_id,
                'prompt': prompt
            }
        }
        content = JSON.stringify(content)
        $.ajax({
            url: base_url + '/code_generate',
            method: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: content
        }).done(function(res) {
            if (!res) return
            var data = res[0]
            remove_code_cell(cell_index)
            insert_code_cell(data['code'], cell_index)
        })
    }

    events.on('delete.Cell', function(event, data) {
        if(REMOVE_ALL) return
        var cell_id = data.cell.cell_id
        var cell_index = data.index
        var length = Jupyter.notebook.get_cells().length
        if (cell_index < length)
             cell_index -= 1
        else cell_index = length
        var prev_text = localStorage.getItem('current_text' + cell_id)
        localStorage.removeItem('current_text' + cell_id)
        current_selected = ""
        if (verifyPromptCell(data)) {
            dialog.modal({
                title: 'Confirm Action',
                body: "If you modified this prompt, all following code will be affected. Are you sure you want to perform this action?",
                buttons: {
                    'Cancel' : {
                        'class': 'btn-danger',
                        'click': function() {
                            insert_prompt_cell(prev_text, cell_index)
                        }
                    },
                    'OK': {
                        'class': 'btn-primary',
                        'click': function() {
                            remove_code_cell(cell_in_index)
                        }
                    }
                }
        
            })
        }
    })

    events.on('rendered.MarkdownCell', function(event, data) {
        var cell_id = data.cell.cell_id
        var content = data.cell.get_text().trim()
        if (!prompts.hasOwnProperty(cell_id)) return
        var prev_text = localStorage.getItem('current_text' + cell_id)
        if (prev_text) {
            prev_text = prev_text.trim()
            if (prev_text == content) return
            var cells = Jupyter.notebook.get_cells()
            var cell_index = 0
            for (var i = 0; i < cells.length; i++) {
                if (cells[i].cell_id != cell_id)
                    continue
                cell_index = i
                break
            }
            submitPrompt(cell_index, prompts[cell_id], content)
        }
        /*
        setTimeout(function() {
            var even2 = localStorage.getItem("NEW_PROMPT_CELL")
            if (even2 != cell_id) {
                dialog.modal({
                    title: 'Confirm Action',
                    body: "If you modified this prompt, all following code will be affected. Are you sure you want to perform this action?",
                    buttons: {
                        'Cancel' : {},
                        'OK': {
                            'class': 'btn-primary',
                            'click': function() {
                                submitPrompt(0, content)
                            }
                        }
                    }
                })
            }
            setTimeout(function() {
                localStorage.removeItem('NEW_PROMPT_CELL')
            }, 100)
        }, 100)
        */
        
    })

    events.on('execute.CodeCell', function(event, data) {
        var cell_id = data.cell.cell_id
    })


    // Run on start
    function load_ipython_extension() {
        addPromptButton()
        addResetButton()
    }
    return {
        load_ipython_extension: load_ipython_extension
    }
})