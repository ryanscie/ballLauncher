from abc import ABC, abstractmethod
from time import perf_counter as now
class SubsystemBase(ABC):
    def __init__(self):
        self._initialized=False; self._last_ts=None
    def _dt(self):
        t=now()
        if self._last_ts is None:
            self._last_ts=t; return 0.0
        dt=t-self._last_ts; self._last_ts=t; return dt
    @abstractmethod
    def initialize(self): ...
    @abstractmethod
    def periodic(self): ...
    @abstractmethod
    def shutdown(self): ...
