from better_web3.contract import Contract
from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction

from .abi import SENDER_ABI, RECEIVER_ABI, MAILER_ABI


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


class LzMailer(Contract):
    def __init__(self, *args, abi=MAILER_ABI, **kwargs):
        super().__init__(*args, abi=abi, **kwargs)

    def send_message(
            self,
            target_app_id: int,
            receive_contract_address: str,
            receive_layer_zero_chain_id: int,
            layer_zero_receive_contract_address: str,
            recipient_address: str,
            message: str,
            native_fee: int = 0,
    ) -> ContractFunction:
        """
        sendMessage
        ```
        0	dstChainId	 uint16	    3
        1	dstAddress	 address	0xA98163227B85CcC765295Ce5C18E8aAD663De147
        2	lzChainId	 uint16	    102
        3	lzDstAddress address	0x39dad2E89a213626a99Ae09b808b4A79c0d3EC16
        4	nativeFee	 uint256	0
        5	recipient	 address	0xRECIPIENT_ADDRESS
        6	message      string	    Embrace the future of cross-chain interoperability on zkBridge!
        ```
        """
        return self.functions.sendMessage(
            target_app_id, receive_contract_address, receive_layer_zero_chain_id,
            layer_zero_receive_contract_address, native_fee, recipient_address, message)
