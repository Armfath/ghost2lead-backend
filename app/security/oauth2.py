from fastapi.security import OAuth2PasswordBearer

from app.core.config import configs

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{configs.API_V1}/auth/verify-otp",
    scheme_name="Bearer",
)
