from typing import TYPE_CHECKING

from eth_utils import is_hex_address, to_checksum_address

if TYPE_CHECKING:
    from .chain import Chain


class Contract:
    def __init__(self, chain: "Chain", address, abi):
        self.address = to_checksum_address(address)
        self.chain = chain
        self.abi = abi
        self.w3 = self.chain.w3
        self._contract = self.chain.w3.eth.contract(self.address, abi=self.abi)

    def __getattr__(self, method_name):
        def fn(*args, block="latest", **kwargs):
            args = [to_checksum_address(a) if is_hex_address(a) else a for a in args]
            kwargs = {
                k: to_checksum_address(v) if is_hex_address(v) else v
                for k, v in kwargs.items()
            }

            return self._contract.functions[method_name](*args, **kwargs).call(
                block_identifier=block
            )

        return fn
