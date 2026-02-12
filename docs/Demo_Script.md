# FoundryIQ Demo Script

A complete guide for delivering an effective demo of the FoundryIQ AI Document Assistant.

---

## 📋 Pre-Demo Checklist

Before starting your demo, verify:

- [ ] **Azure resources are running** - AI Services and AI Search are active
- [ ] **Documents are indexed** - Run a test query to confirm
- [ ] **Application is running** - API server and frontend are up
- [ ] **Browser tabs ready** - Have these open:
  - FoundryIQ chat interface (localhost:5173 or deployed URL)
  - Azure AI Foundry portal (optional, for agent demo)
  - This demo script

### Quick Verification

```bash
# Test the API is responding
curl http://localhost:8000/

# Test a search query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How many products are active?"}'
```

---

## 🎬 Demo Flow (15-20 minutes)

### Opening (2 min)

**What to say:**
> "Today I'll show you FoundryIQ, an AI-powered document assistant that can answer natural language questions across your entire document library. It uses Azure AI Search with vector embeddings and GPT-4.1 to provide intelligent, context-aware responses."

**Key points:**
- This is a RAG (Retrieval Augmented Generation) system
- Combines semantic search with LLM reasoning
- Works with CSV, Excel, Word, and PDF documents
- Can be deployed as a chat app or Azure AI Foundry agent

---

### Part 1: Simple Queries (3 min)

Start with straightforward, single-document questions to build confidence.

#### Query 1: Product Overview
```
What products are in the catalog?
```

**Talking points:**
- Notice how it returns structured data (table format)
- Sources are cited at the bottom
- The AI extracted this from CSV/Excel files automatically

#### Query 2: Customer Status
```
What's the breakdown of customer status?
```

**Talking points:**
- Quantitative analysis from the Customer Master
- Percentages are calculated automatically
- Business insights are provided (re-engagement opportunities)

#### Query 3: Support Tickets
```
Are there any P1 or P2 priority support cases open?
```

**Talking points:**
- Filtered search based on criteria
- Shows ticket age and urgency
- Actionable recommendations included

---

### Part 2: Cross-Document Intelligence (5 min)

This is where the magic happens - questions that require synthesizing multiple documents.

#### Query 4: Executive Summary
```
Give me an executive summary of current operational health - include compliance status, open incidents, security posture, and any customer-impacting issues.
```

**Talking points:**
- Pulls from 5+ documents simultaneously
- Prioritizes and organizes information
- Would take hours manually, done in seconds
- Notice multiple source citations

#### Query 5: Risk Assessment
```
What are our top 5 business risks right now? Consider security vulnerabilities, overdue compliance filings, open high-priority tickets, and audit findings.
```

**Talking points:**
- AI reasoning to prioritize and rank
- Cross-domain analysis (security + compliance + operations)
- Business context applied automatically

#### Query 6: Customer 360
```
I have a QBR with customer CUST001 next week. Summarize their account health including status, billing info, and any related support tickets.
```

**Talking points:**
- Correlates Customer Master with Support Cases
- Prepares you for customer meetings
- Could extend to include revenue, contracts, etc.

---

### Part 3: Specialized Queries (3 min)

Show domain-specific capabilities.

#### Query 7: Compliance Check
```
We're approaching end of quarter. Which compliance filings are due in the next 30 days?
```

#### Query 8: Security Audit Prep
```
Our security audit is coming up. Summarize our security controls, any open vulnerabilities, and access control configuration.
```

#### Query 9: DR Readiness
```
If we had a major outage today, are we prepared? Show me DR test results and backup status.
```

---

### Part 4: How It Works (3 min)

Briefly explain the architecture:

> "Let me show you what's happening behind the scenes..."

**Draw or explain:**
```
Documents → Chunking → Embeddings → Azure AI Search
                                          ↓
User Question → Embedding → Vector Search → Top K Results
                                          ↓
                           Context + Question → GPT-4.1 → Answer
```

**Key points:**
- Documents are chunked and embedded at ingestion time
- Queries find semantically similar content (not just keyword matching)
- GPT-4.1 synthesizes the answer with source attribution
- Everything runs on Azure (AI Search + OpenAI)

---

### Part 5: Extensibility (2 min)

**What to mention:**
- Add your own documents to the `/files` folder
- Re-run ingestion to update the index
- Deploy as Azure AI Foundry agent for Teams/M365 integration
- Add more document types (just extend the processor)
- Multi-agent orchestration for complex workflows

**Show if time permits:**
- Azure AI Foundry portal with the agent
- The Agent_Instructions.md for easy agent creation

---

### Closing (2 min)

**What to say:**
> "What we've built here is a foundation that can be extended to any document corpus. Whether it's HR policies, financial reports, technical documentation, or customer data - the pattern is the same. Ingest, embed, search, and answer."

**Call to action:**
- "Want to try it with your own documents?"
- "Let's discuss how this could apply to your use case"
- "The code is available - I can walk through the implementation"

---

## 💡 Demo Tips

### Do's
- ✅ Start with simple queries, then escalate complexity
- ✅ Point out source citations - this builds trust
- ✅ Compare to manual process ("this would take hours")
- ✅ Ask follow-up questions to show conversation flow
- ✅ Have backup queries ready if something doesn't work

### Don'ts
- ❌ Don't apologize for AI limitations - frame as areas for improvement
- ❌ Don't read from the screen - know your talking points
- ❌ Don't skip the "how it works" section - people want to understand
- ❌ Don't rush - let the AI responses fully render

### Handling Issues

**If a query gives unexpected results:**
> "That's interesting - the AI is working with the data it has. In production, we'd fine-tune the prompts and ensure comprehensive data coverage."

**If the response is slow:**
> "We're making calls to Azure OpenAI in real-time. In production, we can add caching for common queries."

**If someone asks about accuracy:**
> "The source citations let you verify every claim. The system is designed for transparency - you can always click through to the original document."

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| No results returned | Check if documents are indexed: `python3 -m src.ingest` |
| API not responding | Verify server is running: `uvicorn src.api:app --reload` |
| Authentication errors | Re-run `az login` and check `.env` credentials |
| Slow responses | Normal for first query (cold start); subsequent queries faster |

---

## 📚 Additional Resources

- [Agent_Instructions.md](../Agent_Instructions.md) - Create an Azure AI Foundry agent
- [Getting_Started_Prompts.md](../Getting_Started_Prompts.md) - Original prompts used to build this
- [Generic_Getting_Started.md](Generic_Getting_Started.md) - Full setup guide

---

## 🎯 Bonus: Quick Demo Queries

Copy-paste ready queries for a rapid-fire demo:

```
1. What products are active in the catalog?
2. Show me open P1 and P2 support tickets
3. What's our customer status breakdown?
4. Give me an executive summary of operational health
5. What are our top 5 business risks?
6. Which compliance filings are due this month?
7. Summarize our security posture for an audit
8. What's the status of our disaster recovery preparedness?
9. Give me a vendor ecosystem overview
10. Are there any employees with incomplete training who have system access?
```
