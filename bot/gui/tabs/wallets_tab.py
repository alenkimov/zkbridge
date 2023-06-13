import binascii

import dearpygui.dearpygui as dpg
from eth_account import Account

from bot.chains import chains
from bot.input import accounts, rewrite_accounts
from bot.logger import logger
from bot.types_ import NetMode
from bot.settings import settings


def open_input_window(wallets_tab: "WalletsTab"):
    PrivateKeysInputWindow(wallets_tab)


def add_wallets_tab():
    return WalletsTab()


class PrivateKeysInputWindow:
    def __init__(self, wallets_tab: "WalletsTab"):
        self.tag = dpg.generate_uuid()
        self.button = wallets_tab.wallets_button
        self.wallets_tab = wallets_tab
        self.text = ""

        dpg.disable_item(self.button)

        with dpg.window(tag=self.tag, on_close=self.on_close, height=300, width=500, no_resize=True):
            dpg.add_input_text(multiline=True, height=240, width=480, callback=self.rewrite_text)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Confirm", width=75, height=20, callback=self.confirm)

    def rewrite_text(self, _, app_data, user_data):
        self.text = app_data

    def add_accounts(self):
        """Split input text into private keys, create new accounts,
        and add them to the old accounts list"""

        private_keys = set(self.text.split("\n"))
        new_accounts = self._create_new_accounts(private_keys)
        if new_accounts:
            accounts.extend(new_accounts)
            rewrite_accounts(accounts)
            logger.info(f"Loaded {len(new_accounts)} new private keys!")

    @staticmethod
    def _create_new_accounts(private_keys):
        """Create new accounts from private keys not found in old accounts"""
        new_accounts = []
        old_addresses = [account.address for account in accounts]
        for private_key in private_keys:
            try:
                new_account = Account.from_key(private_key)
                if new_account.address not in old_addresses:
                    new_accounts.append(new_account)
            except (UnicodeEncodeError, binascii.Error, ValueError):
                logger.debug(f"(private_key=\"{private_key}\") Failed to load private key: wrong private key")
        return new_accounts

    def on_close(self):
        dpg.delete_item(self.tag)
        dpg.enable_item(self.button)

    def confirm(self):
        self.add_accounts()
        self.wallets_tab.rebuild_table()
        self.on_close()


class WalletsTab:
    def __init__(self):
        self.tag = dpg.generate_uuid()
        self.table_container = dpg.generate_uuid()
        self.wallets_button = dpg.generate_uuid()

        with dpg.tab(tag=self.tag, label="Wallets"):
            dpg.add_button(
                tag=self.wallets_button, label="Add wallets", callback=self.add_wallets)
            dpg.add_group(tag=self.table_container)

        self.rebuild_table()

    def _rebuild_table(self):
        dpg.delete_item(self.table_container, children_only=True)
        with dpg.table(
                parent=self.table_container,
                hideable=True, resizable=True, context_menu_in_body=True,
                reorderable=True, delay_search=True,
                borders_innerH=True, borders_outerH=True, borders_outerV=True,
                scrollY=True, scrollX=True,
        ):
            dpg.add_table_column(label="Private Key")
            dpg.add_table_column(label="Address")
            for account in accounts:
                with dpg.table_row():
                    dpg.add_input_text(
                        default_value=account.key.hex(),
                        width=470,
                        readonly=True,
                    )
                    dpg.add_input_text(
                        default_value=account.address,
                        width=305,
                        readonly=True,
                    )

    def rebuild_table(self):
        self._rebuild_table()

    def add_wallets(self):
        open_input_window(self)
