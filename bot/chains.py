import tomllib

from bot.better_web3 import Explorer
from bot.zk_bridge import ZkBridgeChain
from bot.paths import CONFIG_DIR

CHAINS_TOML = CONFIG_DIR / "chains.toml"

with open(CHAINS_TOML, "rb") as chains_toml:
    chains_data = tomllib.load(chains_toml)

testnet: dict[str: ZkBridgeChain] = dict()
mainnet: dict[str: ZkBridgeChain] = dict()

for chain_name, chain_data in chains_data["testnet"].items():
    explorer = Explorer(chain_data["explorer"])
    chain = ZkBridgeChain(
        name=chain_name,
        rpc=chain_data["RPC"],
        chain_id=chain_data["chain_id"],
        symbol=chain_data["currency"],
        explorer=explorer,
        zkbridge_id=chain_data["zkbridge_id"],
    )
    testnet.update({chain_name: chain})

for chain_name, chain_data in chains_data["mainnet"].items():
    explorer = Explorer(chain_data["explorer"])
    chain = ZkBridgeChain(
        name=chain_name,
        rpc=chain_data["RPC"],
        chain_id=chain_data["chain_id"],
        symbol=chain_data["currency"],
        explorer=explorer,
        zkbridge_id=chain_data["zkbridge_id"],
    )
    mainnet.update({chain_name: chain})


__all__ = [
    "mainnet",
    "testnet",
]
