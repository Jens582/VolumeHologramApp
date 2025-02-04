from dash import html, dcc  
import dash_ag_grid as dag

id_table = "store_table"
id_button_upload = "store_button_upload"
id_button_download = "store_button_download"
id_button_delete = "store_button_delete"
id_download = "store_download"
id_upload = "store_upload"
id_text_area = "store_text_area"

columnDefs = list()
columnDefs.append({ 'field': 'Simulation', "cellStyle":{'fontSize':"100%"}, "flex":3 })
columnDefs.append({ 'field': 'Color', "editable": True, "cellStyle":{'fontSize':"100%"}, 'cellDataType': 'text', "flex":2  })
        
    
_table = dag.AgGrid(
            id = id_table,
            className="ag-theme-alpine",         
            columnDefs = columnDefs,
            rowData=list(),           
            dashGridOptions={
                "undoRedoCellEditingLimit": 20,
                "editType": "fullRow",
                "domLayout": "autoHeight",
                "rowSelection": "multiple",
            }
        )

_text_area = dcc.Textarea(
                id=id_text_area,
                className="store_text_area",
                value="",
)


layout_store = html.Div(   
                    children=[
                        html.Div(
                            className="app_left",
                            children=[
                                html.Button(
                                    id=id_button_download,
                                    className="store_button",
                                    children=[
                                        "Download"
                                    ]
                                ),
                                dcc.Upload(
                                    id = id_upload,
                                    className="store_button",
                                    children=[
                                        html.Button(
                                            id=id_button_upload,
                                            className="store_button",
                                            children=[
                                                "Upload"
                                            ]
                                        ),
                                    ]
                                ), 
                                html.Button(
                                    id=id_button_delete,
                                    className="store_button",
                                    children=[
                                        "Delete"
                                    ]
                                ),
                                _text_area,
                                _table,
                                dcc.Download(id=id_download)
                            ])
                        ],
    )


