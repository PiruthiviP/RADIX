-- Enable pgcrypto extension for UUID support
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Table for raw provider outputs
CREATE TABLE IF NOT EXISTS provider_outputs (
    id bigserial PRIMARY KEY,
    company_id uuid NOT NULL,
    company_name text NOT NULL,
    timestamp timestamptz DEFAULT now() NOT NULL,
    llm_name text NOT NULL CONSTRAINT check_llm_name CHECK (llm_name IN ('gemini', 'groq', 'openrouter', 'consensus', 'test')),
    model_name text NOT NULL,
    parameters jsonb NOT NULL, -- Holds the complete 165-field JSON payload
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- Table for final consolidated profiles
CREATE TABLE IF NOT EXISTS consolidated_profiles (
    id bigserial PRIMARY KEY,
    company_id uuid UNIQUE NOT NULL,
    company_name text NOT NULL,
    timestamp timestamptz DEFAULT now() NOT NULL,
    parameters jsonb NOT NULL, -- Holds the consolidated 165-field output profile
    sources jsonb NOT NULL,    -- Maps field name to winning provider
    generation_status text NOT NULL CONSTRAINT check_gen_status CHECK (generation_status IN ('PENDING', 'IN_PROGRESS', 'SUCCESS', 'FAILED')),
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- Database indexes for performance
CREATE INDEX IF NOT EXISTS idx_provider_outputs_company_id ON provider_outputs(company_id);
CREATE INDEX IF NOT EXISTS idx_provider_outputs_company_name ON provider_outputs(company_name);
CREATE INDEX IF NOT EXISTS idx_provider_outputs_timestamp ON provider_outputs(timestamp);

CREATE INDEX IF NOT EXISTS idx_consolidated_profiles_company_id ON consolidated_profiles(company_id);
CREATE INDEX IF NOT EXISTS idx_consolidated_profiles_company_name ON consolidated_profiles(company_name);
CREATE INDEX IF NOT EXISTS idx_consolidated_profiles_timestamp ON consolidated_profiles(timestamp);

-- Stored procedure to write raw provider outputs and the consolidated profile in a single atomic transaction
CREATE OR REPLACE FUNCTION store_company_profile(
    p_company_id uuid,
    p_company_name text,
    p_generation_status text,
    p_consolidated_profile jsonb,
    p_sources jsonb,
    p_provider_data jsonb[] -- Array of JSON elements like: {"llm_name": "...", "model_name": "...", "parameters": {...}}
) RETURNS void AS $$
DECLARE
    provider_item jsonb;
BEGIN
    -- 1. Insert/Update consolidated profile
    INSERT INTO consolidated_profiles (
        company_id,
        company_name,
        timestamp,
        parameters,
        sources,
        generation_status
    ) VALUES (
        p_company_id,
        p_company_name,
        now(),
        p_consolidated_profile,
        p_sources,
        p_generation_status
    )
    ON CONFLICT (company_id) DO UPDATE SET
        company_name = EXCLUDED.company_name,
        timestamp = now(),
        parameters = EXCLUDED.parameters,
        sources = EXCLUDED.sources,
        generation_status = EXCLUDED.generation_status,
        updated_at = now();

    -- 2. Insert provider outputs
    IF p_provider_data IS NOT NULL THEN
        FOREACH provider_item IN ARRAY p_provider_data
        LOOP
            INSERT INTO provider_outputs (
                company_id,
                company_name,
                timestamp,
                llm_name,
                model_name,
                parameters
            ) VALUES (
                p_company_id,
                p_company_name,
                now(),
                (provider_item->>'llm_name'),
                (provider_item->>'model_name'),
                (provider_item->'parameters')
            );
        END LOOP;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Summary view to aggregate provider outputs
CREATE OR REPLACE VIEW provider_outputs_summary AS
SELECT
    company_id,
    company_name,
    count(id) as provider_count,
    min(timestamp) as started_at,
    max(timestamp) as completed_at,
    array_agg(DISTINCT llm_name) as providers_used
FROM
    provider_outputs
GROUP BY
    company_id,
    company_name;
