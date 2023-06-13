from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
SETTINGS_DIR = BASE_DIR / "settings"
DEFAULT_CONFIG_DIR = BASE_DIR / "default_config"
DATABASE_DIR = BASE_DIR / "database"
CONFIG_DIR = BASE_DIR / "config"
OUTPUT_DIR = BASE_DIR / "output"
INPUT_DIR  = BASE_DIR / "input"
LOG_DIR    = BASE_DIR / "log"
