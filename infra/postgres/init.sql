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

-- Anomalies
CREATE TABLE anomalies (
    anomaly_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES assets(asset_id),
    detected_at TIMESTAMPTZ NOT NULL,
    model_name VARCHAR(100),
    model_version VARCHAR(100),
    anomaly_score NUMERIC(8,5),
    severity VARCHAR(20),
    affected_features JSONB,
    status VARCHAR(30) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Incidents
CREATE TABLE incidents (
    incident_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_code VARCHAR(50) UNIQUE NOT NULL,
    plant_id UUID REFERENCES plants(plant_id),
    line_id UUID REFERENCES production_lines(line_id),
    primary_asset_id UUID REFERENCES assets(asset_id),
    title VARCHAR(255),
    description TEXT,
    severity VARCHAR(20),
    status VARCHAR(30) DEFAULT 'open',
    started_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    business_impact_score NUMERIC(8,3),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Incident <-> Anomaly link table
CREATE TABLE incident_anomalies (
    incident_id UUID REFERENCES incidents(incident_id),
    anomaly_id UUID REFERENCES anomalies(anomaly_id),
    PRIMARY KEY (incident_id, anomaly_id)
);

-- Root cause hypotheses
CREATE TABLE root_cause_hypotheses (
    hypothesis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(incident_id),
    factor_name VARCHAR(255),
    factor_type VARCHAR(100),
    causal_confidence NUMERIC(6,5),
    rank INTEGER,
    evidence JSONB,
    causal_path JSONB,
    model_name VARCHAR(100),
    model_version VARCHAR(100),
    confirmed_by_operator BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Forecasts
CREATE TABLE forecasts (
    forecast_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(incident_id),
    asset_id UUID REFERENCES assets(asset_id),
    forecast_type VARCHAR(100),
    horizon_hours INTEGER,
    predicted_probability NUMERIC(6,5),
    estimated_impact JSONB,
    confidence_interval JSONB,
    model_version VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recommendations
CREATE TABLE recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(incident_id),
    action_type VARCHAR(100),
    action_description TEXT,
    priority VARCHAR(20),
    expected_benefit JSONB,
    estimated_cost NUMERIC(12,2),
    estimated_downtime_minutes INTEGER,
    risk_score NUMERIC(6,5),
    safety_status VARCHAR(50),
    explanation TEXT,
    status VARCHAR(30) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Operator feedback
CREATE TABLE operator_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(incident_id),
    recommendation_id UUID REFERENCES recommendations(recommendation_id),
    user_id VARCHAR(255),
    feedback_type VARCHAR(100),
    accepted BOOLEAN,
    outcome VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);