from eth_account.signers.local import LocalAccount

from bot.better_web3 import Chain, Contract


class ZkBridgeChain(Chain):
    def __init__(self, zkbridge_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zkbridge_id = zkbridge_id


class ZkBridgeContract(Contract):
    def __init__(self, chain: ZkBridgeChain, *args, **kwargs):
        super().__init__(chain, *args, **kwargs)
        self.chain: ZkBridgeChain

    def mint(self, account: LocalAccount, contract_token_id: int, data=""):
        nonce = self.w3.eth.get_transaction_count(account.address)
        prepared_mint_function = self._contract.functions.mint(account.address, contract_token_id, bytes(data, 'utf-8'))
        gas = prepared_mint_function.estimate_gas()
        transaction = prepared_mint_function.build_transaction(
            {
                'from': account.address,
                'chainId': self.chain.chain_id,
                'gas': gas,
                'nonce': nonce,
            }
        )
        signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key=account.key)
        send_tx = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(send_tx)
        return tx_receipt

    def approve(self, account: LocalAccount, address_to: str, contract_token_id: int):
        nonce = self.w3.eth.get_transaction_count(account.address)
        prepared_approve_function = self._contract.functions.approve(address_to, contract_token_id)
        gas = prepared_approve_function.estimate_gas({
            'from': account.address
        })
        transaction = prepared_approve_function.build_transaction(
            {
                'gas': gas,
                'nonce': nonce,
            }
        )
        signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key=account.key)
        send_tx = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(send_tx)
        return tx_receipt
