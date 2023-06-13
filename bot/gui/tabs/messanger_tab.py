import asyncio

import dearpygui.dearpygui as dpg

from bot.scripts import send_messages
from bot.types_ import NetMode
from bot.settings import settings
from bot.input import accounts
from bot.logger import logger
from bot.config import get_messenger_chain_names

from .log_window import add_log_child_window


def add_messanger_tab():
    return zkMessangerTab()


class zkMessangerTab:
    def __init__(self):
        self.tag = dpg.generate_uuid()
        self.menu = dpg.generate_uuid()
        self.start_button = dpg.generate_uuid()

        with dpg.tab(tag=self.tag, label="zkMessanger"):
            with dpg.group(tag=self.menu):
                self.reload_menu()
            add_log_child_window()

    def _reload_menu(self, net_mode: NetMode):
        dpg.delete_item(self.menu, children_only=True)

        chain_names = get_messenger_chain_names(net_mode)

        with dpg.group(parent=self.menu):
            if chain_names:
                dpg.add_text("Choose source and target chains:", wrap=0)
                with dpg.group(horizontal=True):
                    dpg.add_radio_button(
                        chain_names,
                        default_value=settings.messenger.source_chain_name,
                        callback=lambda s, d: settings.messenger.__setattr__("source_chain_name", d),
                    )
                    dpg.add_radio_button(
                        chain_names,
                        default_value=settings.messenger.target_chain_name,
                        callback=lambda s, d: settings.messenger.__setattr__("target_chain_name", d),
                    )
                dpg.add_button(label="MESSAGE", tag=self.start_button, callback=self.message)
            else:
                dpg.add_text("There is no chains to message", wrap=0)

    def reload_menu(self):
        self._reload_menu(settings.net_mode)

    def message(self):
        dpg.disable_item(self.start_button)

        warnings = []
        if settings.messenger.source_chain_name == settings.messenger.target_chain_name:
            warnings.append("The same chains")
        if not accounts:
            warnings.append("No accounts found")

        if warnings:
            for warning_msg in warnings:
                logger.warning(warning_msg)
        else:
            dpg.configure_item(self.start_button, label="MESSAGING...")
            asyncio.run(send_messages(
                accounts, settings.net_mode, settings.messenger.source_chain_name,
                settings.messenger.target_chain_name))

        dpg.enable_item(self.start_button)
        dpg.configure_item(self.start_button, label="MESSAGE")
