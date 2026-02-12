# FoundryIQ Demo - Getting Started Prompts

This document contains the optimized prompts used to generate the FoundryIQ demo application. Use these prompts with GitHub Copilot or similar AI assistants to recreate this project.

---

## Prompt 1: Initialize the Project

**Original:**
> #new blank project that will be used to create an AI FoundryIQ Demo

**Optimized:**
> Create a new Python project for an AI FoundryIQ Demo. Include:
> - src/ folder with __init__.py and main.py
> - tests/ folder with basic test structure
> - requirements.txt with python-dotenv
> - .gitignore for Python projects
> - .env.example template
> - README.md with setup instructions

---

## Prompt 2: Build the Document Ingestion & Chat System

**Original:**
> Using my Azure AI Foundry Called Flinstones and my Azure AI Search called stone-fabrix-agent-connector ingest all files in the Files folder into Azure AI Search adding indexers, vectors and embeddings where necessary. Do not create a virtual environment and ingest the files directly. Enable natural language querying via language model GPT 4.1. Also create a simple React page to ask questions across these files and indexes in Azure AI Search

**Optimized:**
Build a RAG (Retrieval Augmented Generation) system with the following components:
**Backend (Python/FastAPI):**
- Document processor to read CSV, Excel (.xlsx), Word (.docx), and PDF files from the `files/` folder
- Azure AI Search client to create an index with vector search capabilities
- Embeddings generator using Azure OpenAI (text-embedding-3-small model)
- Chat service using GPT-4.1 for natural language querying with RAG
- FastAPI server with /chat endpoint and CORS enabled
- Ingestion script to process all files and upload to Azure AI Search
**Frontend (React/Vite):**
- Simple chat interface to ask questions
- Display AI responses with source document citations
- Suggestion buttons for common queries
**Azure Resources:**
- Azure AI Foundry: `Flinstones`
- Azure AI Search: `stone-fabrix-agent-connector`
- Index name: `foundryiq-documents`

---

## Prompt 3: Connect to Azure and Ingest Files

**Original:**
> Use the AZD commands and connect to my Azure subscription and use the following: Using my Azure AI Foundry Called Flinstones and my Azure AI Search called stone-fabrix-agent-connector to injest the files

**Optimized:**
> Connect to my Azure subscription using Azure CLI and:
> 1. Retrieve the API endpoint and key for Azure OpenAI resource `flinstones`
> 2. Retrieve the endpoint and admin key for Azure AI Search `stone-fabrix-agent-connector`
> 3. List available model deployments in the OpenAI resource
> 4. Create the .env file with the retrieved credentials
> 5. Run the ingestion script to process all files and upload to Azure AI Search with vector embeddings

---

## Prompt 4: Deploy to Azure

**Original:**
> Now deploy the light application you created to Azure so that I can use that for a Demo

**Optimized:**
> Deploy the application to Azure for demo purposes:
> 1. Create a Dockerfile for the FastAPI backend
> 2. Create an Azure Container Apps environment
> 3. Deploy the API to Azure Container Apps with all required environment variables
> 4. Update CORS to allow all origins for demo
> 5. Build the React frontend for production
> 6. Provide the deployment URLs for demo access

---

## Prompt 5: Verify Deployment

**Original:**
> Can you verify the deployment and the injested files

**Optimized:**
> Verify the deployment is working correctly:
> 1. Test the API health endpoint
> 2. Test the /chat endpoint with a sample question
> 3. Query Azure AI Search to confirm document count
> 4. Provide a summary of deployment status and URLs

---

## Prompt 6: Run the Frontend

**Original:**
> lets run the front end now

**Optimized:**
> Start the React frontend development server and open it in the browser

---

## Quick Start - Single Comprehensive Prompt

If you want to recreate this entire project with one prompt, use:

> Create a complete RAG (Retrieval Augmented Generation) demo application called FoundryIQ with:
>
> **Requirements:**
> - Python FastAPI backend with document ingestion for CSV, Excel, Word, and PDF files
> - Azure AI Search integration with vector embeddings (text-embedding-3-small)
> - Natural language chat using Azure OpenAI GPT-4.1
> - React frontend with Vite for asking questions about documents
> - Docker support for Azure Container Apps deployment
>
> **Azure Resources:**
> - Azure AI Foundry: `[YOUR_OPENAI_RESOURCE_NAME]`
> - Azure AI Search: `[YOUR_SEARCH_SERVICE_NAME]`
>
> **Features:**
> - Hybrid search (keyword + vector)
> - Source citation in responses
> - Chat history support
> - CORS enabled for frontend
>
> Use Azure CLI to retrieve credentials and run the ingestion automatically.

---

## Environment Variables Required

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://[resource].cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=[your-key]
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://[service].search.windows.net
AZURE_SEARCH_API_KEY=[your-key]
AZURE_SEARCH_INDEX_NAME=foundryiq-documents
```

---

## Deployment URLs

- **API**: https://foundryiq-api.orangegrass-cf402e05.eastus2.azurecontainerapps.io/
- **API Docs**: https://foundryiq-api.orangegrass-cf402e05.eastus2.azurecontainerapps.io/docs
- **Frontend (local)**: http://localhost:5173
