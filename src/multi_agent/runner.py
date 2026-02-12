"""Command-line runner for multi-agent workflows."""

import argparse
import os
import sys
from typing import Optional
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from multi_agent.orchestrator import WorkflowOrchestrator


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


def print_banner():
    """Print a nice banner."""
    print("\n" + "="*70)
    print("  FoundryIQ Multi-Agent Workflow System")
    print("  Powered by Azure AI Foundry")
    print("="*70 + "\n")


def stream_callback(event_type: str, message: str):
    """Callback for streaming workflow updates."""
    icons = {
        "planning": "🎯",
        "executing": "⚙️",
        "step_complete": "  ",
        "revision": "🔄",
        "complete": "✅"
    }
    icon = icons.get(event_type, "→")
    print(f"{icon} {message}")


def run_interactive():
    """Run in interactive mode."""
    print_banner()
    
    # Load environment
    load_dotenv()
    
    # Initialize search client
    search_client = None
    try:
        search_client = SearchClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            index_name=os.getenv("AZURE_SEARCH_INDEX", "foundryiq-documents"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
        )
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to search: {e}")
    
    orchestrator = WorkflowOrchestrator(search_client)
    
    print("Available demo scenarios:")
    print("-" * 40)
    for key, scenario in DEMO_SCENARIOS.items():
        print(f"  {key}: {scenario['name']}")
    print("-" * 40)
    print("\nEnter a scenario name, or type your own request.")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("🗣️  You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        # Check if it's a scenario name
        if user_input.lower() in DEMO_SCENARIOS:
            scenario = DEMO_SCENARIOS[user_input.lower()]
            print(f"\n📋 Running scenario: {scenario['name']}")
            print(f"   Request: {scenario['request'][:100]}...\n")
            request = scenario["request"]
        else:
            request = user_input
        
        # Create and run workflow
        print("\n" + "-"*50)
        workflow = orchestrator.create_workflow(request)
        
        try:
            workflow = orchestrator.run_workflow(workflow, stream_callback)
            
            # Print summary
            print("\n" + "="*50)
            print("📊 WORKFLOW SUMMARY")
            print("="*50)
            
            summary = orchestrator.get_workflow_summary(workflow)
            print(f"Workflow ID: {summary['workflow_id']}")
            print(f"Iterations: {summary['iterations']}")
            print(f"Steps Executed: {summary['steps_executed']}")
            print(f"Agents Involved: {', '.join(summary['agents_involved'])}")
            
            print("\n" + "="*50)
            print("📝 FINAL OUTPUT")
            print("="*50 + "\n")
            print(summary['final_output'])
            
            # Show agent conversation
            print("\n" + "="*50)
            print("💬 AGENT CONVERSATION HISTORY")
            print("="*50)
            for entry in summary['conversation_history']:
                print(f"\n[Step {entry['step_id']}] {entry['agent'].upper()}")
                print(f"Instruction: {entry['instruction']}")
                if entry['result'].get('success'):
                    response = entry['result'].get('raw_response', '')
                    if len(response) > 300:
                        response = response[:300] + "..."
                    print(f"Response: {response}")
                else:
                    print(f"Error: {entry['result'].get('error')}")
            
        except Exception as e:
            print(f"\n❌ Error running workflow: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n")


def run_scenario(scenario_name: str):
    """Run a specific scenario."""
    print_banner()
    
    if scenario_name not in DEMO_SCENARIOS:
        print(f"❌ Unknown scenario: {scenario_name}")
        print(f"Available: {', '.join(DEMO_SCENARIOS.keys())}")
        return
    
    # Load environment
    load_dotenv()
    
    # Initialize search client
    search_client = None
    try:
        search_client = SearchClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            index_name=os.getenv("AZURE_SEARCH_INDEX", "foundryiq-documents"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
        )
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to search: {e}")
    
    orchestrator = WorkflowOrchestrator(search_client)
    scenario = DEMO_SCENARIOS[scenario_name]
    
    print(f"📋 Running scenario: {scenario['name']}")
    print(f"   Request: {scenario['request']}\n")
    
    workflow = orchestrator.create_workflow(scenario["request"])
    workflow = orchestrator.run_workflow(workflow, stream_callback)
    
    summary = orchestrator.get_workflow_summary(workflow)
    
    print("\n" + "="*50)
    print("📝 FINAL OUTPUT")
    print("="*50 + "\n")
    print(summary['final_output'])


def main():
    parser = argparse.ArgumentParser(description="FoundryIQ Multi-Agent Workflow Runner")
    parser.add_argument(
        "--scenario", "-s",
        choices=list(DEMO_SCENARIOS.keys()),
        help="Run a specific demo scenario"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available scenarios"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("\nAvailable Demo Scenarios:")
        print("-" * 50)
        for key, scenario in DEMO_SCENARIOS.items():
            print(f"\n{key}:")
            print(f"  Name: {scenario['name']}")
            print(f"  Request: {scenario['request'][:100]}...")
        return
    
    if args.scenario:
        run_scenario(args.scenario)
    else:
        run_interactive()


if __name__ == "__main__":
    main()
