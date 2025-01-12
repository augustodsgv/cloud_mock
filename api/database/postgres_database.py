from api.database.database import Database
from api.cloud.tenant import Tenant
from api.cloud.instance import Instance
import psycopg2

class PostgresDatabase(Database):
    def __init__(self, host: str, port: str, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def insert_tenant(self, tenant: Tenant)->None:
        with psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO tenants (id, name) VALUES (%s, %s)", (tenant.id, tenant.name))

    def delete_tenant(self, tenant: Tenant)->None:
        with psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM tenants WHERE id = %s", (tenant.id,))

    def list_tenants(self)->list[Tenant]:
        with psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name FROM tenants")
                tenants = cursor.fetchall()
                return [Tenant(id=row[0], name=row[1]) for row in tenants]

    def get_tenant(self, tenant_id: str)->Tenant | None:
        """
        Get tenant by id. Return None if tenant does not exist.
        """
        with psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name FROM tenants WHERE id = %s", (tenant_id,))
                tenant = cursor.fetchone()
                if tenant is None:
                    return None
                return Tenant(id=tenant[0], name=tenant[1])

    def insert_instance(self, instance: Instance, tenant: Tenant):
        with psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO instances (id, name, tenant_id, product, region) VALUES (%s, %s, %s, %s, %s)", (instance.id, instance.name, tenant.id, instance.product, instance.region))

    def list_instances(self, tenant: Tenant | None = None)->list[Instance]:
        with psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        ) as connection:
            with connection.cursor() as cursor:
                if tenant is not None:
                    cursor.execute("SELECT id, name, product, region, tenant_id FROM instances WHERE tenant_id = %s", (tenant.id,))
                else:
                    cursor.execute("SELECT id, name, product, region, tenant_id FROM instances")
                instances = cursor.fetchall()
                return [Instance(id=row[0], name=row[1], product=row[2], region=row[3], tenant_id=row[4]) for row in instances]

    def get_instance(self, instance_id: str):
        with psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name, product, region, tenant_id FROM instances WHERE id = %s", (instance_id,))
                instance = cursor.fetchone()
                if instance is None:
                    return None
                return Instance(id=instance[0], name=instance[1], product=instance[2], region=instance[3], tenant_id=instance[4])

    def delete_instance(self, instance: Instance):
        with psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM instances WHERE id = %s", (instance.id,))

def main():
    db = PostgresDatabase(host='localhost', port='5432', user='postgres', password='postgres', database='cloud')
    tenant = Tenant(id='1', name='test')
    # db.insert_tenant(tenant)
    # db.list_tenants()
    # instance = Instance(id='1', name='test', tenant=tenant, product='default', region='default', address='192.168.0.3', metrics_port=8080)
    instance = Instance(id='15', name='test', tenant=tenant, product='default', region='default', address='192.168.0.3', metrics_port=8080)
    instance = Instance(id='2345678', name='ta na hora de m', tenant=tenant, product='k8aas', region='sa-east-1', address='192.168.0.3', metrics_port=8080)

    db.insert_instance(instance, tenant)

if __name__ == '__main__':
    main()
