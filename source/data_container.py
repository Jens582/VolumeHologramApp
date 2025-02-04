import numpy as np
import json
from numbers import Number
from source.hoe_logger import logger

class DataContainer:
    """
    A container class for storing and managing diffraction efficiency simulation results.
    
    This class holds simulation data for reflection and transmission efficiencies 
    (Rs, Rp, Ts, Tp) as well as metadata such as variable values, color, and name.

    """
    def __init__(self):
        self.Rs_values: np.ndarray = None
        self.Rp_values: np.ndarray = None
        self.Ts_values: np.ndarray = None
        self.Tp_values: np.ndarray = None

        self.variable: np.ndarray = None
        self.color: str = "black"
        self.name: str = "Simulation"
        self.parameter_text: str = ""

    def to_dict(self) -> dict[str, any]:
        data = dict()
        data["Rs_values"] = self.Rs_values.tolist()
        data["Rp_values"] = self.Rp_values.tolist()
        data["Ts_values"] = self.Ts_values.tolist()
        data["Tp_values"] = self.Tp_values.tolist()
        data["variable"] = self.variable.tolist()
        data["color"] = self.color
        data["name"] = self.name
        data["parameter_text"] = self.parameter_text
        return data
    
    @staticmethod
    def from_dict(data: dict) -> "DataContainer":
        container = DataContainer()
        container.Rs_values = np.array(data["Rs_values"])
        container.Rp_values = np.array(data["Rp_values"])
        container.Ts_values = np.array(data["Ts_values"])
        container.Tp_values = np.array(data["Tp_values"])
        container.variable = np.array(data["variable"])
        container.color = data["color"]
        container.name = data["name"]
        container.parameter_text = data["parameter_text"]
        return container
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def from_json(self, json_str:str) -> "DataContainer":
        data = json.loads(json_str)
        return DataContainer.from_dict(data)  

    
    def get_dim(self) -> int:
        return len(self.variable)

    def insert_data(self, i: int, Rs: np.ndarray, Rp: np.ndarray, Ts: np.ndarray, Tp: np.ndarray) -> None:
        self.Rs_values[:,:,i] = Rs
        self.Rp_values[:,:,i] = Rp
        self.Ts_values[:,:,i] = Ts
        self.Tp_values[:,:,i] = Tp

    def get_i_variable(self, i) -> Number:
        return self.variable[i]
    
    def get_plot_data(self, add_rs, add_rp, add_ts, add_tp, add_es, add_ep, order_x, order_y) -> list[dict]:
        """
        Generates plot data based on selected parameters for visualization.

        Returns:
            list[dict]: A list of dictionaries containing plotly-compatible data 
                        (x-values, y-values, line style, and labels).
        """
        data_list = []
        if add_rs:
            data_list.append(self._get_plot_dict(self.name+"_Rs", self.Rs_values, order_x,order_y, "solid"))
        if add_rp:
            data_list.append(self._get_plot_dict(self.name+"_Rp", self.Rp_values, order_x,order_y, "dot"))
        if add_ts:
            data_list.append(self._get_plot_dict(self.name+"_Ts", self.Ts_values, order_x,order_y, "dash"))
        if add_tp:
            data_list.append(self._get_plot_dict(self.name+"_Tp", self.Tp_values, order_x,order_y, "longdashdot"))
        if add_es:
            data_list.append(self._get_plot_dict_energy_s(self.name+"_Es"))        
        if add_ep:
            data_list.append(self._get_plot_dict_energy_p(self.name+"_Ep"))
        
        # Fallback, if no data selected 
        if len(data_list) == 0:
                    plot = dict()
                    plot["x"] = self.variable
                    plot["y"] = self.variable.copy()
                    plot["y"][:] = 50.0
        return data_list


    def _get_plot_dict_energy_s(self, name: str):
        y = np.sum(self.Ts_values + self.Rs_values, axis=(0,1))
        plot = dict()
        plot["x"] = self.variable.copy()
        plot["y"] = y
        plot["line"] =  {"color": self.color, "dash":"solid"}
        plot["name"] = name
        plot["mode"] = "lines"
        return plot
    
    def _get_plot_dict_energy_p(self, name: str):
        y = np.sum(self.Tp_values + self.Rp_values, axis=(0,1))
        plot = dict()
        plot["x"] = self.variable.copy()
        plot["y"] = y
        plot["line"] =  {"color": self.color, "dash":"dot"}
        plot["name"] = name
        plot["mode"] = "lines"
        return plot

    def _get_plot_dict(self, name: str,values: np.ndarray, hx: int, hy: int, dash: str):
        plot = dict()
        plot["x"] = self.variable.copy()
        plot["y"] = self.get_hx_hy_order_of_values(values, hx, hy)
        plot["line"] =  {"color": self.color, "dash":dash}
        plot["name"] = name
        plot["mode"] = "lines"
        return plot

    @staticmethod
    def get_hx_hy_order_of_values(values: np.ndarray, hx: int, hy: int) -> np.ndarray:
        shape = values.shape
        dimx = shape[1]
        dimy = shape[0]
        dimz = shape[2]

        mx = int((dimx-1)/2)
        my = int((dimy-1)/2)
        ix = mx+hx
        iy = my+hy

        if (ix < 0) or (ix >= dimx) or (iy < 0) or (iy >= dimy):
            return np.zeros(dimz)
        
        return values[iy, ix, :].copy()

    @staticmethod
    def create_empty(dimX: int, dimY: int, dimZ: int, variable: np.ndarray, text: str) -> "DataContainer":
        empty = DataContainer()
        empty.Rs_values = np.ones((dimY, dimX, dimZ))*np.nan
        empty.Rp_values = np.ones((dimY, dimX, dimZ))*np.nan
        empty.Ts_values = np.ones((dimY, dimX, dimZ))*np.nan
        empty.Tp_values = np.ones((dimY, dimX, dimZ))*np.nan

        empty.variable = variable.copy()
        empty.parameter_text = text
        return empty


    