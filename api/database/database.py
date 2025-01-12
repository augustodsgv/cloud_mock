from abc import ABC, abstractmethod
from api.cloud.tenant import Tenant
from api.cloud.instance import Instance

class Database(ABC):
    @abstractmethod
    def insert_tenant(self, tenant: Tenant) -> None:
        pass

    @abstractmethod
    def delete_tenant(self, tenant: Tenant) -> None:
        pass

    @abstractmethod
    def list_tenants(self) -> list[Tenant]:
        pass

    @abstractmethod
    def get_tenant(self, tenant_id: str) -> Tenant | None:
        pass

    @abstractmethod
    def insert_instance(self, instance: Instance, tenant: Tenant) -> None:
        pass

    @abstractmethod
    def list_instances(self, tenant: Tenant | None = None) -> list[Instance]:
        pass

    @abstractmethod
    def get_instance(self, instance_id: str) -> Instance:
        pass

    @abstractmethod
    def delete_instance(self, instance: Instance) -> None:
        pass