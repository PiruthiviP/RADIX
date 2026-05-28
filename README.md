# RADIX- Data Profiling & Architecture Engine

An analytical data framework designed to research, reconcile, store, and analyze company intelligence datasets and interview competencies.

## Repository Structure & Overview

### 📋 Activity 1 — Data Collection and Profiling
- **[Prompt1 - Research.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-01/Activity%201%20-%20Prompt%201/Prompt1%20-%20Research.txt)**: A structured instruction set for a Corporate Intelligence Analyst and Data Researcher. It utilizes a rigorous 163-parameter schema to compile atomic and composite details of target organizations (e.g., Blinkit).

### 🔄 Activity 2 — Data Reconciliation & Consolidation
- **[Prompt  2 - Consolidation.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-01/Activity%202%20-%20Prompt%202/Prompt%20%202%20-%20Consolidation.txt)**: Instructions configuring a Data Reconciliation and Validation Engine. This system deduplicates multi-source responses (up to 489 candidate rows) into a unified, 163-row "Golden Record" master dataset, filtering invalid data points and preserving source attribution.

### 🗄️ Database Schema Design (DDL Scripts)
- **[Script 1 - Create wide table.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-01/Activity%203%20-%20Script%201/Script%201%20-%20Create%20wide%20table.txt)**: Relational flat-table design (`public.company`) containing all 163 attributes inside a single wide entity to support rapid retrieval and simple data dumps.
- **[Script 2 - 10 tables.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-01/Activity%204%20-%20Script%202/Script%202%20-%2010%20tables.txt)**: Highly structured, semi-normalized schema design partitioning the 163 fields into 10 logical domain tables (e.g., `companies`, `company_financials`, `company_culture`, `company_logistics`, etc.) bound by foreign keys.

### 📊 Excel Data Frameworks
- **[Multi Table Framework.xlsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-01/Multi%20Table%20Framework.xlsx)**: Analytical workbook mapping, organizing, and validating multi-table data flows.
- **[Activity 5 - 10 table Framework/Multi Table Framework.xlsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-01/Activity%205%20-%2010%20table%20Framework/Multi%20Table%20Framework.xlsx)**: Validation template companion to the 10-table normalized SQL script.
- **[Book1.xlsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-01/Book1.xlsx)**: Primary workbook representing the raw ingestion/profile outputs.

### 🎯 Technical Interview Competency Engine
- **[Prompt 3 - Skill Areas.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-01/Activity%206%20-%20Prompt%203/Prompt%203%20-%20Skill%20Areas.txt)**: Technical Interview Intelligence prompt evaluating target companies across 18 fixed technical capabilities (DSA, System Design, OS, GenAI, etc.) with standardized scoring and concept lists.

---

## 🚀 Activity 2 — Placement Analytics Portal & Normalization Engine

An end-to-end framework managing placement statistics, corporate profiles, hiring rounds, and frontend interfaces for analytical operations.

### 📁 Milestone 2: Schema Migration & Prompt Pipelines

#### 1. Setup Context & Requirements
- **[SRM-Placements-Portal.pdf](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/0.%20Setting%20the%20Context/SRM-Placements-Portal.pdf)**: Contextual specification document for the placement portal requirements.

#### 2. Ingestion & Database Scripts (Staging and Normalized Tables)
- **[Staging Table Script.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/1.%20Create%20the%20staging%20table%20using%20the%20Script/Staging%20Table%20Script.txt)**: SQL staging schema DDL to load raw company data into a flat ingestion table.
- **[companies_master.csv / .xlsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/2.%20Data%20Ingestion%20into%20the%20staging%20table%20with%20116%20companies/companies_master.csv)**: Datasets for 116 core target companies ready for staging.
- **[Normalised Tables Script.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/3.%20Create%20the%2090%20tables%20using%20the%20Script/Normalised%20Tables%20Script.txt)**: Detailed relational database script specifying a 90-table normalized database architecture.
- **[countries.csv / cities.csv](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/4.%20Load%20the%20Countries%20and%20Cities%20Master%20data%20from%20the%20CSV/1.%20countries.csv)**: Reference lookups mapping geographic structures.
- **[Stored Procedure & Trigger.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/5.%20Execute%20the%20Script%20to%20migrate%20data%20into%20the%2088%20tables%20with%20triggers/Stored%20Procedure%20&%20Trigger.txt)**: Migration scripts to parse and populate the normalized tables from raw staging records using database triggers.
- **[Extra Companies.xlsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/6.%20Add%202%20new%20companies%20to%20the%20Staging%20table/Extra%20Companies.xlsx)**: Staging addition workbook containing 2 incremental companies.

#### 3. Skillset Prompts & Consolidation Pipelines
- **[8. Execute the 12 Prompts for the 12 skillsets](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/8.%20Execute%20the%2012%20Prompts%20for%20the%2012%20skillsets/)**: Folder of LLM prompt templates (OS, DSA, SWE, AI, System Design, SQL, etc.) to evaluate technical capabilities.
- **[Prompt2.md](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/9.%20Execute%20the%20second%20Prompt%20by%20uploading%20the%20CSV/Prompt2.md)**: Follow-up LLM prompt to reconcile skillset topics.
- **[0_Master_Script.sql](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/10.%20Run%20the%20Skill_Set%20Master%20setup%20script/0_Master_Script.sql)**: Setup DDL defining skill master tables.
- **[Prompt1-Output.csv](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/11.%20Upload%20the%20Consolidated%20Skillset_topics%20CSV%20into%20the%20staging_skill_topics%20tables.%20This%20is%20the%20result%20of%20the%2012%20prompts/Prompt1-Output.csv)**: Aggregated outputs maps from the skillset analysis prompts.

### 📁 Milestone 2 - Session 2: Integration & Frontend Portal

#### 1. Supabase Connection Guides
- **[Database Connection Prompt.txt / Guide](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/Session%202/Connection%20Prompt%20and%20Instructions/)**: Prompts, setup PDF, and schema definition JSONs for linking the portal to Supabase.

#### 2. Domain Data & Schema
- **[Hiring Rounds](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/Session%202/Hiring%20Rounds/)**: Schema (`create_job_role_table.sql`) and CSV dataset tracking hiring rounds and job roles.
- **[InnovX](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/Session%202/InnovX/)**: Schema (`create_innovx_json_table.sql`) and dataset tracking InnovX projects.

#### 3. Lovable UI Documents
- **[Lovable - UI Generation Docs](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/Session%202/Lovable%20-%20UI%20Generation%20Docs/)**: Docx requirements file, company schema files, and JSON mocks used to generate the placement portal interface.

#### 4. Pre-built UI Application
- **[remix-of-the-dream-weaver-main](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/Session%202/Pre%20built%20UI/remix-of-the-dream-weaver-main/)**: React/Remix frontend web application including core asset packages and configurations.
- **[SRMPlacement- Companies Research and Analytics Portal.zip](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-02/Milestone%202/Session%202/Pre%20built%20UI/SRMPlacement-%20Companies%20Research%20and%20Analytics%20Portal.zip)**: Archive containing the full export of the frontend portal.

---

## 🧪 Activity 3 — Data Quality Testing & Validation Framework

A robust validation engine designed to test, verify, and monitor the completeness, structural integrity, and business logic conformance of company profile datasets.

### 📁 Validation Configurations & Prompts
- **[Conceptual meta data setting.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-03/Conceptual%20meta%20data%20setting.txt)**: A master data dictionary mapping the 163 fields to metadata parameters (granularity, data volatility, data rules, nullability, regex patterns, business logic rules).
- **[unmodified prompt.txt](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-03/unmodified%20prompt.txt)**: System prompt template configuring a Lead QA Engineer agent to build python testing suites based on the metadata rules.

### 📁 Reference Data & Matrices
- **[companies_master.csv](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-03/companies_master.csv)**: Reference company dataset used for testing ingestions.
- **[table.xlsx / test_Cases.xlsx](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-03/table.xlsx)**: Validation worksheets, parameter templates, and testing status matrices.

### 📁 Programmatic QA Testing Suites
- **[pythontestcases](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-03/pythontestcases/)**: Over 60 individual python script units (e.g., `tc_1.1.py` through `tc_15.5.py`) testing constraints (negative bounds, email formatting, phone country codes, string limits) for specific fields.
- **[each_merged](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-03/each_merged/)**: Consolidated validation scripts grouping the test cases by domain area (e.g., `tc_1.py` for Company Basics, `tc_2.py` for Geographic Presence, etc.).
- **[combined_tests/test_combined.py](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-03/combined_tests/test_combined.py)**: Unified master test execution script running all tests and generating diagnostic logs.

### 📁 Parameter Workspaces (All_parameters/)
- **[All_parameters](file:///Users/Piruthivi'sMacbook/Desktop/RADIX-/activity-03/All_parameters/)**: Parameter-isolated workspaces (e.g., `2.1/`, `2.2/`, `10.2/`) containing custom mockup data generation scripts (`generate_data.py`), validation csv files, local validation scripts, and validation log files.