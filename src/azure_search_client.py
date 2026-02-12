"""Azure AI Search client for indexing and querying documents."""

from typing import List, Dict, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchableField,
    SearchIndex,
)

from .config import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_API_KEY,
    AZURE_SEARCH_INDEX_NAME,
)


def get_index_client() -> SearchIndexClient:
    """Get Azure Search Index Client."""
    credential = AzureKeyCredential(AZURE_SEARCH_API_KEY)
    return SearchIndexClient(endpoint=AZURE_SEARCH_ENDPOINT, credential=credential)


def get_search_client() -> SearchClient:
    """Get Azure Search Client."""
    credential = AzureKeyCredential(AZURE_SEARCH_API_KEY)
    return SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=credential
    )


def create_search_index(vector_dimensions: int = 1536) -> None:
    """Create the search index with vector search capabilities."""
    index_client = get_index_client()
    
    # Define vector search configuration
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config",
            ),
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config",
            ),
        ],
    )
    
    # Define index fields
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="file_name", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="file_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="metadata", type=SearchFieldDataType.String),
        SimpleField(name="source_url", type=SearchFieldDataType.String),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=vector_dimensions,
            vector_search_profile_name="vector-profile",
        ),
    ]
    
    # Create the index
    index = SearchIndex(
        name=AZURE_SEARCH_INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
    )
    
    try:
        index_client.delete_index(AZURE_SEARCH_INDEX_NAME)
        print(f"Deleted existing index: {AZURE_SEARCH_INDEX_NAME}")
    except Exception:
        pass
    
    index_client.create_index(index)
    print(f"Created index: {AZURE_SEARCH_INDEX_NAME}")


def upload_documents(documents: List[Dict[str, Any]]) -> None:
    """Upload documents to the search index."""
    search_client = get_search_client()
    
    # Upload in batches of 100
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        result = search_client.upload_documents(documents=batch)
        succeeded = sum(1 for r in result if r.succeeded)
        print(f"Uploaded batch {i // batch_size + 1}: {succeeded}/{len(batch)} documents")


def search_documents(
    query: str,
    vector: Optional[List[float]] = None,
    top: int = 10,
    filter_expression: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search documents using hybrid search (text + vector)."""
    from azure.search.documents.models import VectorizedQuery
    
    search_client = get_search_client()
    
    vector_queries = None
    if vector:
        vector_queries = [
            VectorizedQuery(
                vector=vector,
                k_nearest_neighbors=top,
                fields="content_vector",
            )
        ]
    
    results = search_client.search(
        search_text=query,
        vector_queries=vector_queries,
        top=top,
        filter=filter_expression,
        select=["id", "file_name", "file_type", "content", "metadata"],
    )
    
    return [
        {
            "id": doc["id"],
            "file_name": doc["file_name"],
            "file_type": doc["file_type"],
            "content": doc["content"],
            "metadata": doc["metadata"],
            "score": doc["@search.score"],
        }
        for doc in results
    ]
