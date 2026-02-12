#!/usr/bin/env python3
"""
FoundryIQ Setup Wizard

An interactive setup wizard that guides users through building their FoundryIQ demo.
Reads prompts from the Getting Started guide and executes them step-by-step.

Usage:
    python setup_wizard.py
    python setup_wizard.py --company "Acme Corp" --industry "Manufacturing"
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class StepType(Enum):
    MANUAL = "manual"           # User must do something outside the system
    PROMPT = "prompt"           # A prompt to run in GitHub Copilot
    AUTOMATED = "automated"     # Can be run automatically via script
    INFO = "info"               # Just informational, no action needed


@dataclass
class SetupStep:
    """Represents a single step in the setup process."""
    number: int
    title: str
    description: str
    step_type: StepType
    prompt: Optional[str] = None
    manual_instructions: Optional[str] = None
    validation_command: Optional[str] = None
    skip_allowed: bool = True


# Define the setup steps
SETUP_STEPS = [
    SetupStep(
        number=0,
        title="Welcome & Configuration",
        description="Configure your company details for the FoundryIQ demo.",
        step_type=StepType.INFO,
    ),
    SetupStep(
        number=1,
        title="Generate Sample Documents (M365 Copilot)",
        description="Use Microsoft 365 Copilot to generate realistic business documents.",
        step_type=StepType.MANUAL,
        manual_instructions="""
This step requires Microsoft 365 Copilot. 

1. Open Microsoft 365 Copilot in your browser or Teams
2. Copy and paste the prompt below
3. Download the generated ZIP file
4. Extract the files

Press Enter when you're ready to see the prompt...""",
        prompt='''Create 50 fake or mocked-up files for a fictional company called {company_name} that would represent important documents related to their core business practices.

Requirements:
- Each file should have at least 10-20 sample records where applicable
- Create a variety of file types: CSV, XLSX, PDF, and DOCX
- Include documents across these categories:

**Customer & Vendor Data:**
- Customer Master (accounts, contacts, billing)
- Vendor Master (suppliers, payment terms)
- Partner Integrations

**Operations & Support:**
- Support Cases (tickets, priorities, status)
- SLA Metrics
- Incident Log
- Change Requests
- Release Calendar

**Compliance & Security:**
- Compliance Filing Calendar
- Security Policies
- Access Control Lists
- Vulnerability Register
- Audit Findings

**Products & Revenue:**
- Product Catalog
- Pricing Rules
- Revenue Recognition
- Renewal Pipeline

**Internal Operations:**
- Training Completion
- DR Test Results
- Backup Status
- Business Continuity Plan

Convert into actual CSV/XLSX, PDF, and DOCX files with realistic data for a {industry} company.
Provide as a zipped bundle of all files.''',
    ),
    SetupStep(
        number=2,
        title="Initialize the Project",
        description="Create the Python project structure with GitHub Copilot.",
        step_type=StepType.PROMPT,
        prompt='''Create a new Python project for an AI Document Assistant Demo called FoundryIQ. Include:
- src/ folder with __init__.py
- tests/ folder with basic test structure  
- requirements.txt with: fastapi, uvicorn, python-dotenv, azure-search-documents, openai, pandas, openpyxl, python-docx, PyPDF2
- .gitignore for Python projects
- .env.example template for Azure credentials
- README.md with setup instructions
- files/ folder (empty, for document uploads)

Do not create a virtual environment yet.''',
    ),
    SetupStep(
        number=3,
        title="Copy Files to Project",
        description="Move the generated documents to the /files folder in your project.",
        step_type=StepType.MANUAL,
        manual_instructions="""
Copy your generated business documents to the project:

1. Locate your downloaded/extracted files from M365 Copilot
2. Copy ALL files (CSV, XLSX, PDF, DOCX) to: {project_path}/files/
3. The /files folder was created in the previous step

Commands to help:
    cp ~/Downloads/your-files/* {project_path}/files/

Press Enter after you've copied the files...""",
        validation_command="ls -la {project_path}/files/ | head -20",
    ),
    SetupStep(
        number=4,
        title="Discover Azure Resources",
        description="Use Azure CLI to find your Azure AI resources and configure the project.",
        step_type=StepType.PROMPT,
        prompt='''Using Azure CLI, discover my existing Azure resources and configure the project:

1. List all Azure OpenAI / Cognitive Services resources in my subscription
2. List all Azure AI Search services in my subscription
3. Let me select which resources to use
4. Retrieve the endpoints and API keys for the selected resources
5. List available model deployments in the OpenAI resource
6. Create the .env file with the retrieved credentials
7. Verify connectivity to both services''',
    ),
    SetupStep(
        number=5,
        title="Build Document Ingestion System",
        description="Create the document processing and Azure AI Search integration.",
        step_type=StepType.PROMPT,
        prompt='''Build a document ingestion system for the FoundryIQ project:

**Document Processor (src/document_processor.py):**
- Read CSV files and extract each row as a document chunk
- Read Excel (.xlsx) files and extract each row as a document chunk
- Read Word (.docx) files and extract paragraphs, splitting large documents into chunks
- Read PDF files and extract text, splitting into chunks
- Each chunk should include: id, file_name, file_type, content, metadata, title

**Azure Search Client (src/azure_search_client.py):**
- Create an index with fields: id, file_name, file_type, content, metadata, title, content_vector
- Configure vector search with HNSW algorithm for the content_vector field
- Support hybrid search (keyword + vector)
- Methods: create_index(), upload_documents(), search()

**Embeddings Generator (src/embeddings.py):**
- Use Azure OpenAI to generate embeddings with text-embedding-3-small
- Batch processing for efficiency (25 documents per batch)

**Ingestion Script (src/ingest.py):**
- Process all files in the /files folder
- Generate embeddings for each document chunk
- Upload to Azure AI Search with vectors
- Print progress and summary

Load configuration from .env file.''',
    ),
    SetupStep(
        number=6,
        title="Build Chat Service and API",
        description="Create the RAG chat service and FastAPI endpoints.",
        step_type=StepType.PROMPT,
        prompt='''Build the chat service and API for FoundryIQ:

**Chat Service (src/chat_service.py):**
- Query Azure AI Search using hybrid search (keyword + vector)
- Build context from top search results
- Call Azure OpenAI GPT model with:
  - System prompt explaining the assistant's role
  - Retrieved document context
  - User's question
  - Chat history for multi-turn conversations
- Return answer with source citations

**FastAPI Server (src/api.py):**
- POST /chat endpoint accepting: question, chat_history (optional)
- GET /health endpoint for health checks
- GET /documents/count endpoint to show indexed document count
- Enable CORS for all origins (for demo purposes)
- Run on port 8000

**Configuration (src/config.py):**
- Load all Azure credentials from environment variables
- Provide defaults where appropriate''',
    ),
    SetupStep(
        number=7,
        title="Run Document Ingestion",
        description="Process and upload all documents to Azure AI Search.",
        step_type=StepType.PROMPT,
        prompt='''Run the document ingestion process:

1. Activate the Python virtual environment (create if needed)
2. Install all dependencies from requirements.txt
3. Run the ingestion script to process all files in /files folder
4. Verify the documents were indexed by querying Azure AI Search
5. Report the total number of document chunks indexed''',
    ),
    SetupStep(
        number=8,
        title="Build React Frontend",
        description="Create the chat interface frontend.",
        step_type=StepType.PROMPT,
        prompt='''Create a React frontend for the FoundryIQ chat interface:

**Setup:**
- Use Vite for the React project in /frontend folder
- Install dependencies: react, react-dom, react-markdown

**Components (src/App.jsx):**
- Chat interface with message history
- Input form for questions
- Display AI responses with markdown formatting
- Show source document citations for each response
- Suggestion buttons for common queries
- Loading state while waiting for response
- Error handling for API failures

**Styling (src/index.css):**
- Modern, clean design with CSS variables
- Purple/blue gradient header
- Chat bubbles for user/assistant messages
- Mobile responsive layout

**Configuration:**
- API URL should point to http://localhost:8000 for local development
- Support switching to deployed URL via environment variable''',
    ),
    SetupStep(
        number=9,
        title="Test the Application",
        description="Start the backend and frontend, and test the application.",
        step_type=StepType.PROMPT,
        prompt='''Start and test the FoundryIQ application locally:

1. Start the FastAPI backend on port 8000
2. Start the React frontend dev server on port 5173
3. Open the frontend in a browser
4. Test with a sample query about the documents
5. Verify responses include source citations''',
    ),
    SetupStep(
        number=10,
        title="Customize Agent Instructions",
        description="Generate customized agent instructions based on your documents.",
        step_type=StepType.PROMPT,
        prompt='''Customize the agent instructions in docs/Generic_Agent_Instructions.md for my specific company:

**Company Information:**
- Company Name: {company_name}
- Industry: {industry}
- Primary Business: {business_description}

**Document Analysis:**
1. Scan the /files folder and list all document types that were ingested
2. Categorize the documents into logical business domains
3. Identify key entities mentioned (customer IDs, product names, metrics, etc.)

**Customization Tasks:**
1. Update the system prompt in Generic_Agent_Instructions.md:
   - Replace generic company references with my company name
   - Update the "Knowledge Base Categories" section to match my actual documents
   - Add industry-specific terminology and context
   - Adjust the tone to match my company's communication style

2. Create 10 customized demo prompts that:
   - Reference actual document names from my /files folder
   - Use real entity names/IDs found in the documents
   - Address business scenarios relevant to my industry
   - Showcase the specific data available in my knowledge base

3. Update the example interactions to use realistic queries and responses based on my documents

4. Save the customized version as Agent_Instructions.md (not in /docs)

Show me a summary of the customizations made.''',
    ),
    SetupStep(
        number=11,
        title="Deploy to Azure (Optional)",
        description="Deploy the application to Azure Container Apps for demo access.",
        step_type=StepType.PROMPT,
        skip_allowed=True,
        prompt='''Deploy the FoundryIQ API to Azure for demo purposes:

1. Create a Dockerfile for the FastAPI backend
2. Create an Azure Container Apps environment
3. Build and deploy the container to Azure Container Apps
4. Configure all environment variables from .env
5. Update CORS settings for production
6. Test the deployed API
7. Update the frontend to use the deployed API URL
8. Build the frontend for production
9. Provide the deployment URLs''',
    ),
    SetupStep(
        number=12,
        title="Setup Complete!",
        description="Your FoundryIQ demo is ready to use.",
        step_type=StepType.INFO,
    ),
]


class SetupWizard:
    """Interactive setup wizard for FoundryIQ."""
    
    def __init__(self, company_name: str = None, industry: str = None, 
                 business_description: str = None, project_path: str = None):
        self.company_name = company_name
        self.industry = industry
        self.business_description = business_description
        self.project_path = project_path or os.getcwd()
        self.completed_steps = set()
        
    def print_header(self, text: str):
        """Print a formatted header."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")
        
    def print_step_header(self, step: SetupStep):
        """Print the header for a setup step."""
        print(f"\n{Colors.CYAN}{Colors.BOLD}Step {step.number}: {step.title}{Colors.END}")
        print(f"{Colors.CYAN}{'-'*50}{Colors.END}")
        print(f"{step.description}\n")
        
    def print_prompt(self, prompt: str):
        """Print a formatted prompt for the user to copy."""
        print(f"{Colors.GREEN}{'─'*50}{Colors.END}")
        print(f"{Colors.GREEN}📋 PROMPT TO USE IN GITHUB COPILOT:{Colors.END}")
        print(f"{Colors.GREEN}{'─'*50}{Colors.END}")
        print(f"\n{prompt}\n")
        print(f"{Colors.GREEN}{'─'*50}{Colors.END}")
        
    def print_manual_instructions(self, instructions: str):
        """Print manual instructions for the user."""
        print(f"{Colors.YELLOW}📝 MANUAL STEPS REQUIRED:{Colors.END}")
        print(instructions)
        
    def format_prompt(self, prompt: str) -> str:
        """Replace placeholders in prompt with actual values."""
        return prompt.format(
            company_name=self.company_name or "[YOUR_COMPANY_NAME]",
            industry=self.industry or "[YOUR_INDUSTRY]",
            business_description=self.business_description or "[YOUR_BUSINESS_DESCRIPTION]",
            project_path=self.project_path,
        )
        
    def get_user_input(self, prompt: str, default: str = None) -> str:
        """Get input from user with optional default."""
        if default:
            user_prompt = f"{prompt} [{default}]: "
        else:
            user_prompt = f"{prompt}: "
        
        response = input(user_prompt).strip()
        return response if response else default
        
    def confirm(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no confirmation from user."""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{prompt} [{default_str}]: ").strip().lower()
        
        if not response:
            return default
        return response in ('y', 'yes')
        
    def wait_for_enter(self, message: str = "Press Enter to continue..."):
        """Wait for user to press Enter."""
        input(f"\n{Colors.BLUE}{message}{Colors.END}")
        
    def collect_company_info(self):
        """Collect company information from user."""
        self.print_header("FoundryIQ Setup Wizard")
        
        print("Let's configure your FoundryIQ demo. Please provide some information about your company.\n")
        
        self.company_name = self.get_user_input(
            "Company Name",
            self.company_name or "Acme Corporation"
        )
        
        print("\nIndustry options: Technology, Healthcare, Financial Services, Manufacturing, Retail, etc.")
        self.industry = self.get_user_input(
            "Industry",
            self.industry or "Technology"
        )
        
        self.business_description = self.get_user_input(
            "Brief business description (e.g., 'Cloud software platform')",
            self.business_description or "Enterprise software solutions"
        )
        
        print(f"\n{Colors.GREEN}✓ Configuration saved:{Colors.END}")
        print(f"  Company: {self.company_name}")
        print(f"  Industry: {self.industry}")
        print(f"  Business: {self.business_description}")
        print(f"  Project Path: {self.project_path}")
        
    def run_step(self, step: SetupStep) -> bool:
        """Run a single setup step. Returns True if completed, False if skipped."""
        self.print_step_header(step)
        
        if step.step_type == StepType.INFO:
            if step.number == 0:
                self.collect_company_info()
            elif step.number == 12:
                self.print_completion_message()
            self.wait_for_enter()
            return True
            
        elif step.step_type == StepType.MANUAL:
            # Show manual instructions
            if step.manual_instructions:
                formatted_instructions = self.format_prompt(step.manual_instructions)
                self.print_manual_instructions(formatted_instructions)
                self.wait_for_enter()
            
            # Show the prompt to copy
            if step.prompt:
                formatted_prompt = self.format_prompt(step.prompt)
                self.print_prompt(formatted_prompt)
                
                print(f"\n{Colors.YELLOW}Copy the prompt above and use it in M365 Copilot.{Colors.END}")
                self.wait_for_enter("Press Enter after you've completed the manual steps...")
            
            # Run validation if available
            if step.validation_command:
                if self.confirm("Would you like to verify the files were copied?"):
                    cmd = self.format_prompt(step.validation_command)
                    print(f"\nRunning: {cmd}")
                    os.system(cmd)
                    
            return True
            
        elif step.step_type == StepType.PROMPT:
            formatted_prompt = self.format_prompt(step.prompt)
            self.print_prompt(formatted_prompt)
            
            print(f"\n{Colors.CYAN}Instructions:{Colors.END}")
            print("1. Copy the prompt above")
            print("2. Paste it into GitHub Copilot Chat (Ctrl+Shift+I or Cmd+Shift+I)")
            print("3. Wait for Copilot to complete the task")
            print("4. Review and accept the generated code/files")
            
            self.wait_for_enter("Press Enter after Copilot has completed this step...")
            return True
            
        return False
        
    def print_completion_message(self):
        """Print the setup completion message."""
        print(f"""
{Colors.GREEN}{Colors.BOLD}🎉 Congratulations! Your FoundryIQ demo is ready!{Colors.END}

{Colors.BOLD}What was created:{Colors.END}
  ✓ Python FastAPI backend with document ingestion
  ✓ Azure AI Search index with vector embeddings
  ✓ React frontend chat interface
  ✓ Customized agent instructions for {self.company_name}

{Colors.BOLD}To run the application:{Colors.END}
  1. Start the backend:  cd {self.project_path} && python -m uvicorn src.api:app --port 8000
  2. Start the frontend: cd {self.project_path}/frontend && npm run dev
  3. Open: http://localhost:5173

{Colors.BOLD}To create an Azure AI Foundry agent:{Colors.END}
  1. Go to https://ai.azure.com
  2. Follow the instructions in Agent_Instructions.md

{Colors.BOLD}Demo prompts to try:{Colors.END}
  • "Give me an executive summary of our operational health"
  • "What products are in the catalog?"
  • "Show me any compliance issues or risks"
  • "What are the top 5 business risks right now?"

{Colors.YELLOW}Thank you for using FoundryIQ Setup Wizard!{Colors.END}
""")
        
    def run(self, start_from: int = 0):
        """Run the setup wizard from the specified step."""
        steps_to_run = [s for s in SETUP_STEPS if s.number >= start_from]
        total_steps = len(steps_to_run)
        
        for i, step in enumerate(steps_to_run):
            # Show progress
            print(f"\n{Colors.BLUE}[Progress: {i+1}/{total_steps}]{Colors.END}")
            
            # Ask if user wants to run or skip this step
            if step.number > 0 and step.number < 12 and step.skip_allowed:
                if not self.confirm(f"Run Step {step.number}: {step.title}?"):
                    print(f"{Colors.YELLOW}Skipping step {step.number}...{Colors.END}")
                    continue
            
            # Run the step
            completed = self.run_step(step)
            
            if completed:
                self.completed_steps.add(step.number)
                print(f"\n{Colors.GREEN}✓ Step {step.number} completed{Colors.END}")
            
            # Ask if user wants to continue
            if step.number < 11 and step.number > 0:
                if not self.confirm("Continue to next step?"):
                    print(f"\n{Colors.YELLOW}Setup paused at step {step.number}.{Colors.END}")
                    print(f"Run 'python setup_wizard.py --resume {step.number + 1}' to continue.")
                    return


def main():
    parser = argparse.ArgumentParser(
        description="FoundryIQ Setup Wizard - Interactive setup for your AI document assistant"
    )
    parser.add_argument(
        "--company", "-c",
        help="Company name for the demo"
    )
    parser.add_argument(
        "--industry", "-i",
        help="Industry (e.g., Technology, Healthcare, Manufacturing)"
    )
    parser.add_argument(
        "--business", "-b",
        help="Brief business description"
    )
    parser.add_argument(
        "--resume", "-r",
        type=int,
        default=0,
        help="Resume from step number"
    )
    parser.add_argument(
        "--list-steps", "-l",
        action="store_true",
        help="List all setup steps and exit"
    )
    
    args = parser.parse_args()
    
    if args.list_steps:
        print("\nFoundryIQ Setup Steps:")
        print("=" * 50)
        for step in SETUP_STEPS:
            skip_info = " (optional)" if step.skip_allowed and step.number > 0 else ""
            type_info = f"[{step.step_type.value}]"
            print(f"  {step.number:2d}. {step.title} {type_info}{skip_info}")
        print()
        return
    
    wizard = SetupWizard(
        company_name=args.company,
        industry=args.industry,
        business_description=args.business,
    )
    
    try:
        wizard.run(start_from=args.resume)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup interrupted. Your progress has been noted.{Colors.END}")
        print(f"Run 'python setup_wizard.py --resume N' to continue from step N.")


if __name__ == "__main__":
    main()
