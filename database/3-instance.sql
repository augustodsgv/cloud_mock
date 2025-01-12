\connect cloud;

CREATE TABLE instances(
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    product VARCHAR(255) NOT NULL,
    region VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    metric_port INT,
    tenant_id UUID NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);