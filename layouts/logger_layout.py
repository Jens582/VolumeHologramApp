from dash import dcc, html

id_logger = "logger_area"
id_button_clean = "logger_clean"


_text_area = dcc.Textarea(                
                id=id_logger,
                className="logger_text_area",
                value="",
)

_button_clean = html.Button(
                    id=id_button_clean,
                    className="logger_button_clean",
                    children=[
                        "Clean"
                    ]
                )

layout_logger = html.Div(
                    className="app_middle_bottom_right",                            
                    children=[
                        _button_clean,
                        _text_area
                    ]
                )