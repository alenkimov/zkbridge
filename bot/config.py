import shutil
from pathlib import Path

from pydantic import BaseSettings

from bot.paths import CONFIG_DIR, DEFAULT_CONFIG_DIR
from bot.utils import load_toml


def copy_file(source_path: Path, destination_path: Path):
    if destination_path.exists():
        return
    shutil.copy2(str(source_path), str(destination_path))


CONFIG_DIR.mkdir(exist_ok=True)

chains_toml_path = CONFIG_DIR / "chains.toml"
copy_file(DEFAULT_CONFIG_DIR / "chains.toml", chains_toml_path)

config_toml_path = CONFIG_DIR / "config.toml"
copy_file(DEFAULT_CONFIG_DIR / "config.toml", config_toml_path)


CHAINS_DATA = load_toml(chains_toml_path)


class Config(BaseSettings):
    LOGGING_LEVEL: str = "INFO"


config = Config(**load_toml(config_toml_path))
