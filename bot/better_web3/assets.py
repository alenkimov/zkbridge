from bot.utils import load_json
from .paths import ASSETS_DIR


CHAINS_FILEPATH = ASSETS_DIR / "chains.json"
CHAINS_DATA     = load_json(CHAINS_FILEPATH)



