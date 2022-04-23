from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_ID: int = 8146243
    ACCESS_TOKEN: str = 'YOUR ACCESS TOKEN FROM .env FILE'

    RELOAD: bool = False

    IMAGES_PATH = 'images'
    IMAGES_BATCH_SIZE: int = 50

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
