from pydantic import BaseModel

class _Settings(BaseModel):
    ALLOW_ORIGINS: list[str] = ["*"]

settings = _Settings()
