import pytest
from turbo.integrations.sap_hana_secure import SapHanaSecureConnector

class TestSapHanaSecurity:
    """Test SQL injection guard and safety mechanisms."""

    def test_validate_prompt_blocks_drop_table(self):
        """Mythos Safe should block DROP TABLE attempts."""
        connector = SapHanaSecureConnector.__new__(SapHanaSecureConnector)
        assert not connector.validate_prompt("SELECT * FROM users; DROP TABLE invoices;")

    def test_validate_prompt_blocks_alter_table(self):
        """Mythos Safe should block ALTER TABLE attempts."""
        connector = SapHanaSecureConnector.__new__(SapHanaSecureConnector)
        assert not connector.validate_prompt("ALTER TABLE users ADD COLUMN admin BOOLEAN;")

    def test_validate_prompt_blocks_union_select(self):
        """Mythos Safe should block UNION SELECT injection."""
        connector = SapHanaSecureConnector.__new__(SapHanaSecureConnector)
        assert not connector.validate_prompt("SELECT * FROM users UNION SELECT password FROM credentials;")

    def test_validate_prompt_blocks_comment_injection(self):
        """Mythos Safe should block comment-based injection."""
        connector = SapHanaSecureConnector.__new__(SapHanaSecureConnector)
        assert not connector.validate_prompt("SELECT * FROM users WHERE id=1 -- bypass")

    def test_validate_prompt_allows_safe_query(self):
        """Mythos Safe should allow safe SELECT queries."""
        connector = SapHanaSecureConnector.__new__(SapHanaSecureConnector)
        assert connector.validate_prompt("SELECT name, email FROM customers WHERE region = 'EU';")

    def test_mask_pii_redacts_emails(self):
        """PII masking should redact email addresses."""
        connector = SapHanaSecureConnector.__new__(SapHanaSecureConnector)
        data = [{"user": "john@example.com", "role": "admin"}]
        masked = connector.mask_pii(data)
        assert masked[0]["user"] == "[EMAIL_REDACTED]"

    def test_mask_pii_redacts_credit_cards(self):
        """PII masking should redact credit card numbers."""
        connector = SapHanaSecureConnector.__new__(SapHanaSecureConnector)
        data = [{"card": "4111-1111-1111-1111", "type": "visa"}]
        masked = connector.mask_pii(data)
        assert masked[0]["card"] == "[CREDIT_CARD_REDACTED]"
