from dash import Dash
import dash_bootstrap_components as dbc
from layouts.app_layout import layout_app
from callbacks.controller_callbacks import register_callbacks
from source.app_controller import AppController


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server    
app.layout = layout_app
app_controller = AppController()
register_callbacks(app_controller)

if __name__ == '__main__':
    app.run_server(debug=True)  