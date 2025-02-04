from dash import html, dcc

from layouts.parameter_layout import layout_parameter
from layouts.store_layout import layout_store
from layouts.display_layout import layout_display
from layouts.controller_layout import layout_controller
from layouts.logger_layout import layout_logger

id_interval = "app_update_interval"
id_dummy_store ="app_dummy_store"


_middle_bottom_panel = html.Div(
                        className="app_middle_bottom",
                        children=[
                            layout_controller,
                            layout_logger
                        ]
                    )

_middle_panel = html.Div(
                    className="app_middle",
                    children=[
                        layout_display,
                        _middle_bottom_panel
                    ]
            )


layout_app = html.Div(
                className="app_layout",
                children=[
                    layout_store,
                    _middle_panel,
                    layout_parameter,
                    dcc.Interval(id=id_interval, interval=1000, n_intervals=0),
                    dcc.Store(id=id_dummy_store)
                ]
            )





