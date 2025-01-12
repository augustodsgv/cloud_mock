from abc import ABC
from api.cloud.instance import Instance

class ServiceDiscovery(ABC):
    def __init__(self):
        pass

    def register_instance(self, instance : Instance) -> None:
        pass

    def deregister_instance(self, instance : Instance) -> None:
        pass