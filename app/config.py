from functools import lru_cache
import os 

from pydantic import BaseSettings, Field

os.environ['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = '1'
class Settings(BaseSettings):
    db_client_id: str = Field(..., env="ASTRA_DB_CLIENT_ID")
    db_client_secret: str = Field(..., env="ASTRA_DB_CLIENT_SECRET")

    class Config:
        env_file = '.env'

@lru_cache(maxsize=None)
def get_settings():
    return Settings()