from better_web3 import Chain, Explorer, NativeToken, GasStation

from bot.types_ import NetMode
from bot.config import CHAINS_DATA


chains: dict[str: dict[str: Chain]] = dict()


for net_mode, name_to_chain_data in CHAINS_DATA.items():
    data: dict[str: Chain] = dict()
    for chain_name, chain_data in name_to_chain_data.items():
        chain = Chain(rpc=chain_data["rpc"])
        if "explorer" in chain_data:
            chain.explorer = Explorer(**chain_data["explorer"])
        if "native_token" in chain_data:
            chain.native_token = NativeToken(**chain_data["native_token"])
        if "gas_station_url" in chain_data:
            chain.gas_station = GasStation(chain_data["gas_station_url"])
        data.update({chain_name: chain})
    chains.update({net_mode: data})


def get_chain_names(net_mode: NetMode) -> tuple[str]:
    return tuple([str(chain_name) for chain_name in chains[net_mode].keys()])
