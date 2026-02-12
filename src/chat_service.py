"""Chat service using GPT-4.1 for natural language querying."""

from typing import List, Dict, Any
from openai import AzureOpenAI

from .config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
)
from .embeddings import generate_embedding
from .azure_search_client import search_documents


def get_openai_client() -> AzureOpenAI:
    """Get Azure OpenAI client."""
    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
    )


SYSTEM_PROMPT = """You are FoundryIQ Assistant, an AI-powered assistant that helps users query and understand their business data.

You have access to the following types of documents:
- Customer Master data
- Product Catalog
- Tax Jurisdictions and Transactions
- Compliance Filing Calendar
- Exemption Certificates
- Support Cases
- Revenue Recognition
- Internal Audit Findings
- Product Roadmap
- Vendor Master
- Access Control Lists
- Change Requests
- Release Calendar
- Incident Logs
- SLA Metrics
- API Usage Logs
- Data Quality Issues
- Pricing Rules
- Discount Approvals
- Renewal Pipeline
- Churn Reasons
- Training Completion
- Vulnerability Register
- Patch Compliance
- DR Test Results
- Backup Job Status
- Customer Feedback
- Partner Integrations
- Policy Documents (Security, Data Retention, Change Management, etc.)
- Various Reports (Tax Compliance, SOC Evidence, QBR, Revenue Forecast, etc.)

When answering questions:
1. Base your answers on the provided context from the search results
2. Be specific and cite the source documents when possible
3. If the information is not available in the context, say so clearly
4. Provide actionable insights when appropriate

Context from search results:
{context}
"""


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for the prompt context."""
    if not results:
        return "No relevant documents found."
    
    formatted = []
    for i, doc in enumerate(results, 1):
        formatted.append(f"[Document {i}] ({doc['file_name']}):\n{doc['content']}")
    
    return "\n\n".join(formatted)


def chat_with_documents(
    user_question: str,
    chat_history: List[Dict[str, str]] = None,
    use_vector_search: bool = True,
) -> Dict[str, Any]:
    """
    Answer a user question using RAG (Retrieval Augmented Generation).
    
    Args:
        user_question: The user's question
        chat_history: Optional list of previous messages
        use_vector_search: Whether to use vector search in addition to keyword search
    
    Returns:
        Dict containing the answer and source documents
    """
    # Generate embedding for the question
    query_vector = None
    if use_vector_search:
        try:
            query_vector = generate_embedding(user_question)
        except Exception as e:
            print(f"Warning: Could not generate embedding: {e}")
    
    # Search for relevant documents
    search_results = search_documents(
        query=user_question,
        vector=query_vector,
        top=10,
    )
    
    # Format context
    context = format_search_results(search_results)
    
    # Build messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context)}
    ]
    
    # Add chat history if provided
    if chat_history:
        messages.extend(chat_history)
    
    # Add current question
    messages.append({"role": "user", "content": user_question})
    
    # Call GPT-4.1
    client = get_openai_client()
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        temperature=0.7,
        max_tokens=1500,
    )
    
    answer = response.choices[0].message.content
    
    return {
        "answer": answer,
        "sources": [
            {
                "file_name": doc["file_name"],
                "file_type": doc["file_type"],
                "score": doc["score"],
                "preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
            }
            for doc in search_results[:5]
        ],
    }
