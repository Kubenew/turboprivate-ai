from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt


class JWTManager:
    def __init__(self, secret: str, algorithm: str = "HS256", expire_minutes: int = 60):
        self.secret = secret
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def create_token(self, data: dict) -> str:
        to_encode = data.copy()
        to_encode["exp"] = datetime.now(UTC) + timedelta(minutes=self.expire_minutes)
        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except JWTError:
            return None
