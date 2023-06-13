import webbrowser

import dearpygui.dearpygui as dpg

from bot.author import TG, GITHUB, DONATE_WALLET
from .utils import add_text_to_copy


def open_donate_window(button: str | int):
    DonateWindow(button)


class DonateWindow:
    def __init__(self, button: str | int):
        self.tag = dpg.generate_uuid()
        self.button = button

        dpg.disable_item(self.button)

        with dpg.window(tag=self.tag, on_close=self.on_close):
            with dpg.group(horizontal=True):
                dpg.add_text("EVM: ")
                add_text_to_copy(DONATE_WALLET)

    def on_close(self):
        dpg.delete_item(self.tag)
        dpg.enable_item(self.button)


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
            donate_button = dpg.generate_uuid()
            dpg.add_menu_item(label="Donate!", tag=donate_button,
                              callback=lambda: open_donate_window(donate_button))
