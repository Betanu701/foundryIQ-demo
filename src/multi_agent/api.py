"""FastAPI endpoints for the multi-agent workflow system."""

import os
import sys
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json

from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from multi_agent.orchestrator import WorkflowOrchestrator, Workflow


# Initialize FastAPI
app = FastAPI(
    title="FoundryIQ Multi-Agent API",
    description="Multi-agent workflow system for complex business analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search client
search_client = None
try:
    search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX", "foundryiq-documents"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
    )
except Exception as e:
    print(f"Warning: Could not connect to search: {e}")

# Initialize orchestrator
orchestrator = WorkflowOrchestrator(search_client)


# Pydantic models
class WorkflowRequest(BaseModel):
    request: str
    max_iterations: Optional[int] = 5


class WorkflowResponse(BaseModel):
    workflow_id: str
    state: str
    final_output: Optional[str]
    iterations: int
    steps_executed: int
    agents_involved: List[str]
    conversation_history: List[dict]


class ScenarioInfo(BaseModel):
    key: str
    name: str
    request: str


# Demo scenarios
DEMO_SCENARIOS = {
    "incident": {
        "name": "Critical Incident Response",
        "request": "We have a critical system outage affecting tax calculations for multiple customers. The issue started 2 hours ago and support is getting escalated tickets. What's our incident response plan, what SLAs are at risk, and what should we communicate to customers?"
    },
    "customer_qbr": {
        "name": "Customer QBR Preparation",
        "request": "I have a Quarterly Business Review with customer CUST-005 (TechFlow Solutions) next week. Prepare a comprehensive customer health report including their support history, any compliance issues, revenue trends, and churn risk indicators. Also identify any upsell opportunities."
    },
    "audit_prep": {
        "name": "SOC 2 Audit Preparation",
        "request": "Our SOC 2 Type II audit is scheduled for next month. Assess our readiness across all control domains - security policies, access controls, vulnerability management, backup procedures, and incident response. Identify any gaps that need immediate remediation."
    },
    "compliance_review": {
        "name": "End of Quarter Compliance",
        "request": "We're approaching end of Q4. Provide a comprehensive compliance status report: Which tax filings are due in the next 30 days? Are there any overdue filings? Which customers have expiring exemption certificates? What's our patch compliance status? Flag anything that could result in penalties or audit findings."
    },
    "risk_assessment": {
        "name": "Enterprise Risk Assessment",
        "request": "The board wants an enterprise risk assessment. Analyze our current risk posture across: security vulnerabilities, compliance gaps, customer churn indicators, vendor dependencies, and operational bottlenecks. Prioritize the top 5 risks with recommended mitigations."
    },
    "revenue_analysis": {
        "name": "Revenue & Product Strategy",
        "request": "Finance needs a strategic analysis: Which products are driving the most revenue? Which ones are underperforming? What's in the roadmap that could impact pricing? Are there customers at high churn risk that could affect forecasts? Provide insights for the upcoming planning cycle."
    }
}


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "service": "FoundryIQ Multi-Agent API",
        "status": "running",
        "version": "1.0.0",
        "agents": ["orchestrator", "triage", "research", "compliance", "review", "output"]
    }


@app.get("/scenarios", response_model=List[ScenarioInfo])
def list_scenarios():
    """List available demo scenarios."""
    return [
        ScenarioInfo(key=key, name=info["name"], request=info["request"])
        for key, info in DEMO_SCENARIOS.items()
    ]


@app.post("/workflow", response_model=WorkflowResponse)
def run_workflow(request: WorkflowRequest):
    """Run a multi-agent workflow."""
    workflow = orchestrator.create_workflow(request.request)
    workflow.max_iterations = request.max_iterations
    
    # Run the workflow
    workflow = orchestrator.run_workflow(workflow)
    
    # Return summary
    summary = orchestrator.get_workflow_summary(workflow)
    
    return WorkflowResponse(
        workflow_id=summary["workflow_id"],
        state=summary["state"],
        final_output=summary["final_output"],
        iterations=summary["iterations"],
        steps_executed=summary["steps_executed"],
        agents_involved=summary["agents_involved"],
        conversation_history=summary["conversation_history"]
    )


@app.post("/workflow/{scenario_key}", response_model=WorkflowResponse)
def run_scenario(scenario_key: str):
    """Run a predefined demo scenario."""
    if scenario_key not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_key}' not found")
    
    scenario = DEMO_SCENARIOS[scenario_key]
    workflow = orchestrator.create_workflow(scenario["request"])
    
    # Run the workflow
    workflow = orchestrator.run_workflow(workflow)
    
    # Return summary
    summary = orchestrator.get_workflow_summary(workflow)
    
    return WorkflowResponse(
        workflow_id=summary["workflow_id"],
        state=summary["state"],
        final_output=summary["final_output"],
        iterations=summary["iterations"],
        steps_executed=summary["steps_executed"],
        agents_involved=summary["agents_involved"],
        conversation_history=summary["conversation_history"]
    )


@app.get("/workflow/stream")
async def stream_workflow(request: str):
    """Stream a workflow execution with real-time updates."""
    
    async def event_generator():
        events = []
        
        def stream_callback(event_type: str, message: str):
            events.append({
                "type": event_type,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
        
        workflow = orchestrator.create_workflow(request)
        
        # Start workflow in a way that captures events
        import threading
        result = {"workflow": None}
        
        def run_workflow_thread():
            result["workflow"] = orchestrator.run_workflow(workflow, stream_callback)
        
        thread = threading.Thread(target=run_workflow_thread)
        thread.start()
        
        # Stream events as they come in
        last_sent = 0
        while thread.is_alive() or last_sent < len(events):
            await asyncio.sleep(0.1)
            while last_sent < len(events):
                event = events[last_sent]
                yield f"data: {json.dumps(event)}\n\n"
                last_sent += 1
        
        # Send final result
        if result["workflow"]:
            summary = orchestrator.get_workflow_summary(result["workflow"])
            yield f"data: {json.dumps({'type': 'result', 'data': summary})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
