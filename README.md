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