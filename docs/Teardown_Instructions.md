# FoundryIQ Teardown Guide

This guide helps you clean up all resources created by the FoundryIQ demo when you're done.

---

## Quick Teardown

Run the interactive teardown script:

```bash
python3 teardown.py
```

The script will prompt you for each resource, letting you choose what to keep or delete.

---

## Teardown Options

```bash
# Interactive mode (recommended) - prompts before each deletion
python3 teardown.py

# Remove everything without prompts
python3 teardown.py --all

# Preview what would be deleted (no actual changes)
python3 teardown.py --dry-run

# Only remove local files (keep Azure resources)
python3 teardown.py --local-only

# Only remove Azure resources (keep local files)  
python3 teardown.py --azure-only

# Combine options
python3 teardown.py --dry-run --azure-only
```

---

## What Gets Cleaned Up

### Step 1: Stop Local Services

| Service | Port | Description |
|---------|------|-------------|
| FastAPI Backend | 8000 | The RAG chat API |
| Vite Frontend | 5173 | React development server |
| HTTP Server | Various | Any Python http.server instances |

**Keep or Remove?**
- **Keep** if you want to continue using the demo locally
- **Remove** to free up ports and stop background processes

---

### Step 2: Azure AI Search Index

| Resource | Name | Description |
|----------|------|-------------|
| Search Index | `foundryiq-documents` | Contains all indexed document chunks and embeddings |

**Keep or Remove?**
- **Keep** if you want to preserve your indexed documents and continue using the agent
- **Remove** if you're done with the demo (can be re-ingested later)

**Manual removal:**
```bash
# Delete just the index (keeps the search service)
curl -X DELETE "https://<your-search-service>.search.windows.net/indexes/foundryiq-documents?api-version=2023-11-01" \
  -H "api-key: <your-admin-key>"
```

---

### Step 3: Azure Container Apps

| Resource | Name | Description |
|----------|------|-------------|
| Container App | `foundryiq-api` | Deployed FastAPI backend |
| Container Environment | `foundryiq-env` | Container Apps hosting environment |

**Keep or Remove?**
- **Keep** if you want to continue accessing the deployed API
- **Remove** to stop incurring hosting costs

**Manual removal:**
```bash
# Delete the container app
az containerapp delete --name foundryiq-api --resource-group <your-rg> --yes

# Delete the environment (after deleting all apps in it)
az containerapp env delete --name foundryiq-env --resource-group <your-rg> --yes
```

---

### Step 4: Blob Storage

| Resource | Description |
|----------|-------------|
| Storage Account | Contains uploaded source documents for citations |
| Container | `documents` - holds the actual files |

**Keep or Remove?**
- **Keep** if you want source document links to continue working
- **Remove** if you're completely done with the demo

**Manual removal:**
```bash
# Delete just the container (keeps storage account)
az storage container delete --name documents --account-name <storage-account>

# Or delete entire storage account
az storage account delete --name <storage-account> --resource-group <your-rg> --yes
```

---

### Step 5: Local Files

| Path | Description |
|------|-------------|
| `/files/` | Your uploaded business documents |
| `/frontend/node_modules/` | Frontend npm dependencies (~200MB) |
| `/frontend/dist/` | Frontend production build |
| `/.venv/` | Python virtual environment |
| `/__pycache__/` | Python bytecode cache |
| `.env` | Environment file with secrets |

**Keep or Remove?**
- **Keep `/files/`** if you want to preserve your documents
- **Keep `.env`** if you plan to run again (contains API keys)
- **Remove `node_modules/` and `.venv/`** to save disk space (can be reinstalled)

**Manual removal:**
```bash
# Remove dependencies (can be reinstalled)
rm -rf frontend/node_modules .venv __pycache__ src/__pycache__

# Remove everything including documents
rm -rf files/ frontend/node_modules frontend/dist .venv .env
```

---

## Resources NOT Deleted

The teardown script intentionally preserves these shared/expensive resources:

| Resource | Reason |
|----------|--------|
| Azure OpenAI / AI Foundry | Shared resource, expensive to recreate, contains model deployments |
| Azure AI Search Service | Only the index is deleted, not the service itself |
| Azure Resource Group | May contain other resources |
| Source Code | Your project files remain intact |

**To completely remove everything:**
```bash
# Delete the entire resource group (CAUTION: removes ALL resources in the group)
az group delete --name <your-resource-group> --yes --no-wait
```

---

## Teardown Checklist

Use this checklist when cleaning up manually:

- [ ] Stop local services (`pkill -f uvicorn`, `pkill -f vite`)
- [ ] Delete Azure AI Search index
- [ ] Delete Azure Container App (if deployed)
- [ ] Delete Azure Container Apps environment (if deployed)
- [ ] Delete Blob Storage container/account (if created)
- [ ] Remove local node_modules and .venv
- [ ] Remove or secure .env file (contains secrets)
- [ ] Optionally remove /files/ directory

---

## Re-deploying After Teardown

If you tore down resources but kept the source code, you can redeploy:

```bash
# Reinstall dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Reinstall frontend
cd frontend && npm install && cd ..

# Re-ingest documents (if you kept /files/)
python src/ingest.py

# Start services
python -m uvicorn src.api:app --port 8000 &
cd frontend && npm run dev &
```

---

## Troubleshooting

### "Index not found" error during teardown
The index may have already been deleted. This is safe to ignore.

### "Container App not found" error
The app was never deployed or already deleted. Safe to ignore.

### Ports still in use after teardown
```bash
# Find what's using port 8000
lsof -i :8000

# Force kill
kill -9 <PID>
```

### .env file concerns
The .env file contains API keys. Either:
- Delete it: `rm .env`
- Or keep it secure and don't commit to git (already in .gitignore)
