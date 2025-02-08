
from threading import Event, Lock, Thread
from queue import Queue
import numpy as np
import logging
import logging.handlers
import queue
from logging import Logger

from source.parameter_controller import ParameterControl
from source.hoe_in_loop import HoeInLoop
from source.data_container import DataContainer
from source.store_controller import StoreController

from rcwa.rcwa_exception import RCWAError


class AppController:
    """
    Manages the execution, data handling, and control flow of the volume hologram simulation.
    """
    
    def __init__(self):
        self.parameter_control: ParameterControl = ParameterControl()
        self.store_controller: StoreController = StoreController()

        self.logger: Logger = logging.getLogger("Hologram_app_logger")
        self.log_queue: Queue = Queue()
        
        self._stop_loop_event: Event = Event()  
        self._thread_loop: Thread  = None
        self._task_queue = Queue()
        
        self._lock_data:Lock = Lock()
        self._progress: int = 0
        self._is_running: bool = False
        self._new_data: bool = False
        self._data: DataContainer = None       
                
        self._hoe_in_loop: HoeInLoop = None
        self._variables: np.ndarray = None

        self._prepare_logger()

    def transfer_simulation_to_store(self, name):
        """
        Transfers the completed simulation data to the store controller.
        
        Args:
            name (str): The name of the simulation to store.

        Returns:
            bool: True if the transfer was successful, False otherwise.
        """
        with self._lock_data:
            if self._is_running:
                self.logger.info("Can't transfer data, simulation is running")
                return False
            if self._progress != 100:
                self.logger.info("Can't transfer data, simulation is not completed")
                return False
            if self._data is None:
                self.logger.info("Can't transfer data, no simulation available")
                return False
            self._data.name = name    
            self._data.color = "red"       
            self.store_controller.add_simulation(name, self._data)
            self._data = None
            self._progress = 0
            self._new_data = True	
            return True

    def _transfer_data_from_queue(self):                       
        while not self._task_queue.empty():               
            transfer = self._task_queue.get() 
            if (transfer.get("running") is not None): self._is_running = transfer["running"]
            if (transfer.get("Progress") is not None): self._progress = transfer["Progress"]                
            if (transfer.get("new_data") is not None): self._new_data = transfer["new_data"]

            Rs = transfer.get("Rs")
            Rp = transfer.get("Rp")
            Ts = transfer.get("Ts")
            Tp = transfer.get("Tp")
            i = transfer.get("i")
            if i is not None:
                if self._data is not None:
                    self._data.insert_data(i, Rs, Rp, Ts, Tp)

    def get_updated_plotting_data_and_status(self, rs, rp, ts, tp, es, ep, hx, hy, ask_for_plot_data):
        """
        Retrieves the latest simulation data for plotting and status updates.

        Args:
            rs, rp, ts, tp, es, ep: Boolean flags indicating which components should be included in the plot.
            hx, hy: Harmonic orders.
            ask_for_plot_data (bool): If True, forces a data update.

        Returns:
            tuple: (is_running, progress, plot_data) or None if locked.
        """
        if self._lock_data.locked():
            self.logger.debug("Data are locked")
            return None
        
        with self._lock_data:
            self._transfer_data_from_queue()
            plot_data = None
            store_new = self.store_controller.new_data
            if ask_for_plot_data or self._new_data or store_new:
                if self._data is None:
                    plot_data = list()
                else:                    
                    plot_data = self._data.get_plot_data(rs,rp, ts, tp, es, ep, hx, hy)
                store_plots = self.store_controller.get_plot_data(rs,rp, ts, tp, es, ep, hx, hy)
                plot_data = plot_data + store_plots
            self._new_data = False
            self.store_controller.new_data = False
            return (self._is_running, self._progress, plot_data)
        
    def start_stop_calculation(self):
        """
        Starts or stops the simulation process. 
        """
        if self._thread_loop is not None and self._thread_loop.is_alive():
            self._stop_loop_event.set()
            self.logger.info("Simulation will be stopped")
            return False
        self._thread_loop = None
        self._prepare_calculation()

    def _prepare_calculation(self):
        """
        Prepare and starts a new simulation loop.
        """
        self.logger.info("Prepare simulation")   
        
        with self._lock_data:            
            try:                
                self._is_running = True                
                self._progress = 0                
                self._hoe_in_loop = HoeInLoop(self.parameter_control)                
                self._task_queue = Queue()                
                self._data = self._hoe_in_loop.get_start_value_container()                                 
                self._variables = self._data.variable   
            except Exception as e:
                self._is_running = False
                self._progress = 0
                self._hoe_in_loop = None
                self._data = None
                self._new_data = True
                self.logger.warning("Simulation preparation failed")
                if isinstance(e, RCWAError):
                    self.logger.warning(e.message+"\n"+e.info+"\n")
                else:
                    self.logger.error(f"Error: {type(e).__name__} - {e}")
                    self.logger.error("Traceback:", exc_info=True)                
                return 

        self._thread_loop = Thread(target=self._simulation_loop, daemon=True)
        self._thread_loop.start()
      
    def _simulation_loop(self):
        """
        Runs the main simulation loop, iterating over all variable values and computing the results.
        """
        variable = self._variables
        dim = len(variable)
        self.logger.info("Start simulation")  
        for i in range(dim):
            if self._stop_loop_event.is_set():
                transfer = dict()
                transfer["running"] = False                
                transfer["new_data"] = True
                self._task_queue.put(transfer)
                self._transfer_data_from_queue()
                self._stop_loop_event.clear()
                self.logger.info("Simulation stopped!")
                return
            else:   
                v = variable[i]                         
                try:                    
                    Rs, Rp, Ts, Tp = self._hoe_in_loop.get_Rs_Rp_Ts_Tp(v)           
                    transfer = dict()
                    transfer["Rs"] = Rs
                    transfer["Rp"] = Rp
                    transfer["Ts"] = Ts
                    transfer["Tp"] = Tp
                    transfer["i"] = i
                    transfer["running"] = True
                    transfer["new_data"] = True
                    transfer["Progress"] = int(100*i/dim)            
                    self._task_queue.put(transfer) 
                except Exception as e:                    
                    message = e.args[0]
                    self.logger.warning(f"Simulation value {v} can not be calculated. Exception type {type(e)}: "+ message)
                   

        transfer = dict()
        transfer["running"] = False
        transfer["Progress"] = 100
        transfer["new_data"] = True
        self._task_queue.put(transfer)
        with self._lock_data:
            self._transfer_data_from_queue()
        self.logger.info("Simulation finished!")

    def _prepare_logger(self):
        log_queue = self.log_queue
        logger = self.logger
        logger.setLevel(logging.INFO)

        queue_handler = logging.handlers.QueueHandler(log_queue)
        logger.addHandler(queue_handler)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        for handler in logger.handlers:
            handler.setFormatter(formatter)


