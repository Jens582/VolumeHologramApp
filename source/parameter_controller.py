from source.hoe_parameter_creator import hoe_parameters
from source.parameter import Parameter
from numbers import Number

class ParameterControl:
    """
    Manages simulation parameters for a holographic optical element (HOE).

    Provides methods to retrieve, update, and manipulate simulation variables 
    and their associated values, ensuring consistency within the parameter set.
    """

    def __init__(self):
        self.current_variable = "cycles_thickness"

    def get_list_of_variable_parameters(self) -> list[Parameter]:
        """
        All parameter for the combobox
        """
        items = hoe_parameters.items()
        pram = [item[0] for item in items if item[1].is_variable]
        return pram
    
    def get_parameters_as_row_data_for_AgGrid(self) -> list[dict]:
        data = list()
        for item in hoe_parameters.items():            
            if item[0] != self.current_variable:
                if item[1].is_data_table:   
                    data.append({"Parameter": item[0], "Value": item[1].value})
        return data
    
    def set_parameter_with_row_data_from_AgGrid(self, rowdata) -> None:
        for item in rowdata:
            key = item["Parameter"]
            value = item["Value"]
            hoe_parameters[key].value = value
    
    def set_variable_range(self, variable: str, start: Number, end: Number, steps: Number):
        hoe_parameters[variable].set_me(start, end, steps)

    def get_variable_range(self, variable: str) -> tuple[Number]:
        pram = hoe_parameters[variable]
        return pram.start, pram.end, pram.steps

    def get_variable_labels(self, variable:str) -> tuple[str]:
        pram = hoe_parameters[variable]
        return pram.label_start, pram.label_end, pram.label_steps

    def get_current_variable_values(self) -> any:
        return hoe_parameters[self.current_variable].get_variable_values()

    def get_parameter_by_name(self, name) -> Parameter:
        return hoe_parameters[name]

