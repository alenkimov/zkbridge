from bot.utils import load_json, load_toml
from .paths import ASSETS_DIR, ABI_DIR


CHAINS_DATA = load_toml(ASSETS_DIR / "chains.toml")

ADDITIONAL_DATA = load_json(ASSETS_DIR / "additional_chains_data.json")
RECEIVERS_DATA  = load_json(ASSETS_DIR / "receivers.json")
SENDERS_DATA    = load_json(ASSETS_DIR / "senders.json")
RECEIVER_ABI    = load_json(ABI_DIR / "receiver.json")
SENDER_ABI      = load_json(ABI_DIR / "sender.json")
