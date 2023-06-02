import tomllib
from typing import Literal

from pydantic import BaseSettings

from bot.paths import CONFIG_DIR


class Config(BaseSettings):
    LOGGING_LEVEL: str = "INFO"
    NET_MODE: Literal["testnet", "mainnet"]
    SOURCE_CHAIN_NAME: str
    TARGET_CHAIN_NAME: str
    TOKEN_STANDARD: str


CONFIG_TOML = CONFIG_DIR / "config.toml"


if CONFIG_TOML.exists():
    with open(CONFIG_TOML, "rb") as config_toml:
        config = Config(**tomllib.load(config_toml))
else:
    raise FileNotFoundError(f"Config file not found")

