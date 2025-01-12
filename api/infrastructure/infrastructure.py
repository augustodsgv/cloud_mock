from api.cloud.instance import Instance
from api.cloud.tenant import Tenant
from abc import ABC, abstractmethod

class Infrastructure(ABC):
    @abstractmethod
    def create_instance(instance_name: str, environment: dict[str, str] | None = None) -> Instance:
        pass

    @abstractmethod
    def delete_instance(self, instance_name: str) -> None:
        pass

    @abstractmethod
    def list_instances(self)->list[str]:
        pass