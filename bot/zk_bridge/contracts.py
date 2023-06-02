from bot.better_web3 import chains
from .contract import ZkBridgeSender, ZkBridgeReceiver
from .assets import RECEIVERS_DATA, SENDERS_DATA, ADDITIONAL_DATA


receivers: dict[str: dict[str: ZkBridgeReceiver]] = dict()
senders: dict[str: dict[str: ZkBridgeSender]] = dict()


for net_mode, chains_dict in chains.items():
    receiver_data: dict[str: ZkBridgeReceiver] = dict()
    sender_data: dict[str: ZkBridgeSender] = dict()
    for chain_name, chain in chains_dict.items():
        if chain_name not in ADDITIONAL_DATA[net_mode]:
            continue
        short_chain_name = ADDITIONAL_DATA[net_mode][chain_name]["short_name"]
        # ZkBridgeReceiver
        receiver_contract_address = RECEIVERS_DATA[short_chain_name]["address"]
        receiver_contract = ZkBridgeReceiver(receiver_contract_address, chain)
        receiver_data.update({chain_name: receiver_contract})
        # ZkBridgeSender
        sender_contract_address = SENDERS_DATA[short_chain_name]["address"]
        sender_contract = ZkBridgeSender(sender_contract_address, chain)
        sender_data.update({chain_name: sender_contract})
    receivers.update({net_mode: receiver_data})
    senders.update({net_mode: sender_data})
