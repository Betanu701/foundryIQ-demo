# FoundryIQ Demo - Generic Setup Guide

This guide walks you through creating a complete AI-powered document assistant using Azure AI services. Follow these prompts with GitHub Copilot to build your own FoundryIQ demo from scratch.

---

## 🚀 Quick Start: Interactive Setup Wizard

For the easiest setup experience, use our interactive wizard that guides you through each step:

```bash
python3 setup_wizard.py
```

**Wizard features:**
- Collects your company information upfront
- Presents each prompt one at a time
- Handles manual steps (like M365 Copilot) with clear instructions
- Lets you skip optional steps
- Tracks progress and allows resuming

**Options:**
```bash
# List all steps
python3 setup_wizard.py --list-steps

# Pre-configure company info
python3 setup_wizard.py --company "Acme Corp" --industry "Manufacturing"

# Resume from a specific step
python3 setup_wizard.py --resume 5
```

---

## 🧹 Teardown: Clean Up Resources

When you're done with the demo, use the teardown script to remove Azure resources and local files.

```bash
python3 teardown.py
```

The interactive script will prompt you for **each resource**, letting you choose what to keep or delete.

👉 **See [Teardown_Instructions.md](Teardown_Instructions.md) for detailed cleanup options and manual steps.**

---

## Manual Setup (Alternative)

If you prefer to run through the prompts manually, follow the sections below.

---

## Prerequisites

### 1. Azure Resources Required

Before starting, ensure you have:
- An **Azure subscription** with access to create resources
- **Azure AI Foundry** (formerly Azure OpenAI) with:
  - A GPT-4 or GPT-4.1 deployment
  - A text-embedding-3-small deployment
- **Azure AI Search** service (Basic tier or higher for vector search)
- **Azure CLI** installed and logged in (`az login`)

> **Note:** If you don't have these resources, GitHub Copilot can help you create them. See the "Create Azure Resources" section below.

### 2. Generate Sample Business Documents (M365 Copilot)

Before building the application, you need sample documents to ingest. Use Microsoft 365 Copilot to generate realistic business documents.

**Open M365 Copilot and use this prompt:**

```
Create 50 fake or mocked-up files for a fictional company called [YOUR_COMPANY_NAME] that would represent important documents related to their core business practices.

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

Convert into actual CSV/XLSX, PDF, and DOCX files with realistic data.
Provide as a zipped bundle of all files.
```

**After generating:**
1. Download the ZIP file from M365 Copilot
2. Extract the contents
3. Copy all files to the `/files` folder in your project repository

---

## Setup Prompts for GitHub Copilot

### Prompt 1: Initialize the Project

```
Create a new Python project for an AI Document Assistant Demo called FoundryIQ. Include:
- src/ folder with __init__.py
- tests/ folder with basic test structure  
- requirements.txt with: fastapi, uvicorn, python-dotenv, azure-search-documents, openai, pandas, openpyxl, python-docx, PyPDF2
- .gitignore for Python projects
- .env.example template for Azure credentials
- README.md with setup instructions
- files/ folder (empty, for document uploads)

Do not create a virtual environment yet.
```

---

### Prompt 2: Create Azure Resources (Optional)

*Use this if you don't already have Azure AI resources:*

```
Using Azure CLI, help me create the following resources for the FoundryIQ demo:

1. Create a resource group for the project
2. Create an Azure AI Search service (Basic tier) with a unique name
3. Create an Azure OpenAI resource (or Azure AI Foundry)
4. Deploy these models to the OpenAI resource:
   - gpt-4 or gpt-4.1 for chat
   - text-embedding-3-small for embeddings
5. Output all the endpoints and keys needed for the .env file

Use my current Azure subscription.
```

---

### Prompt 3: Discover Azure Resources and Configure

*Use this if you already have Azure resources:*

```
Using Azure CLI, discover my existing Azure resources and configure the project:

1. List all Azure OpenAI / Cognitive Services resources in my subscription
2. List all Azure AI Search services in my subscription
3. Let me select which resources to use
4. Retrieve the endpoints and API keys for the selected resources
5. List available model deployments in the OpenAI resource
6. Create the .env file with the retrieved credentials
7. Verify connectivity to both services
```

---

### Prompt 4: Build the Document Ingestion System

```
Build a document ingestion system for the FoundryIQ project:

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

Load configuration from .env file.
```

---

### Prompt 5: Build the Chat Service and API

```
Build the chat service and API for FoundryIQ:

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
- Provide defaults where appropriate
```

---

### Prompt 6: Run Document Ingestion

```
Run the document ingestion process:

1. Activate the Python virtual environment (create if needed)
2. Install all dependencies from requirements.txt
3. Run the ingestion script to process all files in /files folder
4. Verify the documents were indexed by querying Azure AI Search
5. Report the total number of document chunks indexed
```

---

### Prompt 7: Build the React Frontend

```
Create a React frontend for the FoundryIQ chat interface:

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
- Support switching to deployed URL via environment variable
```

---

### Prompt 8: Test the Application Locally

```
Start and test the FoundryIQ application locally:

1. Start the FastAPI backend on port 8000
2. Start the React frontend dev server on port 5173
3. Open the frontend in a browser
4. Test with a sample query about the documents
5. Verify responses include source citations
```

---

### Prompt 9: Deploy to Azure (Optional)

```
Deploy the FoundryIQ API to Azure for demo purposes:

1. Create a Dockerfile for the FastAPI backend
2. Create an Azure Container Apps environment
3. Build and deploy the container to Azure Container Apps
4. Configure all environment variables from .env
5. Update CORS settings for production
6. Test the deployed API
7. Update the frontend to use the deployed API URL
8. Build the frontend for production
9. Provide the deployment URLs
```

---

### Prompt 10: Customize Agent Instructions for Your Company

```
Customize the agent instructions in docs/Generic_Agent_Instructions.md for my specific company:

**Company Information:**
- Company Name: [YOUR_COMPANY_NAME]
- Industry: [YOUR_INDUSTRY - e.g., Financial Services, Healthcare, Manufacturing, Technology]
- Primary Business: [BRIEF DESCRIPTION - e.g., "Tax compliance software", "Healthcare analytics platform"]

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

Show me a summary of the customizations made.
```

---

### Prompt 11: Create Agent Instructions from Scratch (Alternative)

*Use this instead of Prompt 10 if you prefer to generate fresh instructions rather than customizing the template:*

```
Analyze my ingested documents and create comprehensive agent instructions:

1. Scan the Azure AI Search index 'foundryiq-documents' to understand:
   - All document types and their content
   - Key business domains covered
   - Important entities (customers, products, metrics)
   - Common data patterns

2. Generate a complete Agent_Instructions.md file with:
   
   **System Prompt:**
   - Role definition specific to my business domain
   - Detailed knowledge base description based on actual documents
   - Response guidelines with citation requirements
   - 3 example interactions using real document data
   
   **Demo Prompts (10 prompts):**
   - 3 single-document queries (simple lookups)
   - 3 cross-document analysis queries
   - 2 executive summary / dashboard queries
   - 2 risk or compliance assessment queries
   
   Each prompt should:
   - Reference actual documents by name
   - Use realistic business scenarios
   - Include "Why it's powerful" explanation
   
   **Setup Instructions:**
   - Azure AI Foundry configuration steps
   - Field mapping guidance
   - Grounding settings recommendations

3. Save as Agent_Instructions.md in the project root
```

---

## Quick Start - Single Comprehensive Prompt

For experienced users, use this single prompt to generate the entire project:

```
Create a complete RAG (Retrieval Augmented Generation) demo application called FoundryIQ:

**Backend (Python/FastAPI):**
- Document processor for CSV, Excel, Word, and PDF files from /files folder
- Azure AI Search integration with vector embeddings
- Chat service using Azure OpenAI GPT for natural language queries
- FastAPI server with /chat, /health, and /documents/count endpoints
- Ingestion script to process and upload all documents

**Frontend (React/Vite):**
- Chat interface with message history
- Markdown rendering for responses
- Source document citations
- Suggestion buttons for common queries

**Features:**
- Hybrid search (keyword + vector)
- Multi-turn conversation support
- CORS enabled for frontend

**Setup:**
- Use Azure CLI to discover my existing Azure OpenAI and Azure AI Search resources
- Let me select which resources to use
- Create .env with retrieved credentials
- Run ingestion automatically after setup

Include Docker support for Azure Container Apps deployment.
```

---

## Environment Variables

Your `.env` file should contain:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://[your-resource].cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=[your-key]
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT=[your-gpt-deployment-name]
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://[your-service].search.windows.net
AZURE_SEARCH_API_KEY=[your-admin-key]
AZURE_SEARCH_INDEX_NAME=foundryiq-documents
```

---

## Troubleshooting

### Common Issues

1. **"API key not found" errors**
   - Run: `az login` to refresh Azure credentials
   - Verify .env file has correct values

2. **"Index not found" errors**
   - Run the ingestion script first
   - Check Azure AI Search in the portal

3. **Frontend shows blank screen**
   - Make sure Vite dev server is running (not static file server)
   - Check browser console for errors
   - Verify API_URL in App.jsx points to correct backend

4. **No search results**
   - Verify documents were ingested (check /documents/count endpoint)
   - Try a simpler search query
   - Check Azure AI Search index in portal

---

## Next Steps

After completing setup:

1. **Customize the documents** - Replace sample files with your actual business documents
2. **Tune the prompts** - Adjust system prompts for your use case
3. **Add authentication** - Implement Azure AD authentication for production
4. **Scale the deployment** - Configure auto-scaling for Azure Container Apps
5. **Create an AI Foundry agent** - Use the agent instructions to create a managed agent
