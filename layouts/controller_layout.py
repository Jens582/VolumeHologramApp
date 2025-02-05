from dash import html, dcc  
import dash_bootstrap_components as dbc


id_start_stop = "controller_start_stop"
id_progress =  "controller_progress"
id_checkboxes = "controller_checkboxes"
id_harmonic = "controller_harmonic"
id_transfer = "controller_transfer"
id_name = "controller_name"


_button_start_stop = html.Button(    
                        id=id_start_stop,
                        className="controller_btn_start",
                        children = ["Start"]
                        )

_progress = dbc.Progress(
                    id = id_progress,
                    class_name="controller_progress",
                    value=75, 
                    striped=True, 
                    animated=True, max=100
            )

_checkboxes_ref_trn =   dcc.Checklist(
                            id=id_checkboxes,
                            className="controller_checkboxes",
                            labelStyle={'display': 'inline-block', 'margin-right': '2vw'},
                            options=[
                                {'label': 'Rs', 'value': 'Rs'},
                                {'label': 'Rp', 'value': 'Rp'},
                                {'label': 'Ts', 'value': 'Ts'},
                                {'label': 'Tp', 'value': 'Tp'},
                                {'label': 'Es', 'value': 'Es'},
                                {'label': 'Ep', 'value': 'Ep'},
                            ],
                            value=["Rs","Rp","Ts","Tp", "Es", "Ep"]
                        )


_label_harmonic = html.Div("Order:", className="controller_label_order")
_input_harmonic = dcc.Input(id=id_harmonic,className="controller_input_order",type='number', value=0, step=1)


_transfer_button = html.Button(id=id_transfer, className="controller_transfer_btn", children = ["To Store"])
_transfer_name = dcc.Input(id=id_name,className="controller_transfer_name",type='text', value="Name")

_link_read_me = html.A(className="controller_link",children=["README/Github"],target="_blank", href="https://github.com/" )

layout_controller = html.Div(
                className="app_middle_bottom_left",
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(_button_start_stop, width=6),
                            dbc.Col(_progress, width=6)
                        ]
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(_label_harmonic,width=2),
                            dbc.Col(_input_harmonic,width=2),
                            dbc.Col(_transfer_button,width=4),
                            dbc.Col(_transfer_name,width=4),                            
                        ]
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(_checkboxes_ref_trn, width=8),
                            dbc.Col(_link_read_me)
                            ]
                    )
                ]
            )

