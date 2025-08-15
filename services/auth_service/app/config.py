from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "ecommerce"
    DB_USER: str = "ecom_user"
    DB_PASS: str = "ecom_pass"

    JWT_SECRET: str = "change_this_secret"
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MIN: int = 120

    AUTH_PORT: int = 8001

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
