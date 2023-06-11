import webbrowser

import dearpygui.dearpygui as dpg

from bot.author import TG, GITHUB


def add_menu_bar():
    with dpg.menu_bar():
        with dpg.menu(label="View"):
            dpg.add_menu_item(label="Toggle Fullscreen",
                              callback=lambda: dpg.toggle_viewport_fullscreen())
        with dpg.menu(label="Sources"):
            dpg.add_menu_item(label="Telegram channel",
                              callback=lambda: webbrowser.open(TG))
            dpg.add_menu_item(label="GitHub",
                              callback=lambda: webbrowser.open(GITHUB))
