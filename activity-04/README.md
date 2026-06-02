# Activity 04: Multi-Agent Company Intelligence Pipeline

Build AI-driven research agents that automatically collect, structure, and validate company intelligence data using multiple large language models (LLMs).

## Engineering Problem Statement
Traditional research workflows rely heavily on manual data collection. Analysts search across multiple sources, gather information, and manually populate datasets. This approach is time-consuming, does not scale, causes inconsistent data quality, and becomes a bottleneck when analyzing large numbers of companies across hundreds of parameters.

## System Design & Architecture
The system uses an agent-based architecture with parallel Research Agents and a Consolidation Agent:
- **Phase 1 (User Input)**: Submit the target company name.
- **Phase 2 (Parallel Research)**: Three LLMs independently research all 163 parameters simultaneously (in chunks) to generate structured datasets.
- **Phase 3 & 5 (Validation Suite)**: Output datasets are parsed and verified against strict schema constraints (email, URL, numeric limits, ranges).
- **Phase 4 (Consolidation)**: The consolidation agent performs field-by-field comparison, identifies inconsistencies, resolves conflicts, and produces a final consolidated golden record.
- **Phase 7 (Self-Healing Regeneration)**: A targeted self-healing loop runs only on failed fields to fix validation errors.
- **Phase 6 (Database Persistence)**: Validated company profile splits are saved to Supabase.

```
                   ┌──────────────────────────┐
                   │   Phase 1: User Input    │
                   └─────────────┬────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
     ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
     │  LLM 1 (OR) │      │  LLM 2 (OR) │      │ LLM 3 (Groq)│
     └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
            │                    │                    │
            ▼                    ▼                    ▼
     ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
     │ Validation  │      │ Validation  │      │ Validation  │
     └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 ▼
                   ┌──────────────────────────┐
                   │ Phase 4: Consolidation   │
                   └─────────────┬────────────┘
                                 │
                                 ▼
                   ┌──────────────────────────┐
                   │ Phase 5: Final Validation│
                   └──────┬──────────────┬────┘
                          │              │
                    [Pass]▼              ▼[Fail]
             ┌───────────────┐    ┌───────────────────┐
             │ Supabase Write│    │ Regeneration Loop │
             └───────────────┘    └───────────────────┘
```

## Key Engineering Features
- **Multi-Model Research**: Leverages Google Gemini, Groq, and OpenRouter in parallel with robust retry and double-fallback mechanisms.
- **Robust JSON Preprocessing**: Resilient regex cleanup to parse LLM JSON responses containing unquoted values (e.g. converting `: NA` to `:"NA"`).
- **Structured JSON Outputs**: Outputs aligned with schema constraints for 163 fields using Pydantic V2.
- **Conflict Resolution**: Smart rule-based pre-consolidation combined with LLM conflict reconciliation.
- **Self-Healing Loop**: Automatically corrects validation failures dynamically in up to 3 repair rounds.

## Technology Stack
- **AI Models**: Google Gemini (AI Studio), Groq API, OpenRouter
- **AI Framework**: LangChain
- **Programming Language**: Python 3
- **Database**: Supabase (PostgreSQL)

## Engineering Competencies Developed
- AI agent design and orchestration (parallel execution, sequential stagger)
- Multi-model AI architecture patterns with deep fallback resilience
- Prompt engineering for schema-compliant structured outputs
- Automated research pipeline development and quality control validations
- Relational database schema integration with python payloads
