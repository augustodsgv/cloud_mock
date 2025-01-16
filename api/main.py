from api.cloud.cloud import Cloud, TenantDoesNotExist, TenantHasInstances, InstanceDontExist, ProductDoesNotExist, RegionDoesNotExist
from api.infrastructure.docker_infrastructure import DockerInfrastructure
from api.service_discovery.prometheus_ring_sd import PrometheusRingServiceDiscovery
from api.database.postgres_database import PostgresDatabase
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from typing import Optional
import os
import logging

from fastapi import FastAPI
import logging
import logging.config
import os

LOG_LEVEL = os.environ.get('LOG_LEVEL', "INFO").upper()

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {  # root logger
            "level": LOG_LEVEL,
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "DEBUG",
            "handlers": ["default"],
        },
        "uvicorn.access": {
            "level": "DEBUG",
            "handlers": ["default"],
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

import os

app = FastAPI()
Instrumentator().instrument(app).expose(app)

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_DATABASE = os.environ.get('DB_DATABASE')
DOCKER_URL = os.environ.get('DOCKER_URL', 'unix://var/run/docker.sock')
CONTAINER_REGISTRY_REPO = os.environ.get('CONTAINER_REGISTRY_REPO', None)
DOCKER_INSTANCE_IMAGE = os.environ.get('DOCKER_INSTANCE_IMAGE', None)

db = PostgresDatabase(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
cloud_infrastructre_a = DockerInfrastructure(region='cloud-region-a', cloud_instance_image=DOCKER_INSTANCE_IMAGE, docker_url=DOCKER_URL, container_registry_repo=CONTAINER_REGISTRY_REPO)
cloud_infrastructre_b = DockerInfrastructure(region='cloud-region-b', cloud_instance_image=DOCKER_INSTANCE_IMAGE, docker_url=DOCKER_URL, container_registry_repo=CONTAINER_REGISTRY_REPO)
cloud_infrastructre_c = DockerInfrastructure(region='cloud-region-c', cloud_instance_image=DOCKER_INSTANCE_IMAGE, docker_url=DOCKER_URL, container_registry_repo=CONTAINER_REGISTRY_REPO)

if 'SD_HOST' in os.environ:
    SD_HOST = os.environ.get('SD_HOST')
    SD_PORT = os.environ.get('SD_PORT')
    service_discovery = PrometheusRingServiceDiscovery(SD_HOST, SD_PORT)
    logger.debug(f"Service discovery enabled with host {SD_HOST} and port {SD_PORT}")
else:
    service_discovery = None
cloud = Cloud(db, [cloud_infrastructre_a, cloud_infrastructre_b, cloud_infrastructre_c], service_discovery)

class InstanceRequest(BaseModel):
    tenant_id: str
    product: str
    region: str
    instance_id: Optional[str] = None       # Instance creation does not require instance_id
    instance_name: Optional[str] = None

class TenantRequest(BaseModel):
    tenant_name : Optional[str] = None
    tenant_id: Optional[str] = None

@app.post('/create-tenant')
def create_user(r: TenantRequest):
    if r.tenant_name is None:
        raise HTTPException(status_code=400, detail='Field tenant_name is empty')
    new_tenant_id = cloud.create_tenant(r.tenant_name)
    logger.info(f"Tenant {r.tenant_name} created successfully")
    return {"detail": f"Tenant {r.tenant_name} created successfully", "tenant_id": f"{new_tenant_id}"}

@app.get('/list-tenants')
def list_tenants():
    logger.info("Listing tenants")
    return {"tenants-list": cloud.list_tenants()}

@app.delete('/delete-tenant')
def delete_tenant(tenant_id: str = None):
    try:
        cloud.delete_tenant(tenant_id)
        logger.info(f"Tenant {tenant_id} deleted successfully")
        return {"detail": f"Tenant {tenant_id} deleted successfully"}
    except TenantDoesNotExist as e:
        logger.error(f'Tenant with id {tenant_id} not found.')
        raise HTTPException(status_code=404, detail=f'Tenant with id {tenant_id} not found.')
    except TenantHasInstances as e:
        logger.error(f'Tenant with id {tenant_id} has instances and cannot be deleted.')
        raise HTTPException(status_code=400, detail=f'Tenant with id {tenant_id} has instances and cannot be deleted.')

@app.post('/create-instance')
def create_instance(request: InstanceRequest):
    if request.instance_name is None:
        logger.error('Field instance_name is empty')
        raise HTTPException(status_code=400, detail='Field instance_name is empty')
    try:
        instance_id = cloud.create_instance(request.tenant_id, request.instance_name, request.product, request.region)
        logger.info(f"Instance {request.instance_name} created successfully")
        return {"detail": f"Instance {request.instance_name} created successfully for tenant {request.tenant_id}", "instance_id": f"{instance_id}"}
    
    except TenantDoesNotExist as e:
        logger.error(f'Tenant with id {request.tenant_id} not found.')
        raise HTTPException(status_code=404, detail=f'Tenant with id {request.tenant_id} not found.')
    
    except ProductDoesNotExist as e:
        logger.error(f'Product with id {request.product} not found.')
        raise HTTPException(status_code=404, detail=f'Product {request.product} does not exist.')
    
    except RegionDoesNotExist as e:
        logger.error(f'Region with name {request.region} not found.')
        raise HTTPException(status_code=404, detail=f'Region {request.region} does not exist.')

@app.delete('/delete-instance')
def delete_instance(request: InstanceRequest):
    try:
        cloud.delete_instance(request.instance_id, request.region)
        logger.info(f"Instance {request.instance_id} deleted successfully")
        return {"detail": f"Instance {request.instance_id} deleted successfully"}
    
    except TenantDoesNotExist as e:
        logger.error(f'Tenant with id {request.tenant_id} not found.')
        raise HTTPException(status_code=404, detail=f'Tenant with id {request.tenant_id} not found.')
    
    except RegionDoesNotExist as e:
        logger.error(f'Region with name {request.region} not found.')
        raise HTTPException(status_code=404, detail=f'Region {request.region} does not exist.')
    
    except ProductDoesNotExist as e:
        logger.error(f'Product with id {request.product} not found.')
        raise HTTPException(status_code=404, detail=f'Product {request.product} does not exist.')
    
    except InstanceDontExist as e:
        logger.error(f'Instance with id {request.instance_id} not found.')
        raise HTTPException(status_code=404, detail=f'Instance with id {request.instance_id} not found.')
    
    
@app.get('/list-instances')
def list_instances(tenant_id: str = ""):
    try:
        instance_list = cloud.list_instances(tenant_id)
        logger.info(f"Listing instances for tenant {tenant_id}")
        return {"instances-list": instance_list}
    except TenantDoesNotExist as e:
        logger.error(f'Tenant with id {tenant_id} not found.')
        raise HTTPException(status_code=404, detail=f'Tenant with id {tenant_id} not found.')
    