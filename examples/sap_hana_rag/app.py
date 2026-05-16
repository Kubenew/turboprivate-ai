"""FastAPI RAG endpoint: SAP HANA vector search + TurboPrivate AI generation."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from langchain_hana import HanaDB
from langchain_community.embeddings import HuggingFaceEmbeddings
from hana_ml import ConnectionContext
import config

app = FastAPI(title="SAP HANA + TurboPrivate AI RAG")

# ── Initialize connections (lazy-loaded on first request) ──
_cc = None
_vector_store = None
_llm_client = None


def get_cc():
    global _cc
    if _cc is None:
        _cc = ConnectionContext(**config.HANA_CONFIG)
    return _cc


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        _vector_store = HanaDB(
            embedding=embeddings,
            connection=get_cc(),
            table_name=config.VECTOR_TABLE,
        )
    return _vector_store


def get_llm():
    global _llm_client
    if _llm_client is None:
        _llm_client = OpenAI(
            base_url=config.TURBOPRIVATE_BASE_URL,
            api_key=config.TURBOPRIVATE_API_KEY,
        )
    return _llm_client


class RAGRequest(BaseModel):
    question: str
    k: int = 5
    temperature: float = 0.3
    max_tokens: int = 1024


class RAGResponse(BaseModel):
    answer: str
    sources: list[str]
    model: str


@app.post("/rag/query", response_model=RAGResponse)
def rag_query(req: RAGRequest):
    """Retrieve from HANA, generate with TurboPrivate AI."""
    vector_store = get_vector_store()
    llm = get_llm()

    # Retrieve relevant chunks
    docs = vector_store.similarity_search(req.question, k=req.k)
    if not docs:
        raise HTTPException(status_code=404, detail="No relevant documents found in HANA.")

    context = "\n\n".join([doc.page_content for doc in docs])
    sources = [doc.metadata.get("source", "unknown") for doc in docs]

    prompt = f"""You are a helpful SAP expert. Answer the question using only the provided context.
If you don't know, say so.

Context:
{context}

Question: {req.question}
Answer:"""

    response = llm.chat.completions.create(
        model=config.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )

    return RAGResponse(
        answer=response.choices[0].message.content,
        sources=sources,
        model=config.MODEL_NAME,
    )


@app.get("/health")
def health():
    return {"status": "ok", "hana": config.HANA_CONFIG["address"], "model": config.MODEL_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
