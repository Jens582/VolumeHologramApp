from dash import Input, Output, State, callback, callback_context
from source.parameter_controller import ParameterControl
import layouts.parameter_layout as pram
from source.manager_controller import MangerController
import layouts.app_layout as apram
from dash.exceptions import PreventUpdate 

def register_parameter_callbacks(manager_controller: MangerController):
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
            ],
            [          
                State(pram.id_table, "rowData"),
                State(pram.id_start, "value"),
                State(pram.id_end, "value"),
                State(pram.id_steps, "value"),

                State(pram.id_label_start, "children"),
                State(pram.id_label_end, "children"),
                State(pram.id_label_steps, "children"),

                Input(pram.id_combobox, 'options'),
                Input(pram.id_combobox, 'value'),
                State(apram.id_id_store, "data"), 

                Input(pram.id_table, "cellValueChanged"),            

                Input(pram.id_start, "n_submit"),
                Input(pram.id_start, "n_blur"),
                Input(pram.id_end, "n_submit"),
                Input(pram.id_end, "n_blur"),
                Input(pram.id_steps, "n_submit"),
                Input(pram.id_steps, "n_blur"),                
            ],
            prevent_initial_call=True,
        )
        def update_parameter_controller(*inputs):
            inputs = [value for value in inputs]
            i_rowdata = 0
            i_start = 1
            i_end = 2
            i_steps = 3
            i_label_start = 4
            i_label_end = 5
            i_label_steps = 6
            i_combobox_options = 7
            i_combobox_value = 8
            i_id = 9
            i_only_trigger = 9

            id = inputs[i_id]                        
            app_controller = manager_controller.get_app_controller(id)
            if app_controller is None:
                raise PreventUpdate()
            parameter_control = app_controller.parameter_control

        

            trigger = callback_context.triggered[0]["prop_id"] 
           
            # Combobox value change
            if trigger in [pram.id_combobox+'.value']:
                parameter_control.current_variable = inputs[i_combobox_value]
                start, end, steps = parameter_control.get_variable_range(inputs[i_combobox_value])
                inputs[i_start] = start
                inputs[i_end] = end
                inputs[i_steps] = steps
                start_label, end_label, steps_label = parameter_control.get_variable_labels(inputs[i_combobox_value])
                inputs[i_label_start] = start_label
                inputs[i_label_end] = end_label
                inputs[i_label_steps] = steps_label
                
            #Variable value change
            if trigger in [pram.id_start+'.n_submit', pram.id_end+".n_submit",pram.id_steps+".n_submit",
                           pram.id_start+'.n_blur', pram.id_end+".n_blur",pram.id_steps+".n_blur"]:
                start = inputs[i_start]                
                end = inputs[i_end]                
                steps = inputs[i_steps]                
                parameter_control.set_variable_range(inputs[i_combobox_value], start, end, steps)
                start, end, steps = parameter_control.get_variable_range(inputs[i_combobox_value])
                inputs[i_start] = start
                inputs[i_end] = end
                inputs[i_steps] = steps
                
            #Parameter change
            if trigger in [pram.id_table+".cellValueChanged", pram.id_combobox+'.value']:
                rowdata = inputs[i_rowdata]
                parameter_control.set_parameter_with_row_data_from_AgGrid(rowdata)                                
                rowdata = parameter_control.get_parameters_as_row_data_for_AgGrid()                
                inputs[i_rowdata] = rowdata
            
            
            return inputs[:i_only_trigger]
        

