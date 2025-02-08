import plotly.graph_objs as go


def build_dummy_graph(text: str):
    dummy_fig = go.Figure(
                data=[ ],
                layout=go.Layout(
                    title="Volume Hologram",                    
                    xaxis=dict(title='Variable', range=[-5, 105]),
                    yaxis=dict(title='Diffraction efficiency [%]', range=[-5, 105]),
                    margin=dict(l=40, r=40, t=40, b=40)
                )
            )
    dummy_fig.add_annotation(
                    text=text,
                    x=50,  
                    y=50,  
                    showarrow=False, 
                    font=dict(size=24)  
    )
    return dummy_fig


def build_graph(figure_before: go.Figure, plot_data: list[dict], pram_variable):
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
                    xaxis=dict(title= pram_variable, range=rangeX),
                    yaxis=dict(title='Diffraction efficiency [%]', range=[-5, 105]),
                    margin=dict(l=40, r=40, t=40, b=40)
        )
    )               
    return figure

def filter_and_get_pram_variables(plot_data: list[dict]) -> list[str]:
    pram_variables = list()
    if plot_data is None:
        return pram_variables
    for pram in plot_data:        
        if pram.get("pram_variable"):
            pram_variables.append(pram["pram_variable"])
            del pram["pram_variable"]
    return pram_variables




