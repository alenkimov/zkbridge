from typing import Iterable

from eth_account.account import LocalAccount, Account

from bot.paths import INPUT_DIR
from bot.utils import load_lines, rewrite_lines


INPUT_DIR.mkdir(exist_ok=True)
PRIVATE_KEYS_TXT = INPUT_DIR / "private_keys.txt"


def load_private_keys() -> set[str]:
    """
    Загружает приватные ключи из файла.
    Если файл не существует, создает новый пустой файл.
    """
    if not PRIVATE_KEYS_TXT.exists():
        PRIVATE_KEYS_TXT.touch()
    return set(load_lines(PRIVATE_KEYS_TXT))


def rewrite_accounts(accounts: Iterable[LocalAccount]):
    private_keys = [account.key.hex() for account in accounts]
    rewrite_lines(PRIVATE_KEYS_TXT, private_keys)


def load_accounts() -> list[LocalAccount]:
    return [Account.from_key(key.strip()) for key in load_private_keys()]


accounts = load_accounts()
