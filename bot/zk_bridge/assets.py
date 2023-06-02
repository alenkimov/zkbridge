from bot.utils import load_json
from .paths import ASSETS_DIR, ABI_DIR


ADDITIONAL_DATA_FILEPATH = ASSETS_DIR / "additional_chains_data.json"
RECEIVERS_FILEPATH       = ASSETS_DIR / "receivers.json"
SENDERS_FILEPATH         = ASSETS_DIR / "senders.json"
RECEIVER_ABI_FILEPATH    = ABI_DIR / "receiver.json"
SENDER_ABI_FILEPATH      = ABI_DIR / "sender.json"

ADDITIONAL_DATA = load_json(ADDITIONAL_DATA_FILEPATH)
RECEIVERS_DATA  = load_json(RECEIVERS_FILEPATH)
SENDERS_DATA    = load_json(SENDERS_FILEPATH)
RECEIVER_ABI    = load_json(RECEIVER_ABI_FILEPATH)
SENDER_ABI      = load_json(SENDER_ABI_FILEPATH)
