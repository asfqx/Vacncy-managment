from pydantic import PostgresDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


class FastAPISettings:
    
    app_host: str = "localhost"
    app_port: int = 8000 
    app_title: str
    app_description: str
    
    
class DBSettings:
    
    postgres_host: str 
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    
    @property
    def db_url(self) -> str:
        
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
        ).unicode_string()
    
    
class JWTSettings:

    hash_secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    
class Settings(
    BaseSettings,
    FastAPISettings,
    DBSettings,
    JWTSettings,
):
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    

try:
    settings = Settings()
    logger.success("Загрузка настроек прошла успешно")
    
except ValidationError as e:
    logger.error(f"Ошибка в загрузке настроек: {e}")
    