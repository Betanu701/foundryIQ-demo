# AI FoundryIQ Demo

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Betanu701/foundryIQ-demo)

A Python-based AI demo project that ingests business documents into Azure AI Search with vector embeddings and provides natural language querying via GPT-4.1.

## Features

- **Document Ingestion**: Automatically processes CSV, Excel, Word, and PDF files
- **Vector Search**: Uses Azure OpenAI embeddings for semantic search
- **Natural Language Queries**: Chat with your documents using GPT-4.1
- **React Frontend**: Simple chat interface to ask questions
- **Multi-Agent Support**: Orchestrated agents for complex queries

---

## 🚀 Deployment Options

Choose the deployment method that works best for you:

| Method | Best For | Time | Prerequisites |
|--------|----------|------|---------------|
| [**GitHub Codespaces**](#option-1-github-codespaces-easiest) | Quick demos, no local setup | 10 min | Azure subscription |
| [**Interactive Wizard**](#option-2-interactive-setup-wizard) | Guided local setup | 15 min | Python 3.10+, Azure CLI |
| [**Manual Setup**](#option-3-manual-setup) | Full control, learning | 20 min | Python 3.10+, Node.js 18+ |

---

## Option 1: GitHub Codespaces (Easiest)

**No local installation required.** Run everything in the browser.

### Quick Start

1. Click the badge above or go to: [Open in Codespaces](https://codespaces.new/Betanu701/foundryIQ-demo)
2. Wait for the container to build (~2 minutes)
3. Open `deploy_foundryiq.ipynb` in the Codespaces editor
4. Run each cell in order (Shift+Enter)

The notebook will:
- Log you into Azure (device code flow)
- Discover your Azure AI resources
- Create the search index
- Process and index your documents
- Test the system with sample queries

📖 **Detailed Guide:** See [docs/Generic_Getting_Started.md](docs/Generic_Getting_Started.md)

---

## Option 2: Interactive Setup Wizard

**Guided setup** with prompts for each step.

```bash
# Clone the repository
git clone https://github.com/Betanu701/foundryIQ-demo.git
cd foundryIQ-demo

# Run the interactive wizard
python3 docs/setup_wizard.py
```

**Wizard features:**
- Collects your company information upfront
- Presents each prompt one at a time
- Handles manual steps with clear instructions
- Lets you skip optional steps
- Tracks progress and allows resuming

```bash
# Options
python3 docs/setup_wizard.py --list-steps      # List all steps
python3 docs/setup_wizard.py --resume 5        # Resume from step 5
```

📖 **Detailed Guide:** See [docs/Generic_Getting_Started.md](docs/Generic_Getting_Started.md)

---

## Option 3: Manual Setup

**Full control** over each step.

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Azure subscription with:
  - Azure AI Services (OpenAI)
  - Azure AI Search

### Step 1: Clone and Configure

```bash
git clone https://github.com/Betanu701/foundryIQ-demo.git
cd foundryIQ-demo

# Copy environment template
cp .env.example .env
```

### Step 2: Get Azure Credentials

```bash
# Login to Azure
az login

# Get your AI Services endpoint and key
az cognitiveservices account show --name YOUR_AI_SERVICE --resource-group YOUR_RG --query properties.endpoint
az cognitiveservices account keys list --name YOUR_AI_SERVICE --resource-group YOUR_RG

# Get your Search service endpoint and key
az search admin-key show --service-name YOUR_SEARCH --resource-group YOUR_RG
```

Edit `.env` with your credentials:
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT` - GPT-4.1 deployment name
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` - Embedding model deployment
- `AZURE_SEARCH_ENDPOINT` - Azure AI Search endpoint
- `AZURE_SEARCH_API_KEY` - Azure AI Search API key

### Step 3: Install Dependencies and Ingest

```bash
pip install -r requirements.txt
python3 -m src.ingest
```

### Step 4: Run the Application

```bash
# Terminal 1: Start API server
uvicorn src.api:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend && npm install && npm run dev
```

Open http://localhost:5173 in your browser.

📖 **Detailed Guide:** See [docs/Generic_Getting_Started.md](docs/Generic_Getting_Started.md)

---

## 🎯 Running a Demo

See **[docs/Demo_Script.md](docs/Demo_Script.md)** for a complete walkthrough of how to demo this application, including:
- Setup checklist
- Talking points
- Sample queries to showcase
- Tips for audience engagement

---

## 🧹 Cleanup

When finished, clean up Azure resources:

```bash
python3 docs/teardown.py
```

See [docs/Teardown_Instructions.md](docs/Teardown_Instructions.md) for detailed cleanup steps.

---

## Project Structure

```
foundryIQ-demo/
├── src/
│   ├── api.py                 # FastAPI server
│   ├── azure_search_client.py # Azure AI Search operations
│   ├── chat_service.py        # GPT-4.1 RAG implementation
│   ├── config.py              # Configuration settings
│   ├── document_processor.py  # File parsing (CSV, Excel, Word, PDF)
│   ├── embeddings.py          # Azure OpenAI embeddings
│   └── ingest.py              # Document ingestion script
├── frontend/
│   └── src/App.jsx            # React chat component
├── docs/
│   ├── Generic_Getting_Started.md  # Detailed setup guide
│   ├── Demo_Script.md              # Demo walkthrough
│   └── Teardown_Instructions.md    # Cleanup guide
├── files/                     # Source documents to ingest
├── deploy_foundryiq.ipynb     # Codespaces deployment notebook
└── Agent_Instructions.md      # Azure AI Foundry agent setup
```

---

## Creating an Azure AI Foundry Agent

Want to use this as a grounded agent in Azure AI Foundry? See **[Agent_Instructions.md](Agent_Instructions.md)** for:
- System prompt to copy/paste
- Grounding configuration
- Sample queries to test
- Demo tips

---

## API Endpoints

- `GET /` - Health check
- `POST /chat` - Chat with documents

### Example API Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What products are in the catalog?"}'
```

---

## License

MIT
