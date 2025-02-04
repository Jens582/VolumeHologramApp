import plotly.graph_objs as go


def build_graph(figure_before: go.Figure, plot_data: list[dict]):
    if plot_data is None:
        return figure_before
                
    scatter_list = [go.Scatter(**pram) for pram in plot_data]
    rangeX = [0, 100]
    if len(scatter_list) != 0:
        x0 = scatter_list[0]["x"][0]
        x1 = scatter_list[0]["x"][-1]
        rangeX = [x0, x1]
    figure = go.Figure(
        data=scatter_list,
        layout=go.Layout(
                    title="Volume Hologram",                    
                    xaxis=dict(title='Variable', range=rangeX),
                    yaxis=dict(title='Diffraction efficiency [%]', range=[-5, 105]),
                    margin=dict(l=40, r=40, t=40, b=40)
        )
    )               
    return figure