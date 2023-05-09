define([
    'base/js/namespace',
    'jquery',
    'base/js/events',
    'base/js/dialog'
], function (Jupyter, $, events, dialog) {
    
    console.log("loading ChatDS")
    var all_cells = Jupyter.notebook.get_cells();
    var mx = 0;
    for (var i = 0; i < all_cells.length; i++) {
        if (all_cells[i].cell_type != 'markdown') continue;
        var content = all_cells[i].get_text();
        content = content.trim();
        content = content.split(" ");
        if (content.length > 1) {
            var new_mx = parseInt(content[2])
            if (new_mx && mx < new_mx) mx = new_mx
        } 
    }
    localStorage.setItem("prompt_increment", mx);
    var insert_prompt_cell = function (msg, new_cell_index) {
        var all_cells = Jupyter.notebook.get_cells();
        for (var i = 0; i < all_cells.length; i++) { 
            all_cells[i].unselect();
        }
        if (!msg) {
            id = localStorage.getItem("prompt_increment");
            if (id === null) {
                id = 1;
            } else {
                id = parseInt(id);
                id += 1;
            }
            localStorage.setItem("prompt_increment", id);
            msg = "## Prompt " + id;
        }
        var notebook = Jupyter.notebook;
        var new_cell = notebook.insert_cell_below('markdown', new_cell_index);
        new_cell.set_text(msg);
        new_cell.execute();
        new_cell.select();
        new_cell.element[0].scrollIntoViewIfNeeded();
        new_cell.unselect();
        localStorage.setItem('NEW_PROMPT_CELL', new_cell.cell_id);
    };
    
    var insert_code_cell = function () {
        Jupyter.notebook.insert_cell_above('code');
        Jupyter.notebook.select_prev();
        Jupyter.notebook.execute_cell_and_select_below();
    };
    // Add Toolbar button
    var addPromptButton = function () {
        Jupyter.toolbar.add_buttons_group([
            Jupyter.keyboard_manager.actions.register({
                'help': 'Add new prompt cell',
                'icon': 'fa-terminal',
                'handler': function () {
                    if (localStorage.getItem("BLOCK_PROMPT") != 'True') {
                        localStorage.setItem("BLOCK_PROMPT", "True");
                        var last_cell_index = Jupyter.notebook.get_cells().length - 1;
                        insert_prompt_cell("", last_cell_index)
                        setTimeout(function() {
                            localStorage.removeItem("BLOCK_PROMPT")
                        }, 500)
                    } else {
                        alert ("You click too fast!")
                    }
                }
            }, 'addplanetjupyter-cell', 'Planet Jupyter')
        ])
        
        
    }
    
    var verifyPromptCell = function(data) {
        var cell_type = data['cell']['cell_type'];
        var content = data.cell.get_text()
        var cell_code = content.substr(0, 9).toLowerCase();
        return cell_type == 'markdown' && cell_code == '## prompt'
    }
    // check if a cell is modified
    var selectCell = function(cell) {
        var content = cell.get_text();
        var cell_id = cell.cell_id;
        localStorage.setItem("current_selected", cell_id)
        localStorage.setItem('current_text' + cell_id, content);
    }
    events.on('select.Cell', function(event, data) {
        selectCell(data.cell);
    });

    events.on('edit_mode.Cell', function(event, data) {
        if(verifyPromptCell(data)) {
            localStorage.setItem("EVEN_MP", "True")
        }            
    });

    $('[data-jupyter-action="jupyter-notebook:cut-cell"]').on('click', function() {
        if (!localStorage.getItem('current_selected')) {
            var focus_cell = Jupyter.notebook.get_cell(0);
            selectCell(focus_cell);
        }
    })

    events.on('delete.Cell', function(event, data) {
        var cell_id = data.cell.cell_id;
        var cell_index = data.index;
        var length = Jupyter.notebook.get_cells().length;
        if (cell_index < length)
             cell_index -= 1
        else cell_index = length;
        var prev_text = localStorage.getItem('current_text' + cell_id);
        localStorage.removeItem('current_text' + cell_id)
        localStorage.removeItem("current_selected")
        if (verifyPromptCell(data)) {
            dialog.modal({
                title: 'Confirm Action',
                body: "If you modified this prompt, all following code will be affected. Are you sure you want to perform this action?",
                buttons: {
                    'Cancel' : {
                        'class': 'btn-danger',
                        'click': function() {
                            insert_prompt_cell(prev_text, cell_index);
                        }
                    },
                    'OK': {
                        'class': 'btn-primary',
                        'click': function() {
                            var code_cell = Jupyter.notebook.get_cell(cell_index+1);
                            if (code_cell.cell_type == 'code') 
                                Jupyter.notebook.delete_cell(cell_index+1);
                        }
                    }
                }
        
            });
        }
    })

    events.on('rendered.MarkdownCell', function(event, data) {
        var cell_id = data.cell.cell_id;
        // setTimeout(function() {
        //     var even2 = localStorage.getItem("NEW_PROMPT_CELL")
        //     if (even2 != cell_id) {
        //         dialog.modal({
        //             title: 'Confirm Action',
        //             body: "If you modified this prompt, all following code will be affected. Are you sure you want to perform this action?",
        //             buttons: {
        //                 'Cancel' : {},
        //                 'OK': {
        //                     'class': 'btn-primary',
        //                     'click': function() {
                                
        //                     }
        //                 }
        //             }
        //         });
        //     }
        //     setTimeout(function() {
        //         localStorage.removeItem('NEW_PROMPT_CELL')
        //     }, 100)
        // }, 100)
        
    })

    events.on('execute.CodeCell', function(event, data) {
        var cell_id = data.cell.cell_id;
    })


    // Run on start
    function load_ipython_extension() {
        addPromptButton();
    }
    return {
        load_ipython_extension: load_ipython_extension
    };
});