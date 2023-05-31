import aiohttp
from eth_account.signers.local import LocalAccount

from bot.better_web3 import sign_message, Chain, Contract
from .http import get_validation_message
from .http import get_auth_token as _get_auth_token


async def get_auth_token(
        session: aiohttp.ClientSession,
        account: LocalAccount,
) -> str:
    validation_message = await get_validation_message(session, account.address)
    signed_message = sign_message(validation_message, account)
    auth_token = await _get_auth_token(session, account.address, signed_message)
    return auth_token


class ZkbridgeChain(Chain):
    def __init__(self, zkbridge_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zkbridge_id = zkbridge_id


class ZkbridgeContract(Contract):
    def __init__(self, chain: ZkbridgeChain, *args, **kwargs):
        super().__init__(chain, *args, **kwargs)
        self.chain: ZkbridgeChain

    def mint(self, account: LocalAccount, contract_token_id: int, data=""):
        nonce = self.w3.eth.get_transaction_count(account.address)
        prepared_mint_function = self._contract.functions.mint(account.address, contract_token_id, bytes(data, 'utf-8'))
        gas_estimate = prepared_mint_function.estimate_gas()
        call_function = prepared_mint_function.build_transaction(
            {
                'chainId': self.chain.chain_id,
                'gas': gas_estimate,
                'nonce': nonce,
            }
        )
        signed_tx = self.w3.eth.account.sign_transaction(call_function, private_key=account.key)
        send_tx = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(send_tx)
        return tx_receipt

    # async def mint(
    #         self,
    #         session: aiohttp.ClientSession,
    #         account: LocalAccount,
    #         auth_token: str,
    #         *,
    #         contract_token_id: int,
    #         token_id: str,
    #         amount=1,
    #         data="",
    # ):
    #     tx = self._mint(account, contract_token_id, data)
    #     tx_hash = tx.transactionHash.hex()
    #
    #     await check_mint(session, auth_token, tx_hash, token_id, amount=amount)
    #     await check_receipt(session, auth_token, self.chain.zkbridge_id, self.address, tx_hash)
    #     return tx
