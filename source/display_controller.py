import plotly.graph_objs as go
from source.hoe_logger import logger

def build_graph(figure_before: go.Figure, plot_data: list[dict]):
    if plot_data is None:
        return figure_before
    pram_variable = _filter_and_get_pram_variable(plot_data)                
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
                    xaxis=dict(title= pram_variable, range=rangeX),
                    yaxis=dict(title='Diffraction efficiency [%]', range=[-5, 105]),
                    margin=dict(l=40, r=40, t=40, b=40)
        )
    )               
    return figure

def _filter_and_get_pram_variable(plot_data: list[dict]) -> str:
    pram_variables = list()
    for pram in plot_data:        
        if pram.get("pram_variable"):
            pram_variables.append(pram["pram_variable"])
            del pram["pram_variable"]

    if len(pram_variables) == 0:
        return "Variable"
    pram_variable = pram_variables[0]

    if not all(item == pram_variable for item in pram_variables):
        logger.warning("Different variables in graph")

    return pram_variable


