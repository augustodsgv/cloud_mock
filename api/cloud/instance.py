from hashlib import sha1
from api.cloud.tenant import Tenant

class Instance:
    def __init__(self,
                 id : str,
                 name : str,
                 tenant_id : str,
                 product : str | None = 'default',
                 region : str | None = 'default',
                 address : str | None = None,
                 metrics_port : int = 8000
                ):
        self.id = id
        self.name = name
        self.tenant_id = tenant_id
        self.product = product
        self.region = region
        self.address = address
        if address is None:
            self.address = self.name
        self.metrics_port = metrics_port

    def __hash__(self):
        name_hash = int(sha1(self.name.encode()).hexdigest(), 16)
        tenant_hash = int(sha1(self.tenant.id.encode()).hexdigest(), 16)
        product_hash = int(sha1(self.product.encode()).hexdigest(), 16)
        instance_hash = (name_hash + tenant_hash + product_hash) % 10 ** 8
        return instance_hash
    
    def __str__(self):
        return f'ID: {self.id}\nName: {self.name}\nTenant: {self.tenant_id}\nProduct: {self.product}'

    @property
    def dict(self):
        return {"id": self.id,
                "name": self.name,
                "tenant_id": self.tenant_id,
                "product": self.product,
                "region": self.region,
                "address": self.address,
                "metric_port": self.metrics_port}