# Multi-Agent Workflow Demo

This demo showcases multiple AI agents collaborating through a structured workflow to solve complex business scenarios.

## Architecture

```
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │     (Router)    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Triage Agent   │ │ Research Agent  │ │ Compliance Agent│
│  (Classifies &  │ │ (Gathers data   │ │ (Checks rules   │
│   prioritizes)  │ │  from sources)  │ │  & regulations) │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Review Agent   │
                    │ (Synthesizes &  │
                    │    critiques)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Output Agent   │
                    │  (Formats final │
                    │    response)    │
                    └─────────────────┘
```

## Agents

### 1. Orchestrator
- Routes tasks to appropriate specialist agents
- Manages workflow state and handoffs
- Determines when workflow is complete

### 2. Triage Agent
- Classifies incoming requests
- Assigns priority and category
- Identifies which specialists are needed

### 3. Research Agent
- Queries the FoundryIQ knowledge base
- Gathers relevant data from documents
- Provides evidence-based findings

### 4. Compliance Agent
- Checks regulatory requirements
- Evaluates policy adherence
- Flags compliance risks

### 5. Review Agent
- Synthesizes inputs from multiple agents
- Identifies gaps or conflicts
- Requests additional information if needed

### 6. Output Agent
- Formats final response for user
- Creates executive summaries
- Generates action items

## Workflow Examples

### 1. Incident Response Workflow
```
User: "We have a critical system outage affecting tax calculations"

1. Triage Agent → Classifies as P1 incident, identifies impacted systems
2. Research Agent → Pulls related incidents, known issues, runbooks
3. Compliance Agent → Checks SLA obligations, regulatory reporting requirements
4. Review Agent → Synthesizes findings, identifies gaps in response
5. Output Agent → Creates incident summary with action plan
```

### 2. Customer Risk Assessment
```
User: "Prepare a risk assessment for customer CUST-005 renewal"

1. Triage Agent → Identifies as renewal risk assessment
2. Research Agent → Gathers customer data, support history, revenue
3. Compliance Agent → Checks certificate status, tax filings
4. Review Agent → Evaluates churn risk, recommends actions
5. Output Agent → Creates QBR-ready customer health report
```

### 3. Audit Preparation
```
User: "We have a SOC 2 audit next week, what's our readiness?"

1. Triage Agent → Identifies scope and audit type
2. Research Agent → Gathers evidence, controls, policies
3. Compliance Agent → Evaluates control effectiveness, gaps
4. Review Agent → Prioritizes remediation items
5. Output Agent → Creates audit readiness report
```

## Running the Demo

```bash
# Start the multi-agent API
cd /home/derek/repo/foundryIQ-demo
source .venv/bin/activate
python -m src.multi_agent.api

# Or run a specific workflow
python -m src.multi_agent.runner --scenario incident
```
