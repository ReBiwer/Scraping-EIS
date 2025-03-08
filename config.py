import os
import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv()

class Settings(BaseSettings):
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "0.0.0.0")
    REDIS_PORT: str = os.environ.get("REDIS_PORT", "6379")
    REDIS_NUM_DB: str = os.environ.get("REDIS_NUM_DB", "0")

    @property
    def url_redis(self):
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_NUM_DB}'

settings = Settings()
