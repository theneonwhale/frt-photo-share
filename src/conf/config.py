from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = 'postgresql+psycopg2://user:password@localhost:5432/postgres'
    secret_key: str = 'secret_key'
    algorithm: str = 'HS256'
    mail_username: str = 'example@meta.ua'
    mail_password: str = 'password'
    mail_from: str = 'example@meta.ua'
    mail_port: int = 465
    mail_server: str = 'smtp.meta.ua'
    mail_from_name: str = 'sender: app photo-share'
    redis_host: str = 'localhost'
    redis_password: str = 'password'
    redis_port: int = 6379
    cloudinary_name: str = 'name'
    cloudinary_api_key: int = 1
    cloudinary_api_secret: str = 'secret'
    limit_crit: int = 12
    limit_warn: int = 2

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
