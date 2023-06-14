from pydantic import BaseModel

from bot.paths import SETTINGS_DIR
from bot.types_ import NetMode
from bot.zk_bridge.types_ import TokenStandard
from bot.utils import load_json, rewrite_json
from bot.config import config

SETTINGS_DIR.mkdir(exist_ok=True)
settings_filepath = SETTINGS_DIR / "settings.json"


class ModuleChainNames(BaseModel):
    source_chain_name: str or None = None
    target_chain_name: str or None = None


class ModuleChainNamesByNetMode(BaseModel):
    testnet: ModuleChainNames
    mainnet: ModuleChainNames


class Settings(BaseModel):
    net_mode: NetMode
    token_standard: TokenStandard
    bridge: ModuleChainNamesByNetMode
    messenger: ModuleChainNamesByNetMode

    def save(self):
        rewrite_json(settings_filepath, self.dict())


default_settings = {
    "net_mode": "testnet",
    "token_standard": config.TOKEN_STANDARDS[0],
    "bridge": {
        "testnet": {
            "source_chain_name": config.BRIDGE_CHAINS.TESTNET[0] if config.BRIDGE_CHAINS.TESTNET else None,
            "target_chain_name": config.BRIDGE_CHAINS.TESTNET[0] if config.BRIDGE_CHAINS.TESTNET else None,
        },
        "mainnet": {
            "source_chain_name": config.BRIDGE_CHAINS.MAINNET[0] if config.BRIDGE_CHAINS.MAINNET else None,
            "target_chain_name": config.BRIDGE_CHAINS.MAINNET[0] if config.BRIDGE_CHAINS.MAINNET else None,
        },
    },
    "messenger": {
        "testnet": {
            "source_chain_name": config.MESSENGER_CHAINS.TESTNET[0] if config.MESSENGER_CHAINS.TESTNET else None,
            "target_chain_name": config.MESSENGER_CHAINS.TESTNET[0] if config.MESSENGER_CHAINS.TESTNET else None,

        },
        "mainnet": {
            "source_chain_name": config.MESSENGER_CHAINS.MAINNET[0] if config.MESSENGER_CHAINS.MAINNET else None,
            "target_chain_name": config.MESSENGER_CHAINS.MAINNET[0] if config.MESSENGER_CHAINS.MAINNET else None,
        },
    }
}


if settings_filepath.exists():
    settings = Settings(**load_json(settings_filepath))
else:
    settings = Settings(**default_settings)
