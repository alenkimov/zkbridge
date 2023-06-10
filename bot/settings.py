from pydantic import BaseModel

from bot.chains import get_chain_names
from bot.paths import SETTINGS_DIR
from bot.types_ import NetMode, TokenStandard
from bot.utils import load_json, rewrite_json

SETTINGS_DIR.mkdir(exist_ok=True)
settings_filepath = SETTINGS_DIR / "settings.json"

chain_names = get_chain_names("testnet")


class Settings(BaseModel):
    net_mode: NetMode = "testnet"
    token_standard: TokenStandard = "ERC721"
    source_chain_name: str = chain_names[0]
    target_chain_name: str = chain_names[0]

    def save(self):
        rewrite_json(settings_filepath, self.dict())


if settings_filepath.exists():
    settings = Settings(**load_json(settings_filepath))
else:
    settings = Settings()
