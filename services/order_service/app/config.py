from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"  # .../Ecommerce/.env

class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "ecommerce"
    DB_USER: str = "ecom_user"
    DB_PASS: str = "ecom_pass"

    JWT_SECRET: str = "change_this_secret"
    JWT_ALG: str = "HS256"

    ORDER_PORT: int = 8005  # usamos 8005 para no chocar con cart en 8004

    model_config = SettingsConfigDict(
        env_file=str(ROOT_ENV),
        env_file_encoding="utf-8",
        extra="ignore",  # ignorar variables extra del .env
    )

settings = Settings()
