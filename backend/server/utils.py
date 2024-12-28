from jose import JWTError, jwt
from nexusai.config import NEXTAUTH_SECRET


def validate_token(token: str) -> bool:
    try:
        jwt.decode(token, NEXTAUTH_SECRET, algorithms=["HS256"])
        return True
    except JWTError:
        return False
