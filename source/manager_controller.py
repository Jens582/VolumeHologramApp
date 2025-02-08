from source.app_controller import AppController
from threading import Lock, Thread
import datetime
from time import sleep

class MangerController:

    def __init__(self):
        self.controllers: dict[str, AppController] = dict()
        self._lock: Lock = Lock()
        self._times: dict[str, datetime.datetime] = dict()
        self._wait_for_check = 60
        self.max_sleep: int = 5*60

        self._start_loop()

    def get_app_controller(self, id: str) -> AppController:
        if id is None:
            return None
        with self._lock:
            controller = self.controllers.get(id)
            self._times[id] = datetime.datetime.now()
            return controller

    def create_controller(self, id: str):
        self.controllers[id] = AppController()
        self._times[id] = datetime.datetime.now()
    
    def _start_loop(self):        
        self._thread_loop = Thread(target=self._check_for_alive_loop, daemon=True)
        self._thread_loop.start()

    def _check_for_alive_loop(self):
        while True:
            with self._lock:
                keys_del = list()
                for key in self.controllers.keys():
                    time = self._times[key]
                    now = datetime.datetime.now()
                    dt = (now-time).seconds
                    if dt > self.max_sleep:
                        keys_del.append(key)
                for key in keys_del:
                    del self.controllers[key]
                    del self._times[key]
            sleep(self._wait_for_check)

        