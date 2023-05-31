from typing import Union

from datetime import datetime
from typing import Literal, TYPE_CHECKING

from web3 import Web3
from eth_account.messages import encode_defunct
from eth_account.account import LocalAccount
from web3.exceptions import NameNotFound

if TYPE_CHECKING:
    from .chain import Chain
    from .explorer import Explorer

from .types import AddressLike, Address


_w3 = Web3()


def get_block_by_datetime(
    explorer: "Explorer", dt: datetime, closest: Literal["before", "after"] = "before"
):
    return explorer.block.getblocknobytime(
        timestamp=int(dt.timestamp()), closest=closest
    )


def get_datetime_by_block(chain: "Chain", block: int):
    return datetime.fromtimestamp(chain.w3.eth.get_block(block).timestamp)


def sign_message(message: str, account: LocalAccount) -> str:
    message = encode_defunct(text=message)
    signed_message = _w3.eth.account.sign_message(message, private_key=account.key)
    return signed_message.signature.hex()


def _str_to_addr(s: Union[AddressLike, str]) -> Address:
    """Idempotent"""
    if isinstance(s, str):
        if s.startswith("0x"):
            return Address(bytes.fromhex(s[2:]))
        else:
            raise NameNotFound(f"Couldn't convert string '{s}' to AddressLike")
    else:
        return s


def _addr_to_str(a: AddressLike) -> str:
    if isinstance(a, bytes):
        # Address or ChecksumAddress
        addr: str = Web3.to_checksum_address("0x" + bytes(a).hex())
        return addr
    elif isinstance(a, str) and a.startswith("0x"):
        addr = Web3.to_checksum_address(a)
        return addr

    raise NameNotFound(a)


def is_same_address(a1: Union[AddressLike, str], a2: Union[AddressLike, str]) -> bool:
    return _str_to_addr(a1) == _str_to_addr(a2)


def _validate_address(a: AddressLike) -> None:
    assert _addr_to_str(a)
