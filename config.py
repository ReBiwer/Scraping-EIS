import os
import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv()

class Settings(BaseSettings):
    REDIS_HOST = os.environ.get("REDIS_HOST", "0.0.0.0")
    REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
    REDIS_NUM_DB = os.environ.get("REDIS_NUM_DB", "0")
    url_redis = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_NUM_DB}'

settings = Settings()
