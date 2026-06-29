-- ====================================================================
-- RADIX Enterprise Security Database Schema
-- Place in: activity-08/backend/database_setup.sql
-- ====================================================================

-- 1. Create the Immutable Database Audit Trail Ledger Table
CREATE TABLE IF NOT EXISTS database_audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    action VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    record_id BIGINT,
    old_data JSONB,
    new_data JSONB,
    executed_by UUID DEFAULT auth.uid(), -- Traced back to Supabase auth user UUID
    executed_by_email VARCHAR(255),
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Index the audit trail for analytics and quick security audit compliance reports
CREATE INDEX IF NOT EXISTS idx_audit_table_name ON database_audit_trail(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_action ON database_audit_trail(action);
CREATE INDEX IF NOT EXISTS idx_audit_executed_at ON database_audit_trail(executed_at);

-- 2. Create the Trigger Function to Automatically Audit Data Mutations
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
DECLARE
    current_user_email VARCHAR(255);
BEGIN
    -- Extract the user email from the JWT metadata context if running within a Supabase query context
    BEGIN
        current_user_email := COALESCE(
            (auth.jwt() ->> 'email'),
            current_setting('request.jwt.claim.email', true),
            'system_api_worker'
        );
    EXCEPTION WHEN OTHERS THEN
        current_user_email := 'system_api_worker';
    END;

    INSERT INTO database_audit_trail (
        table_name,
        action,
        record_id,
        old_data,
        new_data,
        executed_by_email
    )
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CASE 
            WHEN TG_OP = 'DELETE' THEN OLD.company_id
            ELSE NEW.company_id
        END,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
        current_user_email
    );
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 3. Bind the Audit Trigger to the companies_json Table
DROP TRIGGER IF EXISTS audit_companies_trigger ON companies_json;
CREATE TRIGGER audit_companies_trigger
AFTER INSERT OR UPDATE OR DELETE ON companies_json
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();


-- 4. Enable Row Level Security (RLS) and Define Fine-Grained Access Controls
ALTER TABLE companies_json ENABLE ROW LEVEL SECURITY;

-- Policy A: Students, Recruiters, and Admins can view/select company records
DROP POLICY IF EXISTS "Allow select for all authenticated users" ON companies_json;
CREATE POLICY "Allow select for all authenticated users"
ON companies_json
FOR SELECT
USING (auth.role() = 'authenticated');

-- Policy B: Only Users with 'Admin' or 'LeadAnalyst' role metadata in their JWT can insert, update or delete
DROP POLICY IF EXISTS "Allow writes only for Admins" ON companies_json;
CREATE POLICY "Allow writes only for Admins"
ON companies_json
FOR ALL
USING (
  COALESCE(
    (auth.jwt() -> 'user_metadata' ->> 'role'), 
    'Student'
  ) IN ('Admin', 'LeadAnalyst')
);

-- ====================================================================
-- End of database_setup.sql
-- ====================================================================
