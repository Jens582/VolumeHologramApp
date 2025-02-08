
from dash import Input, Output, State, callback, dcc
from dash.exceptions import PreventUpdate
import matplotlib
import json
import io
import zipfile
import base64

from source.data_container import DataContainer
from source.store_controller import StoreController
from source.manager_controller import MangerController

import layouts.app_layout as apram
import layouts.store_layout as spram


def register_store_callbacks(manager_controller: MangerController):
    @callback(
        [
            Output(spram.id_download, "data"),            
        ],
        [
            Input(spram.id_button_download, 'n_clicks'),
            State(apram.id_id_store, "data")
        ],
        prevent_initial_call=True,        
    )
    def button_click_download(n_clicks, id):     
        app_controller = manager_controller.get_app_controller(id)
        if app_controller is None:
            raise PreventUpdate()
        store_controller = app_controller.store_controller        

        json_data_list = store_controller.get_json_data()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            for item in json_data_list.items():
                zip_file.writestr(item[0]+".json", item[1])
        
        buffer.seek(0)
        return [dcc.send_bytes(buffer.getvalue(), "hoe_simulations.zip")]


    @callback(
        [
            Output(spram.id_table, "rowData", allow_duplicate=True),            
        ],
        [
            Input(spram.id_upload, "contents"),
            State(apram.id_id_store, "data")
        ],
        prevent_initial_call=True,            
    )
    def button_click_upload(contents, id):              
        app_controller = manager_controller.get_app_controller(id)
        if app_controller is None:
            raise PreventUpdate()
        store_controller = app_controller.store_controller
        
        if not contents:
            app_controller.logger.warning("No selections")
            raise PreventUpdate()

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        try:
            with zipfile.ZipFile(io.BytesIO(decoded), "r") as zip_file:
                files = zip_file.namelist()
                for file in files:
                    if file.endswith(".json"):
                        with zip_file.open(file) as f:
                            data_dict = json.load(f)    
                            data = DataContainer.from_dict(data_dict)
                            name = file[:-5]
                            store_controller.add_simulation(name, data)
        except:
            app_controller.logger.warning("Couldn't read data")
            raise PreventUpdate()

        rowdata = store_controller.get_simulations_as_row_data()
        store_controller.new_data = True
        return [rowdata]
    

    @callback(
        [
            Output(spram.id_table, "rowData", allow_duplicate=True),        
        ],
        [
            Input(spram.id_button_delete, "n_clicks"),
            State(apram.id_id_store, "data")
        ],
        prevent_initial_call=True,            
    )
    def button_click_delete(n_click, id):
        app_controller = manager_controller.get_app_controller(id)
        if app_controller is None:
            raise PreventUpdate()
        store_controller = app_controller.store_controller

        
        store_controller.delete_selected()
        rowdata = store_controller.get_simulations_as_row_data()
        store_controller.new_data = True
        return [rowdata]
    
    @callback(
        [
            Output(spram.id_table, "rowData" , allow_duplicate=True),            
        ],
        [
            Input(spram.id_table, "cellValueChanged"),
            Input(spram.id_table, "rowData"),
            State(apram.id_id_store, "data")
        ],
        prevent_initial_call=True,            
    )
    def color_change(change, rowdata, id):
        app_controller = manager_controller.get_app_controller(id)
        if app_controller is None:
            raise PreventUpdate()
        store_controller = app_controller.store_controller

        if change is not None:
            data = change[0]["data"]
            key = data["Simulation"]
            color = data["Color"]
            if color in matplotlib.colors.CSS4_COLORS:
                store_controller.simulations[key].color = color
            else:
                rowdata = store_controller.get_simulations_as_row_data()
            store_controller.new_data = True
        return [rowdata]

    @callback(
        [
            Output(spram.id_text_area, "value"),
        ],
        [
            Input(spram.id_table, "selectedRows"),
            State(apram.id_id_store, "data")
        ],
        prevent_initial_call=True,            
    )
    def selections_change(selected_rows, id):
        app_controller = manager_controller.get_app_controller(id)
        if app_controller is None:
            raise PreventUpdate()
        store_controller = app_controller.store_controller
        

        
        selections = [line["Simulation"] for line in selected_rows]
        store_controller.selected_simulation = selections
        store_controller.new_data = True
        
        if len(selections)==0:
            text = "No simulation selected"
        else:            
            first = selections[0]
            text = "Parameter of simulation "+first+":\n"
            text += store_controller.simulations[first].parameter_text

        return [text]
    
