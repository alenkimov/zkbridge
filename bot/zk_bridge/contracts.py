from .contract import ZkBridgeSender, ZkBridgeReceiver, LzMailer
from .config import RECEIVERS_DATA, SENDERS_DATA, MAILERS_DATA, ADDITIONAL_DATA

from bot.chains import chains

receivers: dict[str: dict[str: ZkBridgeReceiver]] = dict()
senders: dict[str: dict[str: ZkBridgeSender]] = dict()
mailers: dict[str: dict[str: LzMailer]] = dict()


for net_mode, chains_dict in chains.items():
    receivers_: dict[str: ZkBridgeReceiver] = dict()
    senders_: dict[str: ZkBridgeSender] = dict()
    mailers_: dict[str: LzMailer] = dict()
    for chain_name, chain in chains_dict.items():
        if chain_name not in ADDITIONAL_DATA[net_mode]:
            continue
        short_chain_name = ADDITIONAL_DATA[net_mode][chain_name]["short_name"]
        # ZkBridgeReceiver
        if short_chain_name in RECEIVERS_DATA:
            receiver_contract_address = RECEIVERS_DATA[short_chain_name]["address"]
            receiver_contract = ZkBridgeReceiver(chain, receiver_contract_address)
            receivers_.update({chain_name: receiver_contract})
        # ZkBridgeSender
        if short_chain_name in SENDERS_DATA:
            sender_contract_address = SENDERS_DATA[short_chain_name]["address"]
            sender_contract = ZkBridgeSender(chain, sender_contract_address)
            senders_.update({chain_name: sender_contract})
        # LzMailer
        if short_chain_name in MAILERS_DATA:
            mailer_contract_address = MAILERS_DATA[short_chain_name]["send_contract_address"]
            mailer_contract = LzMailer(chain, mailer_contract_address)
            mailers_.update({chain_name: mailer_contract})

    receivers.update({net_mode: receivers_})
    senders.update({net_mode: senders_})
    mailers.update({net_mode: mailers_})
