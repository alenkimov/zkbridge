from bot.utils import load_json
from .paths import CONFIG_DIR


ADDITIONAL_DATA = load_json(CONFIG_DIR / "additional_chains_data.json")
RECEIVERS_DATA  = load_json(CONFIG_DIR / "receivers.json")
SENDERS_DATA    = load_json(CONFIG_DIR / "senders.json")
MAILERS_DATA    = load_json(CONFIG_DIR / "mailers.json")
