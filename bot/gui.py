import webbrowser
import asyncio

import dearpygui.dearpygui as dpg

from bot.chains import chains
from bot.logger import logger
from bot.constants import NET_MODES, TOKEN_STANDARDS
from bot.input import load_accounts
from bot.bridge import bridge


def _hyperlink(text, address):
    dpg.add_button(label=text, callback=lambda: webbrowser.open(address))


def get_chain_names(net_mode: str) -> tuple[str]:
    return tuple(chains[net_mode].keys())


class App:
    def __init__(self):
        self.net_mode = NET_MODES[0]
        self.token_standard = TOKEN_STANDARDS[0]
        chain_names = get_chain_names(self.net_mode)
        self.source_chain_name = chain_names[0]
        self.target_chain_name = chain_names[0]

    def update_token_standard(self, _, app_data, user_data):
        self.token_standard = app_data

    def update_source_chain_name(self, _, app_data, user_data):
        self.source_chain_name = app_data

    def update_target_chain_name(self, _, app_data, user_data):
        self.target_chain_name = app_data

    def change_chains_widget(self, _, app_data, user_data):
        if self.net_mode != app_data:
            self.net_mode = app_data
            dpg.delete_item("chains", children_only=True)
            chain_names = get_chain_names(self.net_mode)
            dpg.add_radio_button(chain_names, parent="chains", callback=self.update_source_chain_name)
            dpg.add_radio_button(chain_names, parent="chains", callback=self.update_target_chain_name)

    def bridge(self):
        if self.source_chain_name == self.target_chain_name:
            logger.warning("The same chains")
            return
        accounts = load_accounts()
        if not accounts:
            logger.warning("No accounts found")
            return
        asyncio.run(bridge(accounts, self.net_mode, self.source_chain_name,
                    self.target_chain_name, self.token_standard))

    def launch(self):
        dpg.create_context()

        with dpg.window() as primary_window:
            with dpg.group(horizontal=True):
                _hyperlink("Telegram channel", "https://t.me/Cum_Insider")
                _hyperlink("GitHub", "https://github.com/AlenKimov/zk_nft_bridge")
            with dpg.group(horizontal=True):
                dpg.add_text("Net mode")
                dpg.add_combo(
                    NET_MODES,
                    default_value=self.net_mode,
                    callback=self.change_chains_widget,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Token standard")
                dpg.add_radio_button(
                    TOKEN_STANDARDS,
                    default_value=self.token_standard,
                    callback=self.update_token_standard,
                    horizontal=True,
                )
            dpg.add_text("Choose source and target chains:", wrap=0)
            with dpg.group(label="Choose the chains", horizontal=True, tag="chains"):
                chain_names = get_chain_names(self.net_mode)
                dpg.add_radio_button(chain_names, callback=self.update_source_chain_name)
                dpg.add_radio_button(chain_names, callback=self.update_target_chain_name)
            dpg.add_button(label="BRIDGE", callback=self.bridge)

        dpg.set_primary_window(primary_window, True)
        dpg.create_viewport(title="zkBridge by @AlenKimov", width=440, height=460)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


if __name__ == '__main__':
    app = App()
    app.launch()
