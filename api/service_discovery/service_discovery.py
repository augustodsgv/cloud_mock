from abc import ABC, abstractmethod
from api.cloud.instance import Instance

class ServiceDiscovery(ABC):
    @abstractmethod
    def register_instance(self, instance : Instance) -> None:
        pass

    @abstractmethod
    def deregister_instance(self, instance : Instance) -> None:
        pass