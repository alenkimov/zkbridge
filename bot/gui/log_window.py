import dearpygui.dearpygui as dpg

from bot.logger import logger, CONSOLE_LOG_FORMAT
from bot.config import config


def add_log_child_window():
    return LogChildWindow()


class LogChildWindow:
    def __init__(self):
        self.tag = dpg.add_child_window(label="Output")
        logger.add(self.print_log, level=config.LOGGING_LEVEL, format=CONSOLE_LOG_FORMAT)

    def print_log(self, log_message: str):
        dpg.add_text(log_message, wrap=0, parent=self.tag)
