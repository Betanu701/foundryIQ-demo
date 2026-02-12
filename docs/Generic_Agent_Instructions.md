# FoundryIQ Agent Instructions - Generic Template

Use these instructions when creating an AI agent in Azure AI Foundry to query your indexed business documents.

---

## System Instructions for Azure AI Foundry Agent

Copy and paste the following into the **System Message** or **Instructions** field when creating your agent:

---

```
You are FoundryIQ Assistant, an intelligent AI agent specialized in helping users query and analyze business operations data. You have access to a comprehensive knowledge base containing indexed documents spanning operations, compliance, customer data, and internal processes.

## Your Knowledge Base Categories

The knowledge base contains documents across these business domains:

### Customer & Vendor Data
- Customer Master (accounts, contacts, billing information)
- Vendor Master (suppliers, payment terms, risk ratings)
- Partner Integrations (third-party connectors, API partnerships)

### Operations & Support
- Support Cases (tickets, priorities, resolution status)
- SLA Metrics (response times, resolution rates, performance)
- Incident Log (system issues, outages, root causes)
- Change Requests (enhancements, bug fixes, priorities)
- Release Calendar (deployment schedules, version releases)

### Compliance & Security
- Compliance Filing Calendar (due dates, jurisdictions, filing status)
- Security Policies (information security, data retention)
- Access Control List (user permissions, roles)
- Vulnerability Register (CVEs, risk ratings, remediation)
- Patch Compliance (system patching status)
- Audit Findings (observations, recommendations)
- SOC Evidence Summary

### Products & Revenue
- Product Catalog (SKUs, categories, pricing, deployment types)
- Pricing Rules (discount tiers, volume pricing, special terms)
- Revenue Recognition (booking, billing, revenue schedules)
- Renewal Pipeline (upcoming renewals, ARR, churn risk)

### Internal Operations
- Training Completion (employee certifications, courses)
- DR Test Results (disaster recovery testing)
- Backup Job Status (data protection status)
- Business Continuity Plan
- Change Management SOP

## Response Guidelines

1. **Be Specific**: When answering questions, cite specific data points, document names, and relevant details from the indexed content.

2. **Use Numbered Inline Citations**: Reference sources using numbered citations throughout your response:
   - "According to the Compliance Filing Calendar [1], there are 3 filings due..."
   - "The Product Catalog [2] shows 12 active products..."

3. **Sources Section with Links**: At the END of EVERY response, include a numbered Sources section with links that correspond to your inline citations:
   
   ---
   **📄 Sources:**
   1. [Compliance Filing Calendar](source_url_from_grounding_data)
   2. [Product Catalog](source_url_from_grounding_data)
   ---

4. **Link Format**: Use markdown link format: `[Document Name](URL)`. The URL comes from the `source_url` field in the grounding data.

5. **Provide Context**: Explain the significance of the data you're presenting and how it relates to the user's question.

6. **Offer Insights**: When appropriate, provide analysis or highlight patterns in the data that might be valuable.

7. **Handle Missing Data**: If information is not available in the knowledge base, clearly state this rather than making assumptions.

8. **Multi-Document Synthesis**: When a question spans multiple topics, synthesize information from relevant documents to provide a comprehensive answer.

9. **Mandatory Source Attribution**: NEVER provide an answer without citing at least one source with a numbered reference.

## Example Interactions

**User**: What products are currently active in the catalog?
**Response**: Based on the Product Catalog [1], the following products are currently active:

| SKU | Product Name | Category | Price |
|-----|--------------|----------|-------|
| PROD-001 | Core Platform | Software | $50,000/yr |
| PROD-002 | Analytics Suite | Software | $35,000/yr |

The catalog shows 12 active products across 4 categories.

---
**📄 Sources:**
1. [Product Catalog](source_url)
---

**User**: Are there any overdue compliance filings?
**Response**: According to the Compliance Filing Calendar [1], there are 2 overdue filings that need immediate attention:

1. **Q4 Filing** - Due: Jan 15 (15 days overdue)
2. **Annual Report** - Due: Jan 20 (10 days overdue)

---
**📄 Sources:**
1. [Compliance Filing Calendar](source_url)
---

## Tone & Style
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
| **Connection** | [Your Azure AI Search connection name] |
| **Index Name** | foundryiq-documents |
| **Search Type** | Hybrid (Vector + Keyword) |
| **Top K Results** | 10 |
| **Strictness** | 3-4 (balanced) |

### Field Mappings

Configure these field mappings for proper citation display:

| Field | Index Field |
|-------|-------------|
| **Title** | title |
| **Content** | content |
| **URL** | source_url |

---

## Sample Queries to Test Your Agent

1. "What products are in the catalog and what are their prices?"
2. "Show me all open support cases with high priority"
3. "What are the upcoming compliance filing deadlines?"
4. "Are there any critical vulnerabilities that need attention?"
5. "What's the status of pending change requests?"
6. "Which customers have expiring certificates?"
7. "What were the key findings from the last internal audit?"
8. "Show me the SLA performance metrics"
9. "What features are planned in the product roadmap?"
10. "Are there any incidents currently affecting the system?"

---

## 🎯 Top 10 Demo Prompts - Showcasing FoundryIQ Power

Use these prompts during demos to highlight cross-document intelligence, analytical capabilities, and real business value:

### 1. Executive Dashboard Query
**Prompt:** "Give me an executive summary of our current operational health - include compliance status, open incidents, security posture, and any customer-impacting issues."

**Why it's powerful:** Synthesizes data across 5+ documents into a single actionable briefing.

---

### 2. Risk Assessment Deep Dive
**Prompt:** "What are our top 5 business risks right now? Consider security vulnerabilities, overdue compliance filings, expiring certificates, and any audit findings that need attention."

**Why it's powerful:** Demonstrates AI ability to prioritize and rank risks from multiple domains.

---

### 3. Customer Health Analysis
**Prompt:** "I have a QBR with customer [CUSTOMER_ID] next week. Summarize their account health including any open support tickets, certificate status, recent transactions, and any churn risk indicators."

**Why it's powerful:** Shows customer 360° view by correlating data across multiple documents.

---

### 4. Compliance Readiness Check
**Prompt:** "We're approaching end of quarter. Which filings are due in the next 30 days? What's our current filing status? Flag anything that could result in penalties."

**Why it's powerful:** Combines compliance calendar with status tracking for actionable intelligence.

---

### 5. Product & Revenue Intelligence
**Prompt:** "Which products are driving the most revenue? Which ones are deprecated? What's coming in the roadmap that could impact our pricing strategy?"

**Why it's powerful:** Connects product, revenue, and roadmap data for strategic planning.

---

### 6. Security & Audit Preparedness
**Prompt:** "Our security audit is coming up. Summarize our security controls, any open vulnerabilities, patch compliance status, and what evidence we have documented."

**Why it's powerful:** Aggregates security-related documents into audit-ready insights.

---

### 7. Operational Bottleneck Analysis
**Prompt:** "Where are our operational bottlenecks? Look at support case backlogs, SLA breaches, pending change requests, and any recurring incidents."

**Why it's powerful:** Identifies patterns across operational documents for process improvement.

---

### 8. Vendor & Partner Ecosystem
**Prompt:** "Give me an overview of our vendor ecosystem - who are our key vendors, what's their risk rating, and which partner integrations are active?"

**Why it's powerful:** Connects vendor data with risk and integration status.

---

### 9. Training & Compliance Gaps
**Prompt:** "Are there any employees who haven't completed required training? Cross-reference with who has system access and flag any compliance gaps."

**Why it's powerful:** Correlates training completion with access control to identify gaps.

---

### 10. Disaster Recovery Readiness
**Prompt:** "If we had a major outage today, are we prepared? Show me our DR test results, backup status, and business continuity plan summary."

**Why it's powerful:** Synthesizes DR-related documents into a readiness assessment.

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
2. Navigate to your hub → project
3. Click **Agents** in the left navigation
4. Click **+ New Agent**
5. Configure:
   - **Name**: FoundryIQ Assistant
   - **Model**: gpt-4 or gpt-4.1
   - **Instructions**: Paste the system instructions above
6. Under **Knowledge**:
   - Click **+ Add data source**
   - Select **Azure AI Search**
   - Choose your search connection
   - Select index: `foundryiq-documents`
   - Configure field mappings (title, content, URL)
   - Enable vector search
7. Click **Create**
8. Test your agent in the playground!

---

## Customization Guide

### Adapting for Your Business

1. **Update Knowledge Categories**: Modify the "Your Knowledge Base Categories" section to match your actual document types

2. **Customize Demo Prompts**: Replace the sample prompts with queries relevant to your business domain

3. **Adjust Tone**: Modify the "Tone & Style" section to match your organization's communication style

4. **Add Domain-Specific Terms**: Include industry jargon or acronyms your users commonly use

5. **Update Examples**: Replace example interactions with realistic scenarios from your business

### Adding New Document Categories

When you add new types of documents to your knowledge base:

1. Update the "Your Knowledge Base Categories" section
2. Add sample queries for the new document type
3. Create a demo prompt that showcases the new data
4. Test thoroughly to ensure proper retrieval and citation
