from jose import JWTError, jwt
from nexusai.config import NEXTAUTH_SECRET


def validate_jwt(token: str) -> bool:
    """Validate jwt."""
    try:
        jwt.decode(token, NEXTAUTH_SECRET, algorithms=["HS256"])
        return True
    except JWTError:
        return False
