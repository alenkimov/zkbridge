import dearpygui.dearpygui as dpg
from eth_account import Account
from eth_account.signers.local import LocalAccount

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
        self.tag = dpg.add_window()
        self.wallets_tab = wallets_tab
        self.text = ""

        dpg.disable_item(self.wallets_tab.add_wallets_btn)

        dpg.add_input_text(parent=self.tag, label="Private keys", multiline=True, height=300, tab_input=True,
                           callback=self.rewrite_text)
        with dpg.group(parent=self.tag, horizontal=True):
            dpg.add_button(label="Cancel", width=75, callback=self.cancel)
            dpg.add_button(label="Ok", width=75, callback=self.ok)

    def rewrite_text(self, _, app_data, user_data):
        self.text = app_data

    def add_accounts(self):
        private_keys = self.text.split("\n")
        old_addresses = [account.address for account in accounts]
        new_accounts: list[LocalAccount] = []
        for private_key in private_keys:
            try:
                new_account: LocalAccount = Account.from_key(private_key)
                if new_account.address not in old_addresses:
                    new_accounts.append(new_account)
            except:
                pass
        if new_accounts:
            logger.info(f"Loaded {len(new_accounts)} new private keys!")
            accounts.extend(new_accounts)
            rewrite_accounts(accounts)

    def cancel(self):
        dpg.delete_item(self.tag)
        dpg.enable_item(self.wallets_tab.add_wallets_btn)

    def ok(self):
        self.add_accounts()
        self.wallets_tab.reload_table()
        self.cancel()


class WalletsTab:
    def __init__(self):
        self.tag = dpg.add_tab(label="Wallets")

        self.add_wallets_btn = dpg.add_button(
            parent=self.tag, label="Add wallets", callback=self.add_wallets)

        self.table = dpg.add_table(
            parent=self.tag,
            header_row=True, no_host_extendX=True, delay_search=True,
            borders_innerH=True, borders_outerH=True, borders_innerV=True,
            borders_outerV=True, context_menu_in_body=True, row_background=True,
            policy=dpg.mvTable_SizingFixedFit,
            scrollY=True, resizable=True
        )
        self.reload_table()

    def _reload_table(self, net_mode: NetMode):
        dpg.delete_item(self.table, children_only=True)
        dpg.add_table_column(parent=self.table, label="Private Key")
        dpg.add_table_column(parent=self.table, label="Address")
        for chain_name, chain in chains[net_mode].items():
            dpg.add_table_column(parent=self.table, label=f"{chain_name}, {chain.native_token.symbol}")
        for account in accounts:
            with dpg.table_row(parent=self.table):
                dpg.add_text(account.key.hex())
                dpg.add_text(account.address)

    def reload_table(self):
        self._reload_table(settings.net_mode)

    def add_wallets(self):
        open_input_window(self)
