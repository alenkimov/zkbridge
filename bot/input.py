from pathlib import Path

from eth_account.account import LocalAccount, Account

from bot.paths import INPUT_DIR
from bot.logger import logger


if not INPUT_DIR.exists():
    INPUT_DIR.mkdir()
    logger.info(f"Создал папку для входных данных {INPUT_DIR}")


PRIVATE_KEYS_TXT = INPUT_DIR / "private_keys.txt"


def _load_accounts(filepath: Path) -> set[LocalAccount]:
    if not filepath.exists():
        with open(filepath, "w"):
            pass
        logger.info(f"Создал файл {filepath}")
    with open(filepath, "r") as file:
        accounts: set[LocalAccount] = {Account.from_key(key.strip()) for key in file.readlines() if key != "\n"}
    return accounts


def load_accounts() -> set[LocalAccount]:
    return _load_accounts(PRIVATE_KEYS_TXT)
