from dash import Dash
import dash_bootstrap_components as dbc
from layouts.app_layout import layout_app
from callbacks.controller_callbacks import register_callbacks
from source.manager_controller import MangerController


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server    
app.layout = layout_app
manger_controller = MangerController()
register_callbacks(manger_controller)

if __name__ == '__main__':
    app.run_server(debug=False)
    