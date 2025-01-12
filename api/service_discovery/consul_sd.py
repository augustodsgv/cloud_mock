from api.service_discovery.service_discovery import ServiceDiscovery
from api.cloud.instance import Instance
import requests
import time
import logging

logger = logging.getLogger(__name__)

class ConsulSD(ServiceDiscovery):
    def __init__(self, consul_url : str, consul_port : int = 8500):
        self.consul_url = consul_url
        self.consul_port = consul_port

    def register_instance(self, instance : Instance) -> None:
        payload = {
            "ID": instance.id,
            "Name": instance.name,
            "Tags": [instance.region, instance.product, instance.tenant_id],
            "Address": instance.id,
            "Port": instance.metrics_port,
        }
        
        response = requests.put(f'http://{self.consul_url}:{self.consul_port}/v1/agent/service/register', json=payload)
        if response.status_code != 200:
            logger.error(f'Error registering instance {instance.id} in consul? {response.content}')
        else:
            logger.info(f'Instance {instance.id} registered in consul')

    def deregister_instance(self, instance : Instance) -> None:
        response = requests.put(f'http://{self.consul_url}:{self.consul_port}/v1/agent/service/deregister/{instance.id}')
        if response.status_code != 200:
            logger.error(f'Error deregistering instance {instance.id} in consul? {response.content}')
        else:
            logger.info(f'Instance {instance.id} deregistered in consul: {response.content}')        
if __name__ == '__main__':
    sd = ConsulSD('localhost:8500')
    i = Instance('2', 'synthetic-0', None, region='america-east1')
    sd.register_instance(i)
    time.sleep(5)
    sd.deregister_instance(i)