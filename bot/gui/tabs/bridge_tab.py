import asyncio

import dearpygui.dearpygui as dpg

from bot.scripts import mint_and_bridge
from bot.types_ import NetMode
from bot.settings import settings
from bot.input import accounts
from bot.logger import logger
from bot.config import get_bridge_chain_names, config

from .log_window import add_log_child_window


def add_zkbridge_tab():
    return ZkBridgeTab()


class ZkBridgeTab:
    def __init__(self):
        self.tag = dpg.generate_uuid()
        self.interaction_menu = dpg.generate_uuid()
        self.start_button = dpg.generate_uuid()

        with dpg.tab(tag=self.tag, label="zkBridge"):
            with dpg.group(horizontal=True):
                dpg.add_text("Token standard")
                dpg.add_radio_button(
                    config.TOKEN_STANDARDS,
                    default_value=settings.token_standard,
                    callback=lambda s, d: settings.__setattr__("token_standard", d),
                    horizontal=True,
                )
            with dpg.group(tag=self.interaction_menu):
                self.reload_chains()

            add_log_child_window()

    def _reload_chains(self, net_mode: NetMode):
        dpg.delete_item(self.interaction_menu, children_only=True)

        chain_names = get_bridge_chain_names(net_mode)

        with dpg.group(parent=self.interaction_menu):
            if chain_names:
                dpg.add_text("Choose the source and target chains:", wrap=0)
                with dpg.group(horizontal=True):
                    dpg.add_radio_button(
                        chain_names,
                        default_value=getattr(settings.bridge, net_mode).source_chain_name,
                        callback=lambda s, d: setattr(getattr(settings.bridge, net_mode), "source_chain_name", d),
                    )
                    dpg.add_radio_button(
                        chain_names,
                        default_value=getattr(settings.bridge, net_mode).target_chain_name,
                        callback=lambda s, d: setattr(getattr(settings.bridge, net_mode), "target_chain_name", d),
                    )
                dpg.add_button(label="MINT and BRIDGE", tag=self.start_button, callback=self.bridge)
            else:
                dpg.add_text("There is no chains to bridge", wrap=0)

    def reload_chains(self):
        self._reload_chains(settings.net_mode)

    def _bridge(self, net_mode: NetMode):
        dpg.disable_item(self.start_button)

        chain_names = getattr(settings.bridge, net_mode)

        warnings = []
        if chain_names.source_chain_name == chain_names.target_chain_name:
            warnings.append("The same chains")
        if not accounts:
            warnings.append("No accounts found")

        if warnings:
            for warning_msg in warnings:
                logger.warning(warning_msg)
        else:
            dpg.configure_item(self.start_button, label="BRIDGING...")
            asyncio.run(mint_and_bridge(
                accounts, settings.net_mode, chain_names.source_chain_name,
                chain_names.target_chain_name, settings.token_standard))

        dpg.enable_item(self.start_button)
        dpg.configure_item(self.start_button, label="MINT and BRIDGE")

    def bridge(self):
        return self._bridge(settings.net_mode)
