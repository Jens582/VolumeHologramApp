from dash import dcc, html
import plotly.graph_objs as go

id_graph = "display_graph"

layout_display = html.Div(
    className="app_middle_top",            
    children=[
        dcc.Graph(
            id= id_graph,
            className="display_graph",
            figure=go.Figure()
        ),
    ],
)

