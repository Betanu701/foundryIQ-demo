"""Document processor for reading various file formats."""

import os
import csv
import json
from typing import List, Dict, Any
from pathlib import Path
from urllib.parse import quote

import pandas as pd

# Blob storage URL base
BLOB_STORAGE_URL = "https://foundryiqdocs11221.blob.core.windows.net/documents"

# SAS token for read access (valid until 2026-02-06, regenerate with:
# az storage container generate-sas --account-name foundryiqdocs11221 --name documents --permissions r --expiry YYYY-MM-DD --auth-mode login --as-user -o tsv
SAS_TOKEN = "se=2026-02-06&sp=r&sv=2022-11-02&sr=c&skoid=ad407371-bfba-4329-baab-1346b3ceece9&sktid=4b8b0561-888f-43b5-927d-3f1a7b147038&skt=2026-01-30T22%3A51%3A22Z&ske=2026-02-06T00%3A00%3A00Z&sks=b&skv=2022-11-02&sig=G%2BMtF6%2Bi7Js/oqquPhmb8bPndxvaxuz6WMJQyugJRv4%3D"


def get_blob_url(filename: str) -> str:
    """Get the blob URL for a file with SAS token."""
    return f"{BLOB_STORAGE_URL}/{quote(filename)}?{SAS_TOKEN}"


def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """Read a CSV file and return list of row dictionaries."""
    documents = []
    filename = os.path.basename(file_path)
    blob_url = get_blob_url(filename)
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader):
            content = " | ".join([f"{k}: {v}" for k, v in row.items() if v])
            documents.append({
                "id": f"{Path(file_path).stem}_row_{row_num}",
                "file_name": filename,
                "file_type": "csv",
                "content": content,
                "metadata": json.dumps(row),
                "source_url": blob_url,
                "title": filename.replace("_", " ").replace(".csv", "")
            })
    return documents


def read_excel_file(file_path: str) -> List[Dict[str, Any]]:
    """Read an Excel file and return list of row dictionaries."""
    documents = []
    filename = os.path.basename(file_path)
    blob_url = get_blob_url(filename)
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        for row_num, row in df.iterrows():
            row_dict = row.to_dict()
            content = " | ".join([f"{k}: {v}" for k, v in row_dict.items() if pd.notna(v)])
            documents.append({
                "id": f"{Path(file_path).stem}_row_{row_num}",
                "file_name": filename,
                "file_type": "xlsx",
                "content": content,
                "metadata": json.dumps({k: str(v) if pd.notna(v) else "" for k, v in row_dict.items()}),
                "source_url": blob_url,
                "title": filename.replace("_", " ").replace(".xlsx", "")
            })
    except Exception as e:
        print(f"Error reading Excel file {file_path}: {e}")
    return documents


def read_docx_file(file_path: str) -> List[Dict[str, Any]]:
    """Read a Word document and return as document."""
    filename = os.path.basename(file_path)
    blob_url = get_blob_url(filename)
    
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        content = "\n".join(paragraphs)
        
        # Split into chunks if content is too long (max ~8000 chars per chunk)
        chunks = []
        chunk_size = 8000
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            chunks.append({
                "id": f"{Path(file_path).stem}_chunk_{i // chunk_size}",
                "file_name": filename,
                "file_type": "docx",
                "content": chunk,
                "metadata": json.dumps({"chunk_index": i // chunk_size}),
                "source_url": blob_url,
                "title": filename.replace("_", " ").replace(".docx", "")
            })
        return chunks if chunks else [{
            "id": f"{Path(file_path).stem}_chunk_0",
            "file_name": filename,
            "file_type": "docx",
            "content": "Empty document",
            "metadata": json.dumps({}),
            "source_url": blob_url,
            "title": filename.replace("_", " ").replace(".docx", "")
        }]
    except Exception as e:
        print(f"Error reading Word file {file_path}: {e}")
        return []


def read_pdf_file(file_path: str) -> List[Dict[str, Any]]:
    """Read a PDF file and return as document."""
    filename = os.path.basename(file_path)
    blob_url = get_blob_url(filename)
    
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        content = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                content += text + "\n"
        
        # Split into chunks if content is too long
        chunks = []
        chunk_size = 8000
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            chunks.append({
                "id": f"{Path(file_path).stem}_chunk_{i // chunk_size}",
                "file_name": filename,
                "file_type": "pdf",
                "content": chunk,
                "metadata": json.dumps({"chunk_index": i // chunk_size}),
                "source_url": blob_url,
                "title": filename.replace("_", " ").replace(".pdf", "")
            })
        return chunks if chunks else [{
            "id": f"{Path(file_path).stem}_chunk_0",
            "file_name": filename,
            "file_type": "pdf",
            "content": "Empty or unreadable PDF",
            "metadata": json.dumps({}),
            "source_url": blob_url,
            "title": filename.replace("_", " ").replace(".pdf", "")
        }]
    except Exception as e:
        print(f"Error reading PDF file {file_path}: {e}")
        return []


def process_all_files(directory: str) -> List[Dict[str, Any]]:
    """Process all supported files in a directory."""
    all_documents = []
    
    for filename in os.listdir(directory):
        # Skip metadata files (Zone.Identifier, sec.endpointdlp)
        if ':' in filename or filename.startswith('.'):
            continue
            
        file_path = os.path.join(directory, filename)
        
        if not os.path.isfile(file_path):
            continue
        
        ext = filename.lower().split('.')[-1]
        
        print(f"Processing: {filename}")
        
        if ext == 'csv':
            docs = read_csv_file(file_path)
        elif ext == 'xlsx':
            docs = read_excel_file(file_path)
        elif ext == 'docx':
            docs = read_docx_file(file_path)
        elif ext == 'pdf':
            docs = read_pdf_file(file_path)
        else:
            print(f"  Skipping unsupported format: {ext}")
            continue
        
        all_documents.extend(docs)
        print(f"  Extracted {len(docs)} document chunks")
    
    return all_documents
