from source.data_container import DataContainer
from threading import Lock

class StoreController:
    """
    Manages storage and retrieval of HOE simulation data.

    This class handles adding, deleting, and accessing stored simulations. 
    It provides thread-safe access to simulation data, allowing for concurrent 
    operations while ensuring data consistency.

    """

    def __init__(self):
        self.simulations: dict[str, DataContainer] = dict()
        self.new_data = False
        self.selected_simulation = list()
        self._lock_data:Lock = Lock()

    def add_simulation(self, name: str,data: DataContainer) -> None:
        with self._lock_data:
            self.simulations[name] = data
            self.new_data = True

    def get_simulations_as_row_data(self) -> list[dict]:
        with self._lock_data:
            data = list()
            for item in self.simulations.items():        
                data.append({"Simulation": item[0], "Color": item[1].color})
            return data

    def get_plot_data(self, add_Rs:bool, add_Rp:bool, add_Ts:bool, add_Tp:bool, add_es:bool, add_ep:bool ,hx: int, hy: int) -> list[dict]:
        with self._lock_data:
            plot_data_all = list()
            for key in self.selected_simulation:
                plot_data = self.simulations[key].get_plot_data(add_Rs, add_Rp, add_Ts, add_Tp, add_es, add_ep, hx, hy)
                plot_data_all = plot_data_all + plot_data
            return plot_data_all
            
    def get_json_data(self) -> dict[str]:
        with self._lock_data:
            json_data = dict()
            for key in self.simulations.keys():
                json_data[key]=(self.simulations[key].to_json())
            return json_data

    def delete_selected(self) -> None:
        with self._lock_data:
            for key in self.selected_simulation:
                del self.simulations[key]
            self.selected_simulation = list()
            self.new_data = True

