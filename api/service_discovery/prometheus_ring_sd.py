from .service_discovery import ServiceDiscovery
from api.cloud.instance import Instance
import requests
# import logger


class PrometheusRingServiceDiscovery(ServiceDiscovery):
    def __init__(
            self,
            url: str,
            port: int
            ):
        self.url = url
        self.port = port

    def register_instance(self, instance: Instance):
        payload = {
            'id': instance.id,
            'name': instance.name,
            'address': instance.id,
            'metrics_port': instance.metrics_port
        }
        response = requests.post(f'http://{self.url}:{self.port}/register-target', json=payload)
        if response.status_code != 200:
            print(f"Failed to register instance {instance} with Prometheus Ring: {response.content}")
            
        else:
            print(f"Instance {instance} registered with Prometheus Ring")
            


    def deregister_instance(self, instance: Instance):
        response = requests.delete(f'http://{self.url}:{self.port}/unregister-target?target_id={instance.id}')
        if response.status_code != 200:
            print(f"Failed to deregister instance {instance} with Prometheus Ring", response.content)
        else:
            print(f"Instance {instance} deregistered with Prometheus Ring")

if __name__ == '__main__':
    sd = PrometheusRingServiceDiscovery('localhost', 9988)
    i = Instance('3', 'synthetic-0', None, region='america-east1')
    sd.register_instance(i)
    input()
    sd.deregister_instance(i)