from better_web3 import Chain

from bot.types_ import NetMode
from bot.config import CHAINS_DATA, config


chains: dict[str: dict[str: Chain]] = dict()


for net_mode, name_to_chain_data in CHAINS_DATA.items():
    data: dict[str: Chain] = dict()
    for chain_name, chain_data in name_to_chain_data.items():
        chain = Chain(
            **chain_data,
            batch_request_size=config.BATCH_REQUEST_SIZE,
            batch_request_delay=config.BATCH_REQUEST_DELAY,
        )
        data.update({chain_name: chain})
    chains.update({net_mode: data})


def get_chain_names(net_mode: NetMode) -> tuple[str]:
    return tuple([str(chain_name) for chain_name in chains[net_mode].keys()])
