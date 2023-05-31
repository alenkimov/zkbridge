from dataclasses import dataclass

from web3 import Web3
from web3.middleware import geth_poa_middleware

from .contract import Contract
from .explorer import Explorer
from . import utils


@dataclass
class NativeToken:
    symbol: str
    decimals: int = 18


class Chain:
    def __init__(
            self,
            name: str,
            rpc: str,
            chain_id: int,
            explorer: Explorer = None,
            symbol: str = None,
            decimals=18,
            poa_middleware=True,
    ):
        self.name = name
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.explorer = explorer
        self.native_token = NativeToken(symbol, decimals) if symbol else None
        self.chain_id = chain_id
        if poa_middleware:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    def __repr__(self):
        return f"Chain(name={self.name}, rpc={self.w3.provider})"

    def contract(self):
        def _contract(*args, **kwargs):
            return Contract(*args, chain=self, **kwargs)

        return _contract

    def get_datetime_by_block(self):
        def _get_datetime_by_block(block):
            return utils.get_datetime_by_block(self, block)

        return _get_datetime_by_block
