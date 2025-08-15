from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "ecommerce"
    DB_USER: str = "ecom_user"
    DB_PASS: str = "ecom_pass"

    JWT_SECRET: str = "change_this_secret"
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MIN: int = 120   # minutos (se sobreescribe por .env)

    AUTH_PORT: int = 8001

    # Si tu .env está en la raíz del repo, apunta directo:
    # env_file="../../.env"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,  # acepta jwt_expire_min o JWT_EXPIRE_MIN
    )

    @field_validator("JWT_EXPIRE_MIN", mode="before")
    @classmethod
    def _strip_inline_comments_and_cast(cls, v):
        # Permite valores como: "43200 # 30 días"
        if isinstance(v, str):
            v = v.split("#", 1)[0].strip().strip('"').strip("'")
            if not v:
                return 120
            return int(v)
        return v

settings = Settings()