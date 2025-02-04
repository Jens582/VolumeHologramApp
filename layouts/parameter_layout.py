import dash_ag_grid as dag
from dash import html, dcc  

id_table = "pram_table"
id_start = "pram_start"
id_end = "parm_end"
id_steps = "pram_steps"

id_label_start = "pram_label_start"
id_label_end = "pram_label_end"
id_label_steps = "pram_label_steps"

id_combobox = "pram_combobox"


columnDefs = list()
columnDefs.append({ 'field': 'Parameter', "cellStyle":{'fontSize':"100%"}, "flex":3 })
columnDefs.append({ 'field': 'Value', "editable": True, "cellStyle":{'fontSize':"100%"}, 'cellDataType': 'text', "flex":2  })
        
_variable_control = html.Div(
                        className="variable_control",
                        children=[
                            html.Div('Variable (X-Axis)', className="variable_control_title"),
                            html.Div(
                                className="variable_control_combobox",
                                children=[
                                    dcc.Dropdown(
                                    id=id_combobox,                                    
                                    clearable=False,
                                    )                                
                                ]
                            ),
                            html.Div('Thickness', id=id_label_start, className="variable_control_label"),
                            dcc.Input(
                                id=id_start,
                                className="variable_control_input",
                                type='number',
                                value = 0,
                                ),
                            html.Div('End', id=id_label_end, className="variable_control_label"),
                            dcc.Input(
                                id=id_end,
                                className="variable_control_input",
                                type='number',
                                value = 100,
                                ),
                            html.Div('Steps', id= id_label_steps, className="variable_control_label"),
                            dcc.Input(
                                id=id_steps,
                                className="variable_control_input",
                                type='number',
                                value = 100,
                                ),
                        ]
                    )

    
_table = dag.AgGrid(
            id=id_table,
            className="ag-theme-alpine",
            columnDefs = columnDefs,
            rowData=list(),                       
            dashGridOptions={
                "undoRedoCellEditingLimit": 20,
                "editType": "fullRow",
                "domLayout": "autoHeight",                                
            }
        )

layout_parameter =  html.Div(
                        className="app_right",   
                        children=[
                            _variable_control,
                            _table,                                                             
                        ]
                    )







