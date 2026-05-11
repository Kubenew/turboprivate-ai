"""Example: Ingest a document and search via the RAG API."""
import httpx

BASE_URL = "http://localhost:8000"

# Ingest a document
with open("example.pdf", "rb") as f:
    resp = httpx.post(
        f"{BASE_URL}/api/v1/memory/ingest",
        files={"file": ("example.pdf", f, "application/pdf")},
        data={"collection": "my_docs"},
    )
print("Ingest:", resp.json())

# Search
resp = httpx.get(
    f"{BASE_URL}/api/v1/memory/search",
    params={"query": "What is this document about?", "collection": "my_docs", "top_k": 3},
)
print("Search:", resp.json())
