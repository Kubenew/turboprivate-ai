"""Ingest SAP documents into HANA vector store for RAG retrieval."""

from langchain_hana import HanaDB
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from hana_ml import ConnectionContext
import config
import sys
from pathlib import Path


def ingest_documents(doc_paths: list[str], table_name: str = None):
    """Load, split, and embed documents into SAP HANA vector store."""
    table_name = table_name or config.VECTOR_TABLE

    # Connect to HANA
    cc = ConnectionContext(**config.HANA_CONFIG)

    # Embedding model
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)

    # Vector Store
    vector_store = HanaDB(
        embedding=embeddings,
        connection=cc,
        table_name=table_name,
    )

    all_chunks = []
    for doc_path in doc_paths:
        path = Path(doc_path)
        if not path.exists():
            print(f"  [WARN] File not found: {doc_path}")
            continue

        if path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(path))
        else:
            loader = TextLoader(str(path), encoding="utf-8")

        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(docs)
        all_chunks.extend(chunks)
        print(f"  Loaded {len(docs)} docs from {path.name} → {len(chunks)} chunks")

    if not all_chunks:
        print("No documents to ingest.")
        return

    # Add to HANA Vector Store
    vector_store.add_documents(all_chunks)
    print(f"\n✓ Added {len(all_chunks)} chunks to HANA vector table '{table_name}'.")

    # Optional: create HNSW index for faster search on large datasets
    try:
        cc.sql(f"""
            CREATE VECTOR INDEX VI_{table_name}
            ON {table_name}(VECTOR_COLUMN)
            USING HNSW
            PARAMETERS('metricType=COSINE', 'maxNeighbours=50')
        """)
        print("✓ Created HNSW vector index for fast similarity search.")
    except Exception as e:
        print(f"  [INFO] HNSW index creation skipped: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <doc1.pdf> [doc2.txt] ...")
        print("Example: python ingest.py docs/sap_s4hana_guide.pdf docs/order_to_cash.txt")
        sys.exit(1)

    print(f"Connecting to HANA at {config.HANA_CONFIG['address']}:{config.HANA_CONFIG['port']}...")
    ingest_documents(sys.argv[1:])
