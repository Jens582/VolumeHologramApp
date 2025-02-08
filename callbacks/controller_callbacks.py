from dash import Input, Output, State, callback, callback_context
from dash.exceptions import PreventUpdate 
import uuid

from callbacks.parameter_callbacks import register_parameter_callbacks
from callbacks.store_callbacks import register_store_callbacks
from callbacks.logger_callbacks import register_logger_callbacks

from source.app_controller import AppController
from source.manager_controller import MangerController
from source.display_controller import build_graph, filter_and_get_pram_variables, build_dummy_graph
from source.parameter_controller import ParameterControl

import layouts.controller_layout as cpram
import layouts.display_layout as dpram
import layouts.app_layout as apram
import layouts.store_layout as spram
import layouts.logger_layout as lpram
import layouts.parameter_layout as pram


import threading

def register_callbacks(manager_controller: MangerController):
    register_initial_callback(manager_controller)
    register_controller_callbacks(manager_controller)
    register_parameter_callbacks(manager_controller)
    register_store_callbacks(manager_controller)
    register_logger_callbacks(manager_controller)


def register_initial_callback(manager_controller: MangerController):
    @callback(
            [
                Output(pram.id_table, "rowData", allow_duplicate=True),
                Output(pram.id_start, "value", allow_duplicate=True),
                Output(pram.id_end, "value", allow_duplicate=True),
                Output(pram.id_steps, "value", allow_duplicate=True),

                Output(pram.id_label_start, "children", allow_duplicate=True),
                Output(pram.id_label_end, "children", allow_duplicate=True),
                Output(pram.id_label_steps, "children", allow_duplicate=True),

                Output(pram.id_combobox, 'options', allow_duplicate=True),
                Output(pram.id_combobox, 'value', allow_duplicate=True),
                Output(dpram.id_graph, 'figure', allow_duplicate=True),
                Output(apram.id_id_store, "data", allow_duplicate=True),                 
            ],
            [
                Input(apram.id_initial, "n_intervals"),                 
            ],
            prevent_initial_call=True,
                          
    )
    def initial(n_intervall):       
        id = str(uuid.uuid4())        
        manager_controller.create_controller(id)        
        app_controller = manager_controller.get_app_controller(id)
        values = get_start_values(app_controller.parameter_control, id)        
        return values

def register_controller_callbacks(manager_controller: MangerController):
   
    @callback(
        [   
            Output(apram.id_interval, "n_intervals"),
            Output(cpram.id_checkboxes, 'value'),
            Output(cpram.id_harmonic, 'value'),
            Output(lpram.id_button_clean, 'n_clicks'),                
            Output(dpram.id_graph, "figure"),
            Output(lpram.id_logger, "value"),
            Output(cpram.id_start_stop, "children"),
            Output(cpram.id_progress, "value"),             
        ],
        [
            Input(apram.id_interval, "n_intervals"),
            Input(cpram.id_checkboxes, 'value'),
            Input(cpram.id_harmonic, 'value'),
            Input(lpram.id_button_clean, 'n_clicks'),                
            State(dpram.id_graph, "figure"),
            State(lpram.id_logger, "value"),
            State(cpram.id_start_stop, "children"),
            State(cpram.id_progress, "value"),
            State(apram.id_id_store, "data")                    
        ]        
    )
    def interval_update(*inputs: tuple):
        inputs = [value for value in inputs]
        i_interval = 0
        i_checkboxes = 1
        i_harmonic = 2
        i_button_clean = 3
        i_graph = 4
        i_logger = 5
        i_start_stop = 6
        i_progress = 7
        i_id = 8

        id = inputs[i_id]
        app_controller = manager_controller.get_app_controller(id)
        if id is None:
            raise PreventUpdate()
        
        if app_controller is None:
            inputs[i_graph] = build_dummy_graph("Session expired, please refresh the site!")
            return inputs[:-1]
                    
        trigger = callback_context.triggered[0]["prop_id"] 
        
        if trigger in [lpram.id_button_clean +".n_clicks"]:
            inputs[i_logger] = ""
        
        log_message = inputs[i_logger]
        log_message = add_logs(log_message, app_controller)
        inputs[i_logger] = log_message

        ask_for_plot_data = False
        if trigger in [cpram.id_checkboxes + '.value', cpram.id_harmonic + '.value',]:
            ask_for_plot_data = True

        add_Rs, add_Rp, add_Ts, add_tp, add_es, add_ep = selected_to_bool(inputs[i_checkboxes])
        harmonic = inputs[i_harmonic]
        data  = app_controller.get_updated_plotting_data_and_status(add_Rs, add_Rp, add_Ts, add_tp, add_es, add_ep, harmonic, 0, ask_for_plot_data)        
        
        if data is None:
            app_controller.logger.debug("Data locked")
            return inputs[:-1]
        
        is_running, progress, plot_data = data
                
        if is_running:
            inputs[i_start_stop] = "Stop"
        else:
            inputs[i_start_stop] = "Start"
        
        inputs[i_progress] = progress       
        
        figure = inputs[i_graph]
        
        pram_variables = filter_and_get_pram_variables(plot_data)
        
        if len(pram_variables) == 0:
            pram_variable = "Variable"
        else:
            pram_variable = pram_variables[0]

        if not all(item == pram_variable for item in pram_variables):
            app_controller.logger.warning("Different variables in graph")
    
        
        figure = build_graph(figure, plot_data, pram_variable)
        inputs[i_graph] = figure
        
        return inputs[:-1]
    
    
    @callback(
        [
            Output(cpram.id_start_stop, "children", allow_duplicate=True),            
        ],
        [
            Input(cpram.id_start_stop, 'n_clicks'),
            State(apram.id_id_store, "data")
        ],
        prevent_initial_call=True,            
    )
    def button_click_start_stop(n_click, id):  
        app_controller = manager_controller.get_app_controller(id)
        if app_controller is None:
            raise PreventUpdate()
        
        thread = threading.Thread(target=app_controller.start_stop_calculation, daemon=True)
        thread.start()
        return ["Wait - Preparing"]


    @callback(
        [
            Output(spram.id_table, "rowData", allow_duplicate=True),            
        ],
        [
            Input(cpram.id_transfer, 'n_clicks'),
            State(cpram.id_name, 'value'),
            State(apram.id_id_store, "data")
        ],        
        prevent_initial_call=True,            
    )
    def button_click_transfer(n_click, name, id):       
        app_controller = manager_controller.get_app_controller(id)
        if app_controller is None:
            raise PreventUpdate()
        
        app_controller.transfer_simulation_to_store(name) 
        rowdata = app_controller.store_controller.get_simulations_as_row_data()
        app_controller._new_data = True
        return [rowdata]
    
    
def selected_to_bool(selected):
    check = dict()
    check["Rs"] = False
    check["Rp"] = False
    check["Tp"] = False
    check["Ts"] = False
    check["Es"] = False
    check["Ep"] = False
    for i in selected:
        check[i] = True
    srs = check["Rs"]
    srp = check["Rp"]
    sts = check["Ts"]
    stp = check["Tp"]
    ses = check["Es"]
    sep = check["Ep"]
    return srs, srp, sts, stp, ses, sep

def add_logs(old_message, app_controller: AppController):
    new_logs = []
    while not app_controller.log_queue.empty():
        record = app_controller.log_queue.get()
        new_logs.append(record.getMessage())
    
    if len(new_logs) == 0:
        return old_message

    updated_logs = (old_message or "") 
    updated_logs += "".join(new_logs)+ "\n"
    return updated_logs


def get_start_values(parameter_control: ParameterControl, id :str):        
    i_rowdata = 0
    i_start = 1
    i_end = 2
    i_steps = 3
    i_label_start = 4
    i_label_end = 5
    i_label_steps = 6
    i_combobox_options = 7
    i_combobox_value = 8
    i_graph = 9
    i_id = 10
    i_only_trigger = 11

    current_variable = parameter_control.current_variable
    options=[{'label': val, 'value': val} for val in parameter_control.get_list_of_variable_parameters()]    
    start_label, end_label, steps_label = parameter_control.get_variable_labels(current_variable)
    rowdata = parameter_control.get_parameters_as_row_data_for_AgGrid()    
    start, end, steps = parameter_control.get_variable_range(current_variable)
    
    start_values = i_only_trigger*[None]
    start_values[i_rowdata] = rowdata
    start_values[i_start] = start
    start_values[i_end] = end
    start_values[i_steps] = steps
    start_values[i_label_start] = start_label
    start_values[i_label_end] = end_label
    start_values[i_label_steps] = steps_label
    start_values[i_combobox_options] = options
    start_values[i_combobox_value] = current_variable    
    start_values[i_graph] = build_dummy_graph("Press start button to simulate.")
    start_values[i_id] = id

    return start_values