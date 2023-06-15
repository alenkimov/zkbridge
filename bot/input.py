from typing import Iterable
from pathlib import Path

from eth_account.account import LocalAccount, Account

from bot.paths import INPUT_DIR
from bot.utils import load_lines, rewrite_lines


INPUT_DIR.mkdir(exist_ok=True)

IMAGES_DIR = INPUT_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)

PRIVATE_KEYS_TXT = INPUT_DIR / "private_keys.txt"
USED_IMAGES_TXT = INPUT_DIR / "used_images.txt"
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".gif", ".tiff")


def load_private_keys() -> set[str]:
    """
    Загружает приватные ключи из файла.
    Если файл не существует, создает новый пустой файл.
    """
    if not PRIVATE_KEYS_TXT.exists():
        PRIVATE_KEYS_TXT.touch()
    return set(load_lines(PRIVATE_KEYS_TXT))


def load_used_images() -> set[str]:
    if not USED_IMAGES_TXT.exists():
        USED_IMAGES_TXT.touch()
    return set(load_lines(USED_IMAGES_TXT))


def rewrite_accounts(accounts: Iterable[LocalAccount]):
    private_keys = [account.key.hex() for account in accounts]
    rewrite_lines(PRIVATE_KEYS_TXT, private_keys)


def rewrite_used_images(image_names: Iterable[str]):
    rewrite_lines(USED_IMAGES_TXT, image_names)


def load_accounts() -> list[LocalAccount]:
    return [Account.from_key(key.strip()) for key in load_private_keys()]


def _get_image_filenames(directory: Path) -> set[str]:
    return {entry.name for entry in directory.iterdir() if entry.is_file() and entry.suffix.lower() in IMAGE_EXT}


def get_image_filenames() -> set[str]:
    return _get_image_filenames(IMAGES_DIR)


accounts = load_accounts()
used_images = load_used_images()
