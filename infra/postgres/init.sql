-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE plants (
    plant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    timezone VARCHAR(64) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE production_lines (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id UUID REFERENCES plants(plant_id),
    line_name VARCHAR(255) NOT NULL,
    product_type VARCHAR(255),
    max_capacity_per_hour INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE assets (
    asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    line_id UUID REFERENCES production_lines(line_id),
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(255),
    model_number VARCHAR(255),
    installation_date DATE,
    criticality_score NUMERIC(4,2),
    operational_status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sensors (
    sensor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES assets(asset_id),
    sensor_name VARCHAR(255) NOT NULL,
    sensor_type VARCHAR(100) NOT NULL,
    unit VARCHAR(32),
    min_valid_value NUMERIC,
    max_valid_value NUMERIC,
    sampling_interval_seconds INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Telemetry events (time-series sensor data)
CREATE TABLE telemetry_events (
    event_id UUID DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    sensor_id UUID REFERENCES sensors(sensor_id),
    asset_id UUID REFERENCES assets(asset_id),
    value DOUBLE PRECISION NOT NULL,
    quality_flag VARCHAR(30) DEFAULT 'valid',
    ingestion_source VARCHAR(50),
    metadata JSONB,
    PRIMARY KEY (timestamp, event_id)
);

-- Maintenance records
CREATE TABLE maintenance_records (
    maintenance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES assets(asset_id),
    maintenance_type VARCHAR(100),
    description TEXT,
    performed_at TIMESTAMPTZ,
    performed_by VARCHAR(255),
    downtime_minutes INTEGER,
    cost NUMERIC(12,2),
    replacement_parts JSONB,
    outcome VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Production batches
CREATE TABLE production_batches (
    batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    line_id UUID REFERENCES production_lines(line_id),
    raw_material_lot VARCHAR(255),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    target_quantity INTEGER,
    produced_quantity INTEGER,
    defective_quantity INTEGER,
    defect_rate NUMERIC(8,5),
    quality_status VARCHAR(50),
    metadata JSONB
);