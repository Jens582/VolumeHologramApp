
from dash import Input, Output, callback, dcc
from dash.exceptions import PreventUpdate
import matplotlib
import json
import io
import zipfile
import base64

from source.data_container import DataContainer
from source.store_controller import StoreController
from source.hoe_logger import logger

import layouts.store_layout as spram


def register_store_callbacks(store_controller: StoreController):
    @callback(
        Output(spram.id_download, "data"),
        Input(spram.id_button_download, 'n_clicks'),
        prevent_initial_call=True,        
    )
    def button_click_download(n_clicks):
        json_data_list = store_controller.get_json_data()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            for item in json_data_list.items():
                zip_file.writestr(item[0]+".json", item[1])
        
        buffer.seek(0)
        return dcc.send_bytes(buffer.getvalue(), "hoe_simulations.zip")


    @callback(
        Output(spram.id_table, "rowData", allow_duplicate=True),
        Input(spram.id_upload, "contents"),
        prevent_initial_call=True,            
    )
    def button_click_upload(contents):
        if not contents:
            logger.warning("No selections")
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
            logger.warning("Couldn't read data")
            raise PreventUpdate()

        rowdata = store_controller.get_simulations_as_row_data()
        store_controller.new_data = True
        return rowdata
    

    @callback(
        Output(spram.id_table, "rowData", allow_duplicate=True),
        Input(spram.id_button_delete, "n_clicks"),
        prevent_initial_call=True,            
    )
    def button_click_delete(n_click):
        store_controller.delete_selected()
        rowdata = store_controller.get_simulations_as_row_data()
        store_controller.new_data = True
        return rowdata
    
    @callback(
        Output(spram.id_table, "rowData" , allow_duplicate=True),
        Input(spram.id_table, "cellValueChanged"),
        Input(spram.id_table, "rowData"),
        prevent_initial_call=True,            
    )
    def color_change(change, rowdata):
        if change is not None:
            data = change[0]["data"]
            key = data["Simulation"]
            color = data["Color"]
            if color in matplotlib.colors.CSS4_COLORS:
                store_controller.simulations[key].color = color
            else:
                rowdata = store_controller.get_simulations_as_row_data()
            store_controller.new_data = True
        return rowdata

    @callback(
        Output(spram.id_text_area, "value"),
        Input(spram.id_table, "selectedRows"),
        prevent_initial_call=True,            
    )
    def selections_change(selected_rows):
        selections = [line["Simulation"] for line in selected_rows]
        store_controller.selected_simulation = selections
        store_controller.new_data = True
        
        if len(selections)==0:
            text = "No simulation selected"
        else:            
            first = selections[0]
            text = "Parameter of simulation "+first+":\n"
            text += store_controller.simulations[first].parameter_text

        return text
    
