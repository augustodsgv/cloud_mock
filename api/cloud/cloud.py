from api.database.database import Database
from api.infrastructure.infrastructure import Infrastructure
from api.service_discovery.consul_sd import ServiceDiscovery
from api.cloud.instance import Instance
from api.cloud.tenant import Tenant
import uuid

class TenantDoesNotExist(Exception):
    pass

class TenantHasInstances(Exception):
    pass

class InstanceDontExist(Exception):
    pass

class ProductDoesNotExist(Exception):
    pass

class RegionDoesNotExist(Exception):
    pass

CLOUD_PRODUCTS = ['k8aas', 'dbaas', 'vm']

class Cloud:
    def __init__(self, database: Database, infrastructure_list: list[Infrastructure], service_discovery: ServiceDiscovery | None = None):
        self.database = database
        self.service_discovery = service_discovery
        self.infrastructure: dict[str, Infrastructure] = {}
        for infrastructure in infrastructure_list:
            self.infrastructure[infrastructure.region] = infrastructure


    def create_tenant(self, tenant_name: str) -> str:
        """
        Creates a tenant and returns its id.
        """
        new_tenant = Tenant(str(uuid.uuid4()), tenant_name)
        self.database.insert_tenant(new_tenant)
        return new_tenant.id
    
    def list_tenants(self) -> list[Tenant]:
        """
        Returns a list of all tenants.
        """
        return self.database.list_tenants()
    
    def delete_tenant(self, tenant_id: str)-> None:
        """
        Deletes a tenant by it's id.
        """
        tenant = self.database.get_tenant(tenant_id)
        if tenant is None:
            raise TenantDoesNotExist(f'Tenant with id {tenant_id} not found.')
        
        instances = self.database.list_instances(tenant)
        if instances:
            raise TenantHasInstances(f'Tenant with id {tenant_id} has instances and cannot be deleted.')
        self.database.delete_tenant(tenant)

    def create_instance(self, tenant_id: str, instance_name: str, instance_product: str = 'default', instance_region: str = 'default') -> str:
        """
        Creates an instance and returns its id.
        """
        tenant = self.database.get_tenant(tenant_id)
        if tenant is None:
            raise TenantDoesNotExist(f'Tenant with id {tenant_id} not found.')
        
        if instance_product not in CLOUD_PRODUCTS:
            raise ProductDoesNotExist(f'Product {instance_product} does not exist.')
        new_instance = Instance(str(uuid.uuid4()), instance_name, tenant_id, instance_product, instance_region)

        if instance_region not in self.infrastructure.keys():
            raise RegionDoesNotExist(f'Region {instance_region} does not exist.')
        
        instance_environment = {'TENANT_ID': tenant_id,
                                'INSTANCE_NAME': instance_name,
                                'INSTANCE_REGION': instance_region,
                                'INSTANCE_ID': new_instance.id,
                                'INSTANCE_TYPE': instance_product
                                }
        self.infrastructure[instance_region].create_instance(str(new_instance.id), instance_environment)
        
        self.database.insert_instance(new_instance, tenant)
        
        if self.service_discovery:
            self.service_discovery.register_instance(new_instance)
        return new_instance.id
    
    def list_instances(self, tenant_id: str | None = None) -> list[Instance]:
        """
        Returns a list of all instances for a given tenant.
        """
        if tenant_id:
            tenant = self.database.get_tenant(tenant_id)
            if tenant is None:
                raise TenantDoesNotExist(f'Tenant with id {tenant_id} not found.')
            return self.database.list_instances(tenant)
        return self.database.list_instances()

    def get_instance(self, instance_id: str) -> Instance:
        """
        Returns an instance by it's id.
        """
        instance = self.database.get_instance(instance_id)
        if instance is None:
            raise InstanceDontExist(f'Instance with id {instance_id} not found.')
        return instance

    def delete_instance(self, instance_id: str, instance_region: str) -> None:
        """
        Deletes an instance by it's id.
        """
        if instance_region not in self.infrastructure.keys():
            raise RegionDoesNotExist(f'Region {instance_region} does not exist.')
        
        instance = self.database.get_instance(instance_id)
        if instance is None:
            raise InstanceDontExist(f'Instance with id {instance_id} not found.')
        
        self.infrastructure[instance_region].delete_instance(instance.id)
        self.database.delete_instance(instance)
        if self.service_discovery:
            self.service_discovery.deregister_instance(instance)