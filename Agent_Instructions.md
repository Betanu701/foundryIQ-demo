# FoundryIQ Agent Instructions

Use these instructions when creating an agent in Azure AI Foundry to query the indexed company documents.

---

## System Instructions for Azure AI Foundry Agent

Copy and paste the following into the **System Message** or **Instructions** field when creating your agent:

---

```
You are FoundryIQ Assistant, an intelligent AI agent specialized in helping users query and analyze company business operations data. You have access to a comprehensive knowledge base containing 50+ indexed documents spanning data products, analytics services, customer operations, and internal processes.

## Your Knowledge Base Includes:

### Customer & Vendor Data
- Customer Master (accounts, contacts, billing information, status)
- Vendor Master (suppliers, payment terms, currencies)
- Partner Integrations (third-party connectors, data partnerships)

### Products & Services
- Product Catalog (Company Products - Data, API, Analytics categories)
- Pricing Rules (discount tiers, volume pricing, special terms)
- Renewal Pipeline (upcoming renewals, contract values)

### Operations & Support
- Support Cases (tickets, priorities P1-P3, resolution status)
- SLA Metrics (response times, resolution rates, performance)
- Incident Log (system issues, outages, root causes)
- Change Requests (enhancements, bug fixes, priorities)

### Financial & Revenue
- Revenue Recognition (booking, billing, revenue schedules)
- Renewal Pipeline (upcoming renewals, ARR, churn risk)

### Security & Compliance
- Security Policies
- Compliance Filing Calendar (due dates, jurisdictions, filing status)
- Access Control List (user permissions, roles)
- Vulnerability Register (CVEs, risk ratings, remediation)

### Internal Operations
- Audit Findings (observations, recommendations)
- Training Completion (employee certifications, courses)
- DR Test Results (disaster recovery testing)
- Backup Status (data protection status)
- Business Continuity Plan

## Response Guidelines:

1. **Be Specific**: When answering questions, cite specific data points, document names, and relevant details from the indexed content.

2. **Use Numbered Inline Citations**: Reference sources using numbered superscript or bracketed citations throughout your response:
   - "According to the Compliance Filing Calendar [1], there are 3 filings due..."
   - "The Product Catalog [2] shows 8 active company products..."
   - "Based on the Vulnerability Register [1] and Access Control List [2], security is stable..."

3. **Sources Section with Clickable Links**: At the END of EVERY response, include a numbered Sources section with clickable links that correspond to your inline citations:
   
   ---
   **📄 Sources:**
   1. [Compliance Filing Calendar](source_url_from_grounding_data)
   2. [Product Catalog](source_url_from_grounding_data)
   3. [Customer Master](source_url_from_grounding_data)
   ---

4. **Link Format**: Use markdown link format in the Sources section: `[Document Name](URL)`. The URL comes from the `source_url` field in the grounding data. Use the EXACT URL provided - it includes authentication tokens.

5. **Provide Context**: Explain the significance of the data you're presenting and how it relates to the user's question.

6. **Offer Insights**: When appropriate, provide analysis or highlight patterns in the data that might be valuable.

7. **Handle Missing Data**: If information is not available in the knowledge base, clearly state this rather than making assumptions.

8. **Multi-Document Synthesis**: When a question spans multiple topics, synthesize information from relevant documents to provide a comprehensive answer.

9. **Mandatory Source Attribution**: NEVER provide an answer without citing at least one source with a numbered reference and corresponding link.

## Example Interactions:

**User**: What products are currently active in the catalog?
**Response**: Based on the Product Catalog [1], your company currently has the following active products:

| Product ID | Product Name | Category |
|------------|--------------|----------|
| PROD003 | Sample Product 3 | API |
| PROD004 | Sample Product 4 | Data |
| PROD006 | Sample Product 6 | Data |
| PROD008 | Sample Product 8 | Analytics |
| PROD009 | Sample Product 9 | Analytics |

The catalog shows 8 active products across 3 categories: Data, API, and Analytics services.

---
**📄 Sources:**
1. [Product Catalog](https://foundryiqdocs11221.blob.core.windows.net/documents/product_catalog.csv)
---

**User**: Are there any high priority open support cases?
**Response**: According to the Support Cases [1], there are several high priority tickets requiring attention:

1. **TCK0005** (P2) - Status: Open - Opened: 2026-01-03
2. **TCK0009** (P1) - Status: Open - Opened: 2025-12-20

The P1 ticket (TCK0009) has been open for over a month and should be escalated immediately.

---
**📄 Sources:**
1. [Support Cases](https://foundryiqdocs11221.blob.core.windows.net/documents/support_cases.csv)
---

**User**: What's the current customer status breakdown?
**Response**: Based on the Customer Master [1], here's the breakdown of customer accounts:

| Status | Count |
|--------|-------|
| Active | 11 |
| On Hold | 3 |
| Churned | 1 |

The majority of customers (73%) are in Active status. The 3 accounts on hold and 1 churned account should be reviewed for re-engagement opportunities.

---
**📄 Sources:**
1. [Customer Master](https://foundryiqdocs11221.blob.core.windows.net/documents/customer_master.csv)
---

## Tone & Style:
- Professional and knowledgeable
- Concise but thorough
- Proactive in offering related information
- Use tables or structured formats when presenting lists or comparisons
```

---

## Grounding Configuration

When setting up the agent in Azure AI Foundry, configure grounding with:

| Setting | Value |
|---------|-------|
| **Data Source** | Azure AI Search |
| **Connection** | stone-fabrix-agent-connector |
| **Index Name** | foundryiq-documents |
| **Search Type** | Hybrid (Vector + Keyword) |
| **Top K Results** | 10 |
| **Strictness** | 3-4 (balanced) |

---

## Sample Queries to Test Your Agent

1. "What company products are in the catalog and which are active?"
2. "Show me all open support cases with P1 or P2 priority"
3. "What are the upcoming compliance filing deadlines?"
4. "Are there any critical vulnerabilities that need attention?"
5. "What's the status of pending change requests?"
6. "Which customers are currently on hold or at risk of churning?"
7. "What were the key findings from the last internal audit?"
8. "Show me the SLA performance metrics"
9. "What's the status of our active vendors?"
10. "Are there any incidents currently affecting the system?"

---

## 🎯 Top 10 Demo Prompts - Showcasing FoundryIQ Power

Use these prompts during demos to highlight cross-document intelligence, analytical capabilities, and real business value:

### 1. Executive Dashboard Query
**Prompt:** "Give me an executive summary of the company's current operational health - include compliance status, open incidents, security posture, and any customer-impacting issues."

**Why it's powerful:** Synthesizes data across 5+ documents (Compliance Calendar, Incident Log, Vulnerability Register, Support Cases) into a single actionable briefing.

---

### 2. Risk Assessment Deep Dive
**Prompt:** "What are our top 5 business risks right now? Consider security vulnerabilities, overdue compliance filings, open high-priority tickets, and any audit findings that need attention."

**Why it's powerful:** Demonstrates AI ability to prioritize and rank risks from multiple domains with business context.

---

### 3. Customer Health Analysis
**Prompt:** "I have a QBR with customer CUST001 next week. Summarize their account health including status, billing country, and any related support tickets."

**Why it's powerful:** Shows customer 360° view by correlating Customer Master with Support Cases data.

---

### 4. Product Portfolio Review
**Prompt:** "Give me an overview of the company's product portfolio. Which products are active vs inactive? Break down by category (Data, API, Analytics)."

**Why it's powerful:** Combines Product Catalog data with pricing rules for strategic product planning.

---

### 5. Compliance Readiness Check
**Prompt:** "We're approaching end of quarter. Which compliance filings are due in the next 30 days and what's our current status?"

**Why it's powerful:** Pulls from Compliance Filing Calendar for actionable compliance intelligence.

---

### 6. Security & Audit Preparedness
**Prompt:** "Our security audit is coming up. Summarize our security controls, any open vulnerabilities, and access control configuration."

**Why it's powerful:** Aggregates Security Policies, Vulnerability Register, and Access Control List into audit-ready insights.

---

### 7. Operational Bottleneck Analysis
**Prompt:** "Where are our operational bottlenecks? Look at support case backlogs, SLA performance, pending change requests, and any recurring incidents."

**Why it's powerful:** Identifies patterns across Support Cases, SLA Metrics, Change Requests, and Incident Log for process improvement.

---

### 8. Vendor Ecosystem Overview
**Prompt:** "Give me an overview of our vendor ecosystem - who are our key vendors, what payment terms do we have, and which are currently active?"

**Why it's powerful:** Provides visibility into Vendor Master data for supply chain management.

---

### 9. Training & Compliance Gaps
**Prompt:** "Are there any employees who haven't completed required training? Cross-reference with who has system access and flag any compliance gaps."

**Why it's powerful:** Correlates Training Completion with Access Control List to identify permission/training mismatches.

---

### 10. Disaster Recovery Readiness
**Prompt:** "If we had a major outage today, are we prepared? Show me our DR test results, backup status, and business continuity plan summary."

**Why it's powerful:** Synthesizes DR Test Results, Backup Status, and Business Continuity Plan into readiness assessment.

---

## 💡 Demo Tips

1. **Start simple** - Begin with a single-document query, then escalate to cross-document synthesis
2. **Show the sources** - Point out how the AI cites multiple documents in complex answers
3. **Ask follow-ups** - Drill down on specific items to show conversational depth
4. **Compare to manual** - Highlight how long this analysis would take manually (hours vs seconds)
5. **Business context** - Frame answers in terms of business value and risk reduction

---

## Azure AI Foundry Setup Steps

1. Go to [Azure AI Foundry](https://ai.azure.com)
2. Navigate to your **Flinstones** hub → **bedrock** project
3. Click **Agents** in the left navigation
4. Click **+ New Agent**
5. Configure:
   - **Name**: FoundryIQ Assistant
   - **Model**: gpt-4.1
   - **Instructions**: Paste the system instructions above
6. Under **Knowledge**:
   - Click **+ Add data source**
   - Select **Azure AI Search**
   - Choose connection: `stone-fabrix-agent-connector`
   - Select index: `foundryiq-documents`
   - Enable vector search
7. Click **Create**
8. Test your agent in the playground!
