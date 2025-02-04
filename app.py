from dash import Dash
import dash_bootstrap_components as dbc
from layouts.app_layout import layout_app
from callbacks.controller_callbacks import register_callbacks
from source.app_controller import AppController

if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])    
    app.layout = layout_app
    app_controller = AppController()
    register_callbacks(app_controller)
    app.run_server(debug=False)