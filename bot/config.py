from pydantic import BaseModel

from bot.logger import LoggingLevel, setup_logger
from bot.paths import CONFIG_DIR, DEFAULT_CONFIG_DIR, LOG_DIR
from bot.types_ import NetMode
from bot.zk_bridge.types_ import TokenStandard
from bot.utils import load_toml, copy_file

CONFIG_DIR.mkdir(exist_ok=True)

chains_toml_path = CONFIG_DIR / "chains.toml"
copy_file(DEFAULT_CONFIG_DIR / "chains.toml", chains_toml_path)

config_toml_path = CONFIG_DIR / "config.toml"
copy_file(DEFAULT_CONFIG_DIR / "config.toml", config_toml_path)

CHAINS_DATA = load_toml(chains_toml_path)


class AvailableChains(BaseModel):
    MAINNET: list[str]
    TESTNET: list[str]


class Config(BaseModel):
    LOGGING_LEVEL: "LoggingLevel"
    BRIDGE_CHAINS: AvailableChains
    MESSENGER_CHAINS: AvailableChains
    TOKEN_STANDARDS: list[TokenStandard]
    DELAY: list[int]
    RESIZE_PICTURE: bool
    BATCH_REQUEST_SIZE: int
    BATCH_REQUEST_DELAY: int
    IGNORE_ERRORS: bool


config = Config(**load_toml(config_toml_path))


def get_bridge_chain_names(net_mode: NetMode) -> list[str]:
    chain_names = []
    if net_mode == "testnet":
        chain_names = config.BRIDGE_CHAINS.TESTNET
    elif net_mode == "mainnet":
        chain_names = config.BRIDGE_CHAINS.MAINNET
    return chain_names


def get_messenger_chain_names(net_mode: NetMode) -> list[str]:
    chain_names = []
    if net_mode == "testnet":
        chain_names = config.MESSENGER_CHAINS.TESTNET
    elif net_mode == "mainnet":
        chain_names = config.MESSENGER_CHAINS.MAINNET
    return chain_names


setup_logger(LOG_DIR, config.LOGGING_LEVEL)
