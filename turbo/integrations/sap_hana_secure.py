"""SAP HANA Secure RAG Connector — Enterprise-grade SQL generation and data masking."""

import re
import logging
from typing import Any, Dict, List, Optional

from hdbcli import dbapi
from turboprivate.safety.gate import SafetyGate
from turboprivate.safety.verifiers.pii_detector import PIIDetector

logger = logging.getLogger(__name__)

# SQL Injection patterns to block
DANGEROUS_SQL_PATTERNS = [
    r"(?i)\b(DROP|ALTER|GRANT|REVOKE|TRUNCATE|DELETE\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET)\b",
    r"(?i)\b(UNION\s+ALL|UNION\s+SELECT)\b",
    r"(?i)(--|;|/\*|\*/)",
]

# PII patterns for masking
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
}


class SapHanaSecureConnector:
    """Secure connector for SAP HANA with SQL injection guard, RLS, and PII masking."""

    def __init__(
        self,
        address: str,
        port: int,
        user: str,
        password: str,
        database: str = "HANA_DB",
        encrypt: bool = True,
    ):
        self.conn = dbapi.connect(
            address=address,
            port=port,
            user=user,
            password=password,
            databaseName=database,
            encrypt=encrypt,
        )
        self.safety_gate = SafetyGate()
        self.pii_detector = PIIDetector()
        logger.info("SAP HANA Secure Connector initialized")

    def validate_prompt(self, prompt: str) -> bool:
        """Check prompt for SQL injection attempts."""
        for pattern in DANGEROUS_SQL_PATTERNS:
            if re.search(pattern, prompt):
                logger.warning(f"SQL injection attempt detected: {prompt}")
                return False
        return True

    def generate_sql(self, prompt: str, model_name: str = "llama-3.1-8b") -> str:
        """Generate SQL from natural language prompt using local LLM."""
        # In production, this would call the inference engine
        # For now, we use a placeholder that would be replaced with actual LLM call
        system_prompt = """You are a SAP HANA SQL expert. Generate a SELECT query based on the user's request.
Rules:
- Only generate SELECT statements.
- Use standard SQL syntax compatible with SAP HANA.
- Do not include any DDL or DML statements (DROP, ALTER, INSERT, UPDATE, DELETE).
- Return only the SQL query, no explanations."""

        # Placeholder for actual LLM integration
        # response = self.inference_engine.generate(system_prompt, prompt)
        # return response.strip()
        raise NotImplementedError("LLM integration required for SQL generation")

    def inject_rls(self, sql: str, user_role: str, tenant_id: Optional[str] = None) -> str:
        """Inject Row-Level Security constraints based on user role."""
        if tenant_id:
            # Add tenant isolation
            if "WHERE" in sql.upper():
                sql = sql.rstrip(";") + f" AND tenant_id = '{tenant_id}'"
            else:
                sql = sql.rstrip(";") + f" WHERE tenant_id = '{tenant_id}'"

        # Role-based column restrictions (example)
        if user_role == "viewer":
            # Remove sensitive columns from SELECT
            sensitive_cols = ["salary", "ssn", "credit_card", "password_hash"]
            for col in sensitive_cols:
                sql = re.sub(rf"(?i)\b{col}\b", "[REDACTED]", sql)

        return sql

    def mask_pii(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mask PII in query results."""
        masked_data = []
        for row in data:
            masked_row = {}
            for key, value in row.items():
                if isinstance(value, str):
                    for pii_type, pattern in PII_PATTERNS.items():
                        if re.search(pattern, value):
                            value = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", value)
                masked_row[key] = value
            masked_data.append(masked_row)
        return masked_data

    def execute_secure_query(
        self,
        prompt: str,
        user_role: str,
        tenant_id: Optional[str] = None,
        model_name: str = "llama-3.1-8b",
    ) -> List[Dict[str, Any]]:
        """Execute a secure query end-to-end."""
        # 1. Validate prompt
        if not self.validate_prompt(prompt):
            raise PermissionError("Prompt blocked by safety gate")

        # 2. Generate SQL
        sql = self.generate_sql(prompt, model_name)

        # 3. Inject RLS
        safe_sql = self.inject_rls(sql, user_role, tenant_id)

        # 4. Execute query
        cursor = self.conn.cursor()
        cursor.execute(safe_sql)
        columns = [desc[0] for desc in cursor.description]
        raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # 5. Mask PII
        clean_results = self.mask_pii(raw_results)

        # 6. Audit log
        logger.info(f"Secure query executed: {safe_sql[:50]}...")

        return clean_results

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("SAP HANA connection closed")
