from dash import Input, Output, State, callback, callback_context

from callbacks.parameter_callbacks import register_parameter_callbacks
from callbacks.store_callbacks import register_store_callbacks
from callbacks.logger_callbacks import register_logger_callbacks

from source.app_controller import AppController
from source.display_controller import build_graph
from source.hoe_logger import log_queue, logger

import layouts.controller_layout as cpram
import layouts.display_layout as dpram
import layouts.app_layout as apram
import layouts.store_layout as spram
import layouts.logger_layout as lpram


import threading

def register_callbacks(app_controller: AppController):
    register_controller_callbacks(app_controller)
    register_parameter_callbacks(app_controller.parameter_control)
    register_store_callbacks(app_controller.store_controller)
    register_logger_callbacks()



def register_controller_callbacks(app_controller: AppController):
    
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

        trigger = callback_context.triggered[0]["prop_id"] 
        
        if trigger in [lpram.id_button_clean +".n_clicks"]:
            inputs[i_logger] = ""
        
        log_message = inputs[i_logger]
        log_message = add_logs(log_message)
        inputs[i_logger] = log_message

        ask_for_plot_data = False
        if trigger in [cpram.id_checkboxes + '.value', cpram.id_harmonic + '.value',]:
            ask_for_plot_data = True

        add_Rs, add_Rp, add_Ts, add_tp, add_es, add_ep = selected_to_bool(inputs[i_checkboxes])
        harmonic = inputs[i_harmonic]
        data  = app_controller.get_updated_plotting_data_and_status(add_Rs, add_Rp, add_Ts, add_tp, add_es, add_ep, harmonic, 0, ask_for_plot_data)        
        
        if data is None:
            logger.debug("Data locked")
            return inputs
        
        is_running, progress, plot_data = data

        if is_running:
            inputs[i_start_stop] = "Stop"
        else:
            inputs[i_start_stop] = "Start"
        
        inputs[i_progress] = progress       
        
        figure = inputs[i_graph]
        figure = build_graph(figure, plot_data)
        inputs[i_graph] = figure

        return inputs
    
    
    @callback(
        Output(cpram.id_start_stop, "children", allow_duplicate=True),
        Input(cpram.id_start_stop, 'n_clicks'),
        prevent_initial_call=True,            
    )
    def button_click_start_stop(n_click):    
        thread = threading.Thread(target=app_controller.start_stop_calculation, daemon=True)
        thread.start()
        return "Wait - Preparing"


    @callback(
        [
            Output(spram.id_table, "rowData", allow_duplicate=True),
        ],
        Input(cpram.id_transfer, 'n_clicks'),
        State(cpram.id_name, 'value'),
        prevent_initial_call=True,            
    )
    def button_click_transfer(n_click, name):
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

def add_logs(old_message):
    new_logs = []
    while not log_queue.empty():
        record = log_queue.get()
        new_logs.append(record.getMessage())
    
    if len(new_logs) == 0:
        return old_message

    updated_logs = (old_message or "") 
    updated_logs += "".join(new_logs)+ "\n"
    return updated_logs
