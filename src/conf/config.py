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
    redis_password: str = ''
    redis_port: int = 6379
    cloudinary_name: str = 'name'
    cloudinary_api_key: int = 1
    cloudinary_api_secret: str = 'secret'
    limit_crit: int = 12
    limit_warn: int = 2
    tags_limit: int = 5
    limit_crit_timer: int = 60 # seconds
    access_token_timer: int = 1 # hours
    refresh_token_timer: int = 168 # hours
    email_token_timer: int = 1 # hours
    password_reset_token_timer: int = 1 # hours
    redis_user_timer: int = 3600 # seconds
    redis_addition_lag: int = 300
    break_point: int = 8
    password_length: int = 12

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
