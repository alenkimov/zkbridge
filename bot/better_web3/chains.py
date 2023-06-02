from .assets import CHAINS_DATA
from .explorer import Explorer
from .chain import Chain


chains: dict[str: dict[str: Chain]] = dict()


for net_mode, chain_full_data in CHAINS_DATA.items():
    data: dict[str: Chain] = dict()
    for chain_name, chain_data in chain_full_data.items():
        explorer = Explorer(chain_data["explorer"])
        chain = Chain(
            name=chain_name,
            rpc=chain_data["RPC"],
            chain_id=chain_data["chain_id"],
            symbol=chain_data["currency"],
            explorer=explorer,
        )
        data.update({chain_name: chain})
    chains.update({net_mode: data})
