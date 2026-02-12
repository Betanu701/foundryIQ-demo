"""Embeddings generation using Azure OpenAI."""

from typing import List
from openai import AzureOpenAI

from .config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
)


def get_openai_client() -> AzureOpenAI:
    """Get Azure OpenAI client."""
    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
    )


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text."""
    client = get_openai_client()
    
    # Truncate text if too long (max ~8000 tokens for ada-002)
    max_chars = 30000
    if len(text) > max_chars:
        text = text[:max_chars]
    
    response = client.embeddings.create(
        input=text,
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    )
    
    return response.data[0].embedding


def generate_embeddings_batch(texts: List[str], batch_size: int = 16) -> List[List[float]]:
    """Generate embeddings for a batch of texts."""
    client = get_openai_client()
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        # Truncate each text
        batch = [t[:30000] if len(t) > 30000 else t for t in batch]
        
        response = client.embeddings.create(
            input=batch,
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        )
        
        embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(embeddings)
        print(f"Generated embeddings for batch {i // batch_size + 1}")
    
    return all_embeddings
