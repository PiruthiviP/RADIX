-- SQL Script to create job_role_details_json table
-- This table stores raw JSON data from the data/ folder with company references

-- Drop table if exists (optional - uncomment if you want to recreate)
-- DROP TABLE IF EXISTS job_role_details_json;

-- Create the job_role_details_json table
CREATE TABLE IF NOT EXISTS job_role_details_json (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    job_role_json JSONB NOT NULL,
    
    -- Foreign key constraint to companies table
    CONSTRAINT fk_company 
        FOREIGN KEY (company_id) 
        REFERENCES companies(company_id) 
        ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_job_role_company_id 
    ON job_role_details_json(company_id);

CREATE INDEX IF NOT EXISTS idx_job_role_company_name 
    ON job_role_details_json(company_name);

-- Create GIN index on JSONB column for efficient JSON queries
CREATE INDEX IF NOT EXISTS idx_job_role_json 
    ON job_role_details_json USING GIN (job_role_json);


-- Add comments for documentation
COMMENT ON TABLE job_role_details_json IS 'Stores raw JSON data from company job role JSON files';
COMMENT ON COLUMN job_role_details_json.id IS 'Primary key - auto-incrementing identifier';
COMMENT ON COLUMN job_role_details_json.company_id IS 'Foreign key reference to companies table';
COMMENT ON COLUMN job_role_details_json.company_name IS 'Company name extracted from JSON for quick reference';
COMMENT ON COLUMN job_role_details_json.job_role_json IS 'Complete JSON object stored as JSONB for efficient querying';

