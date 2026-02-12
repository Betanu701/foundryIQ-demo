"""Orchestration layer for multi-agent workflows."""

import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os

from openai import AzureOpenAI

from .agents import AgentRole, AgentConfig, AgentMessage, get_agent_config, AGENT_PROMPTS


class WorkflowState(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    NEEDS_REVISION = "needs_revision"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    step_id: int
    agent: AgentRole
    instruction: str
    status: str = "pending"
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class Workflow:
    """A multi-agent workflow."""
    workflow_id: str
    user_request: str
    state: WorkflowState = WorkflowState.PENDING
    steps: List[WorkflowStep] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    final_output: Optional[str] = None
    iteration_count: int = 0
    max_iterations: int = 5
    created_at: datetime = field(default_factory=datetime.now)


class AgentExecutor:
    """Executes individual agent tasks."""
    
    def __init__(self, search_client=None):
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview"
        )
        self.model = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
        self.search_client = search_client
    
    def _query_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query the FoundryIQ knowledge base."""
        if not self.search_client:
            return []
        
        try:
            results = self.search_client.search(
                search_text=query,
                top=top_k,
                select=["file_name", "content", "title", "source_url"]
            )
            return [
                {
                    "file_name": r["file_name"],
                    "content": r["content"][:1000],  # Truncate for context
                    "title": r.get("title", r["file_name"]),
                    "source_url": r.get("source_url", "")
                }
                for r in results
            ]
        except Exception as e:
            print(f"Knowledge base query error: {e}")
            return []
    
    def execute(
        self, 
        agent_role: AgentRole, 
        instruction: str, 
        context: Dict[str, Any] = None,
        knowledge_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a single agent task."""
        config = get_agent_config(agent_role)
        
        # Build context message
        context_parts = []
        if context:
            context_parts.append(f"Previous agent outputs:\n{json.dumps(context, indent=2)}")
        
        # Query knowledge base if agent has permission
        if config.can_query_knowledge and knowledge_query:
            kb_results = self._query_knowledge_base(knowledge_query)
            if kb_results:
                context_parts.append(f"Knowledge Base Results:\n{json.dumps(kb_results, indent=2)}")
        
        # Build messages
        messages = [
            {"role": "system", "content": config.system_prompt}
        ]
        
        if context_parts:
            messages.append({
                "role": "system",
                "content": "\n\n".join(context_parts)
            })
        
        messages.append({
            "role": "user",
            "content": instruction
        })
        
        # Call the LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON if possible
            try:
                return {
                    "agent": agent_role.value,
                    "raw_response": content,
                    "parsed": json.loads(content),
                    "success": True
                }
            except json.JSONDecodeError:
                return {
                    "agent": agent_role.value,
                    "raw_response": content,
                    "parsed": None,
                    "success": True
                }
                
        except Exception as e:
            return {
                "agent": agent_role.value,
                "error": str(e),
                "success": False
            }


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows."""
    
    def __init__(self, search_client=None):
        self.executor = AgentExecutor(search_client)
        self.workflows: Dict[str, Workflow] = {}
    
    def _generate_workflow_id(self) -> str:
        """Generate a unique workflow ID."""
        import uuid
        return f"wf_{uuid.uuid4().hex[:8]}"
    
    def create_workflow(self, user_request: str) -> Workflow:
        """Create a new workflow from a user request."""
        workflow_id = self._generate_workflow_id()
        workflow = Workflow(
            workflow_id=workflow_id,
            user_request=user_request
        )
        self.workflows[workflow_id] = workflow
        return workflow
    
    def _plan_workflow(self, workflow: Workflow) -> List[WorkflowStep]:
        """Use the orchestrator agent to plan the workflow."""
        result = self.executor.execute(
            AgentRole.ORCHESTRATOR,
            f"Plan a workflow for this user request: {workflow.user_request}"
        )
        
        steps = []
        step_id = 1
        
        if result["success"] and result.get("parsed"):
            plan = result["parsed"]
            for step_info in plan.get("workflow_steps", []):
                agent_name = step_info.get("agent", "RESEARCH").upper()
                try:
                    agent_role = AgentRole[agent_name]
                except KeyError:
                    agent_role = AgentRole.RESEARCH
                
                steps.append(WorkflowStep(
                    step_id=step_id,
                    agent=agent_role,
                    instruction=step_info.get("instruction", "")
                ))
                step_id += 1
        else:
            # Default workflow if planning fails
            steps = [
                WorkflowStep(step_id=1, agent=AgentRole.TRIAGE, instruction=f"Classify and prioritize: {workflow.user_request}"),
                WorkflowStep(step_id=2, agent=AgentRole.RESEARCH, instruction=f"Research relevant data for: {workflow.user_request}"),
                WorkflowStep(step_id=3, agent=AgentRole.COMPLIANCE, instruction=f"Check compliance requirements for: {workflow.user_request}"),
                WorkflowStep(step_id=4, agent=AgentRole.REVIEW, instruction="Review all findings and identify gaps"),
                WorkflowStep(step_id=5, agent=AgentRole.OUTPUT, instruction="Create final response for user"),
            ]
        
        return steps
    
    def _execute_step(self, workflow: Workflow, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step.status = "in_progress"
        step.started_at = datetime.now()
        
        # Gather context from previous steps
        context = {}
        for prev_step in workflow.steps:
            if prev_step.step_id < step.step_id and prev_step.output_data:
                context[prev_step.agent.value] = prev_step.output_data
        
        # Add user request to context
        context["user_request"] = workflow.user_request
        
        # Determine knowledge query
        knowledge_query = None
        if get_agent_config(step.agent).can_query_knowledge:
            knowledge_query = workflow.user_request
        
        # Execute the agent
        result = self.executor.execute(
            step.agent,
            step.instruction,
            context=context,
            knowledge_query=knowledge_query
        )
        
        step.completed_at = datetime.now()
        
        if result["success"]:
            step.status = "completed"
            step.output_data = result
        else:
            step.status = "failed"
            step.error = result.get("error", "Unknown error")
        
        # Add to conversation history
        workflow.conversation_history.append({
            "step_id": step.step_id,
            "agent": step.agent.value,
            "instruction": step.instruction,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def _check_if_revision_needed(self, workflow: Workflow) -> bool:
        """Check if the review agent requested revisions."""
        for step in workflow.steps:
            if step.agent == AgentRole.REVIEW and step.output_data:
                parsed = step.output_data.get("parsed", {})
                if parsed:
                    # Check if review agent says more work is needed
                    additional_work = parsed.get("additional_work_needed", [])
                    ready_for_output = parsed.get("ready_for_output", True)
                    return bool(additional_work) or not ready_for_output
        return False
    
    def _add_revision_steps(self, workflow: Workflow) -> List[WorkflowStep]:
        """Add additional steps based on review agent feedback."""
        new_steps = []
        next_step_id = len(workflow.steps) + 1
        
        # Find the review step
        for step in workflow.steps:
            if step.agent == AgentRole.REVIEW and step.output_data:
                parsed = step.output_data.get("parsed", {})
                if parsed:
                    for work_item in parsed.get("additional_work_needed", []):
                        agent_name = work_item.get("agent", "RESEARCH").upper()
                        try:
                            agent_role = AgentRole[agent_name]
                        except KeyError:
                            agent_role = AgentRole.RESEARCH
                        
                        new_steps.append(WorkflowStep(
                            step_id=next_step_id,
                            agent=agent_role,
                            instruction=work_item.get("task", "")
                        ))
                        next_step_id += 1
        
        # Add another review step if we added work
        if new_steps:
            new_steps.append(WorkflowStep(
                step_id=next_step_id,
                agent=AgentRole.REVIEW,
                instruction="Review the additional findings and determine if analysis is complete"
            ))
        
        return new_steps
    
    def run_workflow(self, workflow: Workflow, stream_callback=None) -> Workflow:
        """Run a complete workflow with agent collaboration."""
        workflow.state = WorkflowState.IN_PROGRESS
        
        # Plan the workflow
        if stream_callback:
            stream_callback("planning", "Orchestrator is planning the workflow...")
        
        workflow.steps = self._plan_workflow(workflow)
        
        # Execute each step
        while workflow.iteration_count < workflow.max_iterations:
            workflow.iteration_count += 1
            
            for step in workflow.steps:
                if step.status == "pending":
                    if stream_callback:
                        stream_callback(
                            "executing",
                            f"[{step.agent.value}] {step.instruction[:100]}..."
                        )
                    
                    self._execute_step(workflow, step)
                    
                    if stream_callback:
                        status = "✓" if step.status == "completed" else "✗"
                        stream_callback(
                            "step_complete",
                            f"[{status}] {step.agent.value} completed"
                        )
            
            # Check if review agent requested revisions
            if self._check_if_revision_needed(workflow):
                if stream_callback:
                    stream_callback("revision", "Review agent requested additional analysis...")
                
                new_steps = self._add_revision_steps(workflow)
                workflow.steps.extend(new_steps)
                workflow.state = WorkflowState.NEEDS_REVISION
            else:
                break
        
        # Generate final output
        output_steps = [s for s in workflow.steps if s.agent == AgentRole.OUTPUT and s.status == "completed"]
        if output_steps:
            workflow.final_output = output_steps[-1].output_data.get("raw_response", "")
        else:
            # Run output agent if not already done
            output_step = WorkflowStep(
                step_id=len(workflow.steps) + 1,
                agent=AgentRole.OUTPUT,
                instruction="Create final response synthesizing all agent findings"
            )
            workflow.steps.append(output_step)
            self._execute_step(workflow, output_step)
            workflow.final_output = output_step.output_data.get("raw_response", "")
        
        workflow.state = WorkflowState.COMPLETED
        
        if stream_callback:
            stream_callback("complete", "Workflow completed!")
        
        return workflow
    
    def get_workflow_summary(self, workflow: Workflow) -> Dict[str, Any]:
        """Get a summary of a workflow execution."""
        return {
            "workflow_id": workflow.workflow_id,
            "user_request": workflow.user_request,
            "state": workflow.state.value,
            "iterations": workflow.iteration_count,
            "steps_executed": len([s for s in workflow.steps if s.status == "completed"]),
            "steps_failed": len([s for s in workflow.steps if s.status == "failed"]),
            "agents_involved": list(set(s.agent.value for s in workflow.steps)),
            "final_output": workflow.final_output,
            "conversation_history": workflow.conversation_history
        }
