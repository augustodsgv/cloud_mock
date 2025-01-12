# Cloud Mock
This projects is meant to create a cloud-like environment that may be used to research porpouses.

## The project
The cloud business model is implemented by the following aspects
* Cloud tenant: represents a client of the cloud provider, that can create and delete instances
* Instance: represents an running object that the tenant bought from the cloud, such as Virtual Machines, Databases or Kubernetes Clusters
* Regions: A cloud provider may have numerous regions, such as GCPs regions sa-east-1. In this implementation, being in different regions means that instances can't 
communicate with themselves

## Running the project
### Cloud infrastructre
An infrastructre is an API that the project API can communicate and generate containers, VMs, databases etc.
This is what makes this API really work.
For now, this project only supports the docker infrastructure, and will use the [cloud_metrics_generator](github.com/augustodsgv/cloud_metrics_generator) to simulate cloud instances.
So download it on your host machine by running

```sh
curl -fsSL https://get.docker.com -o get-docker.sh
sudo ./get-docker.sh
```
### Database
For this project to run, a relational database is needed to store the data. The recomended one is postgres, that can
also be deployed using docker

### Service Discovery
This project also has support for service discovery. This is useful for monitoring systems such as Prometheus to 
keep track of the instances being deployed.
For now, the project only supports Consul as service discovery, that can also be deployed with docker

## Running the docker container
The fastest way of starting the project is building the docker image locally
```sh
docker build . -t cloud_metrics_generator
```
If you need the container on other environment that supports docker, it might be
useful to send it to dockerhub. To do so, use the script
```
./push_to_dockerhub.sh
```
With the image in hands, the following environment variables needed

Finally run the container. It require the following environment variables
* `DB_HOST` -> Host of the database, e.g., postgres
* `DB_PORT` -> Port of the database, e.g., 5432
* `DB_USER` -> User for the database, e.g., postgres
* `DB_PASSWORD` -> Password for the database, e.g., postgres
* `DB_DATABASE` -> Name of the database, e.g., cloud
* `CONTAINER_REGISTRY_REPO` -> Repository for the container registry, e.g., augustodsgv
* `DOCKER_INSTANCE_IMAGE` -> Docker image for the instance, e.g., cloud_metrics_generator
* `LOG_LEVEL` -> Log level for the application, e.g., debug
* `SD_HOST` -> Host for the service discovery, e.g., consul-server
* `SD_PORT` -> Port for the service discovery, e.g., 8500

Finally, run it:
```sh
docker run --rm -it \
    -e DB_HOST=postgres \
    -e DB_PORT=5432 \
    -e DB_USER=postgres \
    -e DB_PASSWORD=postgres \
    -e DB_DATABASE=cloud \
    -e CONTAINER_REGISTRY_REPO=augustodsgv \
    -e DOCKER_INSTANCE_IMAGE=cloud_metrics_generator \
    -e LOG_LEVEL=debug \
    -e SD_HOST=consul-server \
    -e SD_PORT=8500 \
    -p 7000:7000 cloud_metrics_generator   
``` 
## API Refference
The following methods are implemented:

### Tenants

#### Create Tenant
- **Endpoint:** `/create-tenant`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "tenant_name": "string"
    }
    ```
- **Response:**
    ```json
    {
        "detail": "Tenant {tenant_name} created successfully",
        "tenant_id": "string"
    }
    ```

#### List Tenants
- **Endpoint:** `/list-tenants`
- **Method:** `GET`
- **Response:**
    ```json
    {
        "tenants-list": ["tenant1", "tenant2", ...]
    }
    ```

#### Delete Tenant
- **Endpoint:** `/delete-tenant`
- **Method:** `DELETE`
- **Query Parameter:**
    - `tenant_id`: `string`
- **Response:**
    ```json
    {
        "detail": "Tenant {tenant_id} deleted successfully"
    }
    ```

### Instances

#### Create Instance
- **Endpoint:** `/create-instance`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "tenant_id": "string",
        "product": "string",
        "region": "string",
        "instance_name": "string"
    }
    ```
- **Response:**
    ```json
    {
        "detail": "Instance {instance_name} created successfully for tenant {tenant_id}",
        "instance_id": "string"
    }
    ```

#### Delete Instance
- **Endpoint:** `/delete-instance`
- **Method:** `DELETE`
- **Request Body:**
    ```json
    {
        "tenant_id": "string",
        "region": "string",
        "instance_id": "string"
    }
    ```
- **Response:**
    ```json
    {
        "detail": "Instance {instance_id} deleted successfully"
    }
    ```

#### List Instances
- **Endpoint:** `/list-instances`
- **Method:** `GET`
- **Query Parameter:**
    - `tenant_id`: `string`
- **Response:**
    ```json
    {
        "instances-list": ["instance1", "instance2", ...]
    }
    ```

# Authors
augustodsgv