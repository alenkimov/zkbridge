import webbrowser

import dearpygui.dearpygui as dpg


def hyperlink(text, address):
    return dpg.add_button(label=text, callback=lambda: webbrowser.open(address))
