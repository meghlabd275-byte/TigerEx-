"""
TigerEx White Label Multi-Tenant Database System
PostgreSQL with schema separation per client
"""
import psycopg2
import os

class WhiteLabelDB:
    def __init__(self):
        self.conn_string = os.environ.get('DATABASE_URL', 
            'postgresql://user:pass@localhost:5432/tigerex_whitelabel')
    
    def get_client_schema(self, client_id):
        """Get database schema name for client"""
        return f"client_{client_id}"
    
    def create_client_database(self, client_id, client_name):
        """Create new database schema for white label client"""
        schema = self.get_client_schema(client_id)
        return {'schema': schema, 'client_id': client_id}
    
    def get_client_config(self, client_id):
        """Get client configuration from master database"""
        return {
            'client_id': client_id,
            'database': f'tigerex_{client_id}',
            'user': f'client_{client_id}_user',
            'status': 'active'
        }

# Migration SQL for PostgreSQL
MIGRATION_SQL = """
-- Master database for white labels
CREATE TABLE IF NOT EXISTS white_label_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    schema_name VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    email VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES white_label_clients(id),
    key VARCHAR(100) NOT NULL,
    value TEXT,
    UNIQUE(client_id, key)
);

CREATE TABLE IF NOT EXISTS client_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES white_label_clients(id),
    plan VARCHAR(50) NOT NULL,
    monthly_price DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'active',
    start_date DATE,
    end_date DATE
);
"""

print("White Label Database Module Ready")
