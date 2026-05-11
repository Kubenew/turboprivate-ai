from turbo.auth.jwt import JWTManager


def test_jwt_roundtrip():
    mgr = JWTManager(secret="test-secret")
    token = mgr.create_token({"sub": "user1", "role": "admin"})
    payload = mgr.verify_token(token)
    assert payload["sub"] == "user1"
    assert payload["role"] == "admin"


def test_jwt_invalid():
    mgr = JWTManager(secret="test-secret")
    assert mgr.verify_token("invalid") is None
