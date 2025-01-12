from api.infrastructure.infrastructure import Infrastructure
import docker
import logging
logger = logging.getLogger(__name__)

class DockerInfrastructure(Infrastructure):
    def __init__(
            self,
            region: str,
            cloud_instance_image: str,
            docker_network: str | None = None,
            docker_url: str = 'unix://var/run/docker.sock',
            container_registry_repo: str | None = None,
        ):
        # TODO: create docker project implementation
        self.client = docker.DockerClient(base_url=docker_url)
        self.cloud_instance_image = cloud_instance_image
        self.region = region

        # If pulling image from registry
        if container_registry_repo != None:
            self.cloud_instance_image = f'{container_registry_repo}/{self.cloud_instance_image}'

        # If no network is provided, use the region as network name
        self.docker_network = docker_network
        if self.docker_network is None:
            self.docker_network = f'{self.region}'
            
        # Create the docker network if it does not exist
        try:
            self.client.networks.get(self.docker_network)
            logger.info(f"Network {self.docker_network} already exists.")
        except docker.errors.NotFound:
            self.client.networks.create(self.docker_network)
            logger.info(f"Network {self.docker_network} created.")
        
        self.instance_list = dict()


    def create_instance(self,
                        instance_id: str,
                        environment: dict[str, str] | None = None,
                        # expose_port: int | None = None,
                        ) -> None:
        """
        Creates a docker container with the given image.
        """
        logger.info(f"Creating instance {instance_id} with image {self.cloud_instance_image} an environment {environment}")

        container = self.client.containers.run(self.cloud_instance_image,
                                               name=instance_id,                # The id of the instance in the cloud database is the name of the container to allow instances with equal names
                                               detach=True,
                                               environment=environment,
                                               network=self.docker_network,
                                            #    ports={f'{expose_port}': expose_port} if expose_port else None
                                            )
        self.instance_list[instance_id] = container
        return True
    
    def delete_instance(self, instance_id: str) -> None:
        """
        Deletes a docker container with the given id.
        """
        container = self.instance_list[instance_id]
        container.stop()
        container.remove()
        del self.instance_list[instance_id]

    def list_instances(self)->list[str]:
        return list(self.instance_list.keys())

if __name__ == '__main__':
    cloud = DockerInfrastructure()
    cloud.create_instance('1234', 'synthetic_exporter', expose_port=8000)
    print(cloud.list_instances())
    input()
    cloud.delete_instance('1234')