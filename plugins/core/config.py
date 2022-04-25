import yaml
from typing import Dict, Any

from pydantic import BaseModel


def yaml_config_settings_source() -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a JSON file
    at the project's root.

    Here we happen to choose to use the `env_file_encoding` from Config
    when reading `config.json`
    """

    with open("config/test.yaml", 'r') as stream:
        config = yaml.safe_load(stream)

    return config


class Config(BaseModel):
    timeout_for_chat: int
    debug: bool
    use_black_list: bool
    numbers_of_attemp: int
    bot_token: str


class CacheConfig(BaseModel):
    host: str
    port: int


class Cache(BaseModel):
    cache_type: str
    config: CacheConfig


class DbConfig(BaseModel):
    host: str
    port: int
    url: str


class Db(BaseModel):
    db_type: str
    config: DbConfig


class App(BaseModel):
    configuration: Config
    cache: Cache
    db: Db


class Settings(BaseModel):
    app: App


setting = Settings(**yaml_config_settings_source())


