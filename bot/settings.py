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


class Settings(BaseModel):
    net_mode: NetMode = "testnet"
    token_standard: TokenStandard = config.TOKEN_STANDARDS[0]
    bridge: ModuleChainNames = ModuleChainNames(
        source_chain_name=config.BRIDGE_CHAINS.TESTNET[0] if config.BRIDGE_CHAINS.TESTNET else None,
        target_chain_name=config.BRIDGE_CHAINS.TESTNET[0] if config.BRIDGE_CHAINS.TESTNET else None,
    )
    messenger: ModuleChainNames = ModuleChainNames(
        source_chain_name=config.MESSENGER_CHAINS.TESTNET[0] if config.MESSENGER_CHAINS.TESTNET else None,
        target_chain_name=config.MESSENGER_CHAINS.TESTNET[0] if config.MESSENGER_CHAINS.TESTNET else None,
    )

    def save(self):
        rewrite_json(settings_filepath, self.dict())


if settings_filepath.exists():
    settings = Settings(**load_json(settings_filepath))
else:
    settings = Settings()
