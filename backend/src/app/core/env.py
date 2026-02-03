from pydantic import PostgresDsn, RedisDsn, ValidationError, AmqpDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


class FastAPISettings:
    
    app_host: str = "localhost"
    app_port: int = 8000 
    app_title: str
    app_description: str
    api_prefix: str = "/api/v1/auth"
    debug: bool = False
    


class SMTPSettings:
    
    smtp_mail_username: str
    smtp_mail_password: str
    smtp_mail_from: str
    smtp_mail_port: int
    smtp_mail_host: str
    smtp_mail_starttls: bool
    smtp_mail_ssl_tls: bool
    smtp_debug: bool = True


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
    
    
class RabbitMQSettings:

    amqp_user: str
    amqp_password: str
    amqp_host: str
    amqp_port: int = 5672

    @property
    def rabbitmq_url(self) -> str:

        return AmqpDsn.build(
            scheme="amqp",
            host=self.amqp_host,
            port=self.amqp_port,
            username=self.amqp_user,
            password=self.amqp_password,
        ).unicode_string()
    
    
class CacheAdapter:

    cache_adapter: str = "redis"
    cache_adapter_host: str = "localhost"
    cache_adapter_port: int = 6379

    @property
    def cache_url(self) -> str:

        if self.cache_adapter.lower() in ("redis", "keydb"):
            return RedisDsn.build(
                scheme=self.cache_adapter.lower(),
                host=self.cache_adapter_host,
                port=self.cache_adapter_port,
            ).unicode_string()

        return ""


class JWTSettings:

    hash_secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    
class Settings(
    BaseSettings,
    FastAPISettings,
    DBSettings,
    JWTSettings,
    CacheAdapter,
    SMTPSettings,
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
    