import dearpygui.dearpygui as dpg

from bot.chains import chains
from bot.types_ import NetMode
from bot.settings import settings


def add_chains_tab():
    return ChainsTab()


class ChainsTab:
    def __init__(self):
        self.tag = dpg.add_tab(label="Chains")
        self.table = dpg.add_table(
                parent=self.tag,
                header_row=True, no_host_extendX=True, delay_search=True,
                borders_innerH=True, borders_outerH=True, borders_innerV=True,
                borders_outerV=True, context_menu_in_body=True, row_background=True,
                policy=dpg.mvTable_SizingFixedFit,
                scrollY=True
        )
        self.reload_table()

    def _reload_table(self, net_mode: NetMode):
        dpg.delete_item(self.table, children_only=True)

        dpg.add_table_column(parent=self.table, label="Chain")
        dpg.add_table_column(parent=self.table, label="RPC")
        dpg.add_table_column(parent=self.table, label="Symbol")
        dpg.add_table_column(parent=self.table, label="Explorer")

        for chain_name, chain in chains[net_mode].items():
            with dpg.table_row(parent=self.table):
                dpg.add_text(chain_name)
                dpg.add_text(chain.rpc)
                dpg.add_text(chain.token.symbol)
                dpg.add_text(chain.explorer_url)

    def reload_table(self):
        self._reload_table(settings.net_mode)
