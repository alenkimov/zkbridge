import webbrowser

import dearpygui.dearpygui as dpg

# blank_button_theme = dpg.theme()  # To make a button look like text
# with dpg.theme_component(dpg.mvButton, parent=blank_button_theme):
#     dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
#     dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0))
#     dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 0))


def add_hyperlink(text, address):
    return dpg.add_button(label=text, callback=lambda: webbrowser.open(address))


def add_text_to_copy(text):
    with dpg.theme() as blank_button_theme:  # To make a button look like text
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 0))

    tag = dpg.generate_uuid()
    dpg.add_button(tag=tag, label=text, callback=dpg.set_clipboard_text(text))
    dpg.bind_item_theme(tag, blank_button_theme)

    with dpg.tooltip(tag):
        dpg.add_text("Click to copy!")
