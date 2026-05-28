-- ============================================
-- Create innovx_json Table
-- ============================================
-- This script creates the innovx_json table for storing
-- company JSON data with references to the companies table.

-- Drop table if it exists (uncomment if you want to recreate)
-- DROP TABLE IF EXISTS innovx_json CASCADE;

-- Create the main table
CREATE TABLE IF NOT EXISTS innovx_json (
    id SERIAL PRIMARY KEY,
    company_id INTEGER,
    name VARCHAR NOT NULL,
    json_data JSONB,
    
    -- Foreign key constraint to companies table
    CONSTRAINT fk_innovx_json_company
        FOREIGN KEY (company_id) 
        REFERENCES companies (company_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Create index on name column for faster lookups
CREATE INDEX IF NOT EXISTS ix_innovx_json_name 
    ON innovx_json (name);

-- Optional: Create index on company_id for faster joins
CREATE INDEX IF NOT EXISTS ix_innovx_json_company_id 
    ON innovx_json (company_id);

-- Optional: Create GIN index on json_data for faster JSONB queries
CREATE INDEX IF NOT EXISTS ix_innovx_json_data 
    ON innovx_json USING GIN (json_data);


-- Success message
SELECT 'innovx_json table created successfully!' AS status;
