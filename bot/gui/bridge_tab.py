import asyncio

import dearpygui.dearpygui as dpg

from bot.bridge import bridge as _bridge
from bot.chains import get_chain_names
from bot.constants import TOKEN_STANDARDS
from bot.types_ import NetMode
from bot.settings import settings
from bot.input import accounts
from bot.logger import logger
from .log_window import add_log_child_window


def add_zkbridge_tab():
    return zkBridgeTab()


class zkBridgeTab:
    def __init__(self):
        self.tag = dpg.generate_uuid()
        self.chains_buttons_group = dpg.generate_uuid()
        self.bridge_button = dpg.generate_uuid()

        with dpg.tab(tag=self.tag, label="zkBridge"):
            with dpg.group(horizontal=True):
                dpg.add_text("Token standard")
                dpg.add_radio_button(
                    TOKEN_STANDARDS,
                    default_value=settings.token_standard,
                    callback=lambda s, d: settings.__setattr__("token_standard", d),
                    horizontal=True,
                )
            dpg.add_text("Choose source and target chains:", wrap=0)
            with dpg.group(label="Choose the chains", horizontal=True, tag=self.chains_buttons_group):
                self.reload_chains()
            dpg.add_button(label="MINT and BRIDGE", tag=self.bridge_button, callback=self.bridge)
            add_log_child_window()

    def _reload_chains(self, net_mode: NetMode):
        dpg.delete_item(self.chains_buttons_group, children_only=True)

        chain_names = get_chain_names(net_mode)
        dpg.add_radio_button(
            chain_names,
            parent=self.chains_buttons_group,
            default_value=settings.source_chain_name,
            callback=lambda s, d: settings.__setattr__("source_chain_name", d),
        )
        dpg.add_radio_button(
            chain_names,
            parent=self.chains_buttons_group,
            default_value=settings.target_chain_name,
            callback=lambda s, d: settings.__setattr__("target_chain_name", d),
        )

    def reload_chains(self):
        self._reload_chains(settings.net_mode)

    def bridge(self):
        dpg.disable_item(self.bridge_button)

        warnings = []
        if settings.source_chain_name == settings.target_chain_name:
            warnings.append("The same chains")
        if not accounts:
            warnings.append("No accounts found")

        if warnings:
            for warning_msg in warnings:
                logger.warning(warning_msg)
        else:
            dpg.configure_item(self.bridge_button, label="BRIDGING...")
            asyncio.run(_bridge(accounts, settings.net_mode, settings.source_chain_name,
                                settings.target_chain_name, settings.token_standard))

        dpg.enable_item(self.bridge_button)
        dpg.configure_item(self.bridge_button, label="MINT and BRIDGE")
