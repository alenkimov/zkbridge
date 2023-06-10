from better_web3.contract import Contract
from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction

from .assets import SENDER_ABI, RECEIVER_ABI


class ZkBridgeCreator(Contract):
    def mint_function(
            self, address: ChecksumAddress, contract_token_id: int, data=""
    ) -> ContractFunction:
        data = bytes(data, 'utf-8')
        return self.functions.mint(address, contract_token_id, data)

    def approve_function(
            self, address_to: str, contract_token_id: int
    ) -> ContractFunction:
        """
        approve(address to, uint256 tokenId)
        """
        return self.functions.approve(address_to, contract_token_id)


class ZkBridgeSender(Contract):
    def __init__(self, *args, abi=SENDER_ABI, **kwargs):
        super().__init__(*args, abi=abi, **kwargs)

    def transfer_function(
        self,
        contract_address: str,
        contract_token_id: int,
        recipient_app_id: int,
        recipient_address: str,
    ) -> ContractFunction:
        """
        transferNFT(address token,uint256 tokenID,uint16 recipientChain,bytes32 recipient)
        """
        contract_address = self.w3.to_checksum_address(contract_address)
        # Безумие обуяло мой разум, пока я пытался понять, как передать recipient_address
        recipient_address_bytes32 = bytes.fromhex(recipient_address[2:].lower()).rjust(32, b'\0')
        return self.functions.transferNFT(
            contract_address, contract_token_id, recipient_app_id, recipient_address_bytes32)


class ZkBridgeReceiver(Contract):
    def __init__(self, *args, abi=RECEIVER_ABI, **kwargs):
        super().__init__(*args, abi=abi, **kwargs)

    def claim_function(
        self,
        source_app_id: int,
        source_deposit_hash: str,
        log_index: int,
        mpt_proof: str,
    ) -> ContractFunction:
        """
        validateTransactionProof(uint16 srcChainId,bytes32 srcBlockHash,uint256 logIndex,bytes mptProof)
        """
        return self.functions.validateTransactionProof(
            source_app_id, source_deposit_hash, log_index, mpt_proof)
