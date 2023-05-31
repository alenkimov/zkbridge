import tomllib

from pydantic import BaseSettings

from bot.paths import CONFIG_DIR


class Config(BaseSettings):
    LOGGING_LEVEL: str = "INFO"
    TESTNET: bool = True
    CHAIN_NAME_FROM: str
    CHAIN_NAME_TO: str
    TOKEN_STANDARD: str = "ERC721"


CONFIG_TOML = CONFIG_DIR / "config.toml"


if CONFIG_TOML.exists():
    with open(CONFIG_TOML, "rb") as config_toml:
        config = Config(**tomllib.load(config_toml))
else:
    raise FileNotFoundError(f"Config file not found")

