import webbrowser
import asyncio

import dearpygui.dearpygui as dpg

from bot.chains import get_chain_names
from bot.logger import logger
from bot.input import load_accounts
from bot.bridge import bridge as _bridge
from bot.settings import settings
from bot.paths import SETTINGS_DIR
from bot.constants import NET_MODES, TOKEN_STANDARDS


dpg_ini_filepath = SETTINGS_DIR / "dpg.ini"
dpg.create_context()
dpg.configure_app(init_file=dpg_ini_filepath)


def _hyperlink(text, address):
    dpg.add_button(label=text, callback=lambda: webbrowser.open(address))


def change_chains_widget(_, app_data, user_data):
    if settings.net_mode != app_data:
        settings.net_mode = app_data
        dpg.delete_item("chains", children_only=True)
        chain_names = get_chain_names(settings.net_mode)
        dpg.add_radio_button(chain_names, parent="chains", callback=lambda s, d: settings.__setattr__("source_chain_name", d))
        dpg.add_radio_button(chain_names, parent="chains", callback=lambda s, d: settings.__setattr__("target_chain_name", d))


def bridge():
    if settings.source_chain_name == settings.target_chain_name:
        logger.warning("The same chains")
        return
    accounts = load_accounts()
    if not accounts:
        logger.warning("No accounts found")
        return
    asyncio.run(_bridge(accounts, settings.net_mode, settings.source_chain_name,
                settings.target_chain_name, settings.token_standard))


def launch():
    with dpg.window() as primary_window:
        with dpg.group(horizontal=True):
            _hyperlink("Telegram channel", "https://t.me/Cum_Insider")
            _hyperlink("GitHub", "https://github.com/AlenKimov/zk_nft_bridge")
        with dpg.group(horizontal=True):
            dpg.add_text("Net mode")
            dpg.add_combo(
                NET_MODES,
                default_value=settings.net_mode,
                callback=change_chains_widget,
            )
        with dpg.group(horizontal=True):
            dpg.add_text("Token standard")
            dpg.add_radio_button(
                TOKEN_STANDARDS,
                default_value=settings.token_standard,
                callback=lambda s, d: settings.__setattr__("token_standard", d),
                horizontal=True,
            )
        dpg.add_text("Choose source and target chains:", wrap=0)
        with dpg.group(label="Choose the chains", horizontal=True, tag="chains"):
            chain_names = get_chain_names(settings.net_mode)
            dpg.add_radio_button(
                chain_names,
                default_value=settings.source_chain_name,
                callback=lambda s, d: settings.__setattr__("source_chain_name", d),
            )
            dpg.add_radio_button(
                chain_names,
                default_value=settings.target_chain_name,
                callback=lambda s, d: settings.__setattr__("target_chain_name", d),
            )
        dpg.add_button(label="MINT and BRIDGE", callback=bridge)

    dpg.set_primary_window(primary_window, True)
    dpg.create_viewport(title="zkBridge by @AlenKimov", width=440, height=460)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    try:
        dpg.start_dearpygui()
    finally:
        settings.save()
        dpg.destroy_context()
