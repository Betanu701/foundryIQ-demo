"""Ingest all files from the files directory into Azure AI Search."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import FILES_DIRECTORY
from src.document_processor import process_all_files
from src.azure_search_client import create_search_index, upload_documents
from src.embeddings import generate_embeddings_batch


def main():
    """Main ingestion function."""
    print("=" * 60)
    print("FoundryIQ Document Ingestion")
    print("=" * 60)
    
    # Step 1: Process all files
    print("\n[Step 1] Processing files from:", FILES_DIRECTORY)
    documents = process_all_files(FILES_DIRECTORY)
    print(f"\nTotal documents extracted: {len(documents)}")
    
    if not documents:
        print("No documents found. Exiting.")
        return
    
    # Step 2: Create the search index
    print("\n[Step 2] Creating Azure AI Search index...")
    try:
        create_search_index()
    except Exception as e:
        print(f"Error creating index: {e}")
        print("Make sure your Azure Search credentials are configured in .env")
        return
    
    # Step 3: Generate embeddings for all documents
    print("\n[Step 3] Generating embeddings...")
    try:
        contents = [doc["content"] for doc in documents]
        embeddings = generate_embeddings_batch(contents)
        
        # Add embeddings to documents
        for doc, embedding in zip(documents, embeddings):
            doc["content_vector"] = embedding
        
        print(f"Generated {len(embeddings)} embeddings")
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        print("Make sure your Azure OpenAI credentials are configured in .env")
        print("Continuing without vector embeddings...")
        # Remove content_vector field if embeddings failed
        for doc in documents:
            if "content_vector" in doc:
                del doc["content_vector"]
    
    # Step 4: Upload documents to Azure Search
    print("\n[Step 4] Uploading documents to Azure AI Search...")
    try:
        upload_documents(documents)
        print("\nIngestion complete!")
    except Exception as e:
        print(f"Error uploading documents: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  - Files processed: {len(set(d['file_name'] for d in documents))}")
    print(f"  - Document chunks indexed: {len(documents)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
