from eth_account.signers.local import LocalAccount

from bot.better_web3 import Contract
from .assets import SENDER_ABI, RECEIVER_ABI


class ZkBridgeCreator(Contract):
    def mint(self, account: LocalAccount, contract_token_id: int, data=""):
        nonce = self.w3.eth.get_transaction_count(account.address)
        prepared_function = self._contract.functions.mint(
            account.address, contract_token_id, bytes(data, 'utf-8'))
        gas = prepared_function.estimate_gas()
        transaction = prepared_function.build_transaction(
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
        """
        approve(address to,uint256 tokenId)
        """
        nonce = self.w3.eth.get_transaction_count(account.address)
        prepared_function = self._contract.functions.approve(address_to, contract_token_id)
        gas = prepared_function.estimate_gas(
            {
                'from': account.address
            }
        )
        transaction = prepared_function.build_transaction(
            {
                'gas': gas,
                'nonce': nonce,
            }
        )
        signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key=account.key)
        send_tx = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(send_tx)
        return tx_receipt


class ZkBridgeSender(Contract):
    def __init__(self, *args, abi=SENDER_ABI, **kwargs):
        super().__init__(*args, abi=abi, **kwargs)

    def transfer(
            self,
            account: LocalAccount,
            contract_address: str,
            contract_token_id: int,
            recipient_app_id: int,
            recipient_address: str,
    ):
        """
        transferNFT(address token,uint256 tokenID,uint16 recipientChain,bytes32 recipient)
        """
        contract_address = self.w3.to_checksum_address(contract_address)
        # Безумие обуяло мой разум, пока я пытался понять, как передать recipient_address
        recipient_address_bytes32 = bytes.fromhex(recipient_address[2:].lower()).rjust(32, b'\0')
        nonce = self.w3.eth.get_transaction_count(account.address)
        prepared_function = self._contract.functions.transferNFT(
            contract_address, contract_token_id, recipient_app_id, recipient_address_bytes32)
        gas = prepared_function.estimate_gas(
            {
                'from': account.address,
                'nonce': nonce,
            }
        )
        transaction = prepared_function.build_transaction(
            {
                'gas': gas,
                'nonce': nonce,
            }
        )
        signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key=account.key)
        send_tx = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(send_tx)
        return tx_receipt


class ZkBridgeReceiver(Contract):
    def __init__(self, *args, abi=RECEIVER_ABI, **kwargs):
        super().__init__(*args, abi=abi, **kwargs)

    def claim(
            self,
            account: LocalAccount,
            source_app_id: int,
            source_deposit_hash: str,
            log_index: int,
            mpt_proof: str,
    ):
        """
        validateTransactionProof(uint16 srcChainId,bytes32 srcBlockHash,uint256 logIndex,bytes mptProof)
        """
        nonce = self.w3.eth.get_transaction_count(account.address)
        prepared_function = self._contract.functions.validateTransactionProof(
            source_app_id, source_deposit_hash, log_index, mpt_proof)
        gas = prepared_function.estimate_gas(
            {
                # 'nonce': nonce,
                'from': account.address,
            }
        )
        transaction = prepared_function.build_transaction(
            {
                'nonce': nonce,
                'gas': gas,
                'gasPrice': self.w3.to_wei(50, 'gwei'),
            }
        )
        signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key=account.key)
        send_tx = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(send_tx)
        return tx_receipt
