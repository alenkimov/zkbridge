import dearpygui.dearpygui as dpg

from bot.constants import NET_MODES
from bot.paths import SETTINGS_DIR
from bot.settings import settings
from .wallets_tab import add_wallets_tab
from .chains_tab import add_chains_tab
from .bridge_tab import add_zkbridge_tab
from .menu_bar import add_menu_bar
from .messager_tab import add_messanger_tab


dpg.create_context()
dpg.configure_app(init_file=SETTINGS_DIR / "gui.ini")


def change_net_mode(_, app_data, user_data):
    settings.net_mode = app_data
    chains_tab.reload_table()
    wallets_tab.reload_table()
    zkbridge_tab.reload_chains()
    messanger_tab.reload_menu()


with dpg.window() as primary_window:
    add_menu_bar()

    with dpg.group(horizontal=True):
        dpg.add_text("Net mode")
        dpg.add_combo(
            NET_MODES,
            default_value=settings.net_mode,
            callback=change_net_mode,
        )

    with dpg.tab_bar():
        chains_tab = add_chains_tab()
        wallets_tab = add_wallets_tab()
        zkbridge_tab = add_zkbridge_tab()
        messanger_tab = add_messanger_tab()


def launch():
    dpg.set_primary_window(primary_window, True)
    dpg.create_viewport(title="zkBridge by @AlenKimov", width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    try:
        dpg.start_dearpygui()
    finally:
        settings.save()
        dpg.destroy_context()
