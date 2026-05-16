from dotenv import load_dotenv
import os

load_dotenv()

# SAP HANA Connection
HANA_CONFIG = {
    "address": os.getenv("HANA_HOST", "localhost"),
    "port": int(os.getenv("HANA_PORT", 443)),
    "user": os.getenv("HANA_USER", "SYSTEM"),
    "password": os.getenv("HANA_PASSWORD", ""),
    "database_name": os.getenv("HANA_DATABASE", "HANA_DB"),
    "encrypt": "true",
    "sslValidateCertificate": os.getenv("HANA_SSL_VALIDATE", "false"),
}

# TurboPrivate AI (OpenAI compatible)
TURBOPRIVATE_BASE_URL = os.getenv("TURBOPRIVATE_BASE_URL", "http://localhost:8000/v1")
TURBOPRIVATE_API_KEY = os.getenv("TURBOPRIVATE_API_KEY", "anything")
MODEL_NAME = os.getenv("TURBOPRIVATE_MODEL", "llama-3.1-8b")

# Embedding model (must match at query time)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Vector store table name
VECTOR_TABLE = os.getenv("VECTOR_TABLE", "SAP_DOCS_VECTOR")
