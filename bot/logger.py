import logging
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from bot.config import config
from bot.paths import LOG_DIR


LOG_DIR.mkdir(exist_ok=True)
FILE_LOG_FORMAT = "<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <white>{message}</white>"
CONSOLE_LOG_FORMAT = "<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <white>{message}</white>"


class InterceptHandler(logging.Handler):
    LEVELS_MAP = {
        logging.CRITICAL: "CRITICAL",
        logging.ERROR: "ERROR",
        logging.WARNING: "WARNING",
        logging.INFO: "INFO",
        logging.DEBUG: "DEBUG",
    }

    def _get_level(self, record):
        return self.LEVELS_MAP.get(record.levelno, record.levelno)

    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(self._get_level(record), record.getMessage())


def setup(level="DEBUG"):
    logger.remove()
    log_file_name = f"{datetime.now().strftime('%d-%m-%Y')}.log"
    log_file_path = Path(LOG_DIR, log_file_name)
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
    logger.add(log_file_path, format=FILE_LOG_FORMAT, level=level, rotation='1 day')
    logger.add(sys.stderr, colorize=True, format=CONSOLE_LOG_FORMAT, level=level)


setup(config.LOGGING_LEVEL)
