from dash import dcc, html
import plotly.graph_objs as go

id_graph = "display_graph"

dummy_fig = go.Figure(
                data=[ ],
                layout=go.Layout(
                    title="Volume Hologram",                    
                    xaxis=dict(title='Variable', range=[-5, 105]),
                    yaxis=dict(title='Diffraction efficiency [%]', range=[-5, 105]),
                    margin=dict(l=40, r=40, t=40, b=40)
                )
            )


layout_display = html.Div(
    className="app_middle_top",            
    children=[
        dcc.Graph(
            id= id_graph,
            className="display_graph",
            figure=dummy_fig
        ),
    ],
)

