# AI FoundryIQ Demo

A Python-based AI demo project that ingests business documents into Azure AI Search with vector embeddings and provides natural language querying via GPT-4.1.

## Features

- **Document Ingestion**: Automatically processes CSV, Excel, Word, and PDF files
- **Vector Search**: Uses Azure OpenAI embeddings for semantic search
- **Natural Language Queries**: Chat with your documents using GPT-4.1
- **React Frontend**: Simple chat interface to ask questions

## Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Azure AI Foundry account (Flinstones)
- Azure AI Search service (stone-fabrix-agent-connector)

## Setup

### 1. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

Required environment variables:
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT` - GPT-4.1 deployment name
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` - Embedding model deployment
- `AZURE_SEARCH_ENDPOINT` - Azure AI Search endpoint
- `AZURE_SEARCH_API_KEY` - Azure AI Search API key

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Ingest Documents

Run the ingestion script to process all files and upload to Azure AI Search:

```bash
python3 -m src.ingest
```

### 4. Start the API Server

```bash
uvicorn src.api:app --reload --port 8000
```

### 5. Start the React Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

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
│   ├── src/
│   │   ├── App.jsx            # React chat component
│   │   ├── index.css          # Styles
│   │   └── main.jsx           # Entry point
│   ├── index.html
│   └── package.json
├── files/                     # Source documents to ingest
├── .env.example
├── requirements.txt
└── README.md
```

## Indexed Document Types

The system ingests and indexes:
- Customer Master data
- Product Catalog
- Tax Jurisdictions and Transactions
- Compliance Filing Calendar
- Exemption Certificates
- Support Cases
- Revenue Recognition
- Internal Audit Findings
- Product Roadmap
- And 40+ more document types...

## API Endpoints

- `GET /` - Health check
- `POST /chat` - Chat with documents

### Example API Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What products are in the catalog?"}'
```
