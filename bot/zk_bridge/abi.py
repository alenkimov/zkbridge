from bot.utils import load_json
from .paths import ABI_DIR

RECEIVER_ABI = load_json(ABI_DIR / "receiver.json")
SENDER_ABI   = load_json(ABI_DIR / "sender.json")
MAILER_ABI   = load_json(ABI_DIR / "mailer.json")
