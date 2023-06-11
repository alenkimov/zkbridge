import asyncio
import secrets
from typing import Iterable

import aiohttp
from better_web3 import Chain
from eth_account.signers.local import LocalAccount
from web3 import Web3
from better_web3.utils import sign_message, estimate_gas
from web3.contract.contract import ContractFunction

from bot.utils import get_random_image
from bot.chains import chains
from bot.zk_bridge import (
    ZkBridgeAPI,
    ZkBridgeCreator,
    receivers,
    senders,
    ADDITIONAL_DATA,
)
from bot.logger import logger
from bot.types_ import NetMode, TokenStandard


def execute_transaction(
        log_message: str,
        chain: Chain,
        fn: ContractFunction,
        account: LocalAccount) -> str:
    tx_gas = estimate_gas(fn, from_=account.address)
    tx = chain.build_tx(fn, gas=tx_gas, from_=account.address)
    tx_hash = chain.sign_and_send_tx(account, tx)
    tx_receipt = chain.wait_for_tx_receipt(tx_hash)
    tx_hash_link = chain.explorer.get_link_by_tx_hash(tx_hash)
    tx_fee_wei = tx_receipt.gasUsed * tx_receipt.effectiveGasPrice
    tx_fee = Web3.from_wei(tx_fee_wei, "ether")
    logger.info(f"{log_message}\nFee: {tx_fee} {chain.native_token.symbol}\nHash: {tx_hash_link}")
    return tx_hash


async def bridge(
        accounts: Iterable[LocalAccount],
        net_mode: NetMode,
        source_chain_name: str,
        target_chain_name: str,
        standard: TokenStandard
):
    is_testnet = net_mode == "testnet"

    source_chain = chains[net_mode][source_chain_name]
    target_chain = chains[net_mode][target_chain_name]

    sender = senders[net_mode][source_chain_name]
    receiver = receivers[net_mode][target_chain_name]

    source_additional_chain_data = ADDITIONAL_DATA[net_mode][source_chain_name]
    target_additional_chain_data = ADDITIONAL_DATA[net_mode][target_chain_name]

    async with aiohttp.ClientSession() as session:
        for i, account in enumerate(accounts, start=1):
            zk_bridge = ZkBridgeAPI(session)

            try:
                validation_message = await zk_bridge.get_validation_message(account.address)
                signed_message = sign_message(validation_message, account)
                await zk_bridge.get_and_set_auth_token(account.address, signed_message)
                logger.info(f"[{i}] [{account.address}] Authorization token obtained")
            except Exception as e:
                logger.error(f"[{i}] [{account.address}] Failed to obtain authorization token")
                logger.exception(e)
                continue

            image = get_random_image()

            try:
                image_url = await zk_bridge.upload_image(image)
                logger.info(f"[{i}] [{account.address}] Image generated and uploaded\nURL: {image_url}")
            except Exception as e:
                logger.error(f"[{i}] [{account.address}] Failed to upload image")
                logger.exception(e)
                continue

            nft_name, nft_description = secrets.token_hex(16), secrets.token_hex(16)

            try:
                mint_data = await zk_bridge.get_mint_data(
                    image_url,
                    nft_name,
                    nft_description,
                    source_additional_chain_data["id"],
                    standard,
                )
                logger.info(f"[{i}] [{account.address}] Mint data obtained")
            except Exception as e:
                logger.error(f"[{i}] [{account.address}] Failed to get mint data")
                logger.exception(e)
                continue

            creator = ZkBridgeCreator(
                source_chain,
                mint_data.contract.contract_address,
                mint_data.contract.abi,
            )

            mint_tx_hash = execute_transaction(
                f"[{i}] [{account.address}] Mint NFT",
                source_chain,
                creator.mint_function(account.address, mint_data.token.contract_token_id),
                account,
            )

            is_minted = await zk_bridge.check_mint(mint_tx_hash, mint_data.token.id)
            logger.info(f"[{i}] [{account.address}] Mint confirmed: {is_minted}")

            is_received = await zk_bridge.check_receipt(
                source_additional_chain_data["id"],
                mint_data.contract.contract_address,
                mint_tx_hash,
            )
            logger.info(f"[{i}] [{account.address}] NFT receipt confirmed: {is_received}")

            approve_tx_hash = execute_transaction(
                f"[{i}] [{account.address}] Approve NFT",
                source_chain,
                creator.approve_function(sender.address, mint_data.token.contract_token_id),
                account,
            )

            transfer_tx_hash = execute_transaction(
                f"[{i}] [{account.address}] Transfer NFT",
                source_chain,
                sender.transfer_function(
                    mint_data.contract.contract_address,
                    mint_data.token.contract_token_id,
                    target_additional_chain_data["app_id"],
                    account.address,
                ),
                account,
            )

            await zk_bridge.create_order(
                account.address,
                account.address,
                source_chain.chain_id,
                target_chain.chain_id,
                approve_tx_hash,
                creator.address,
                mint_data.token.contract_token_id,
            )

            claim_data = await zk_bridge.generate(
                transfer_tx_hash,
                source_additional_chain_data["app_id"],
                is_testnet=is_testnet,
            )

            await asyncio.sleep(60)

            execute_transaction(
                f"[{i}] [{account.address}] Claim NFT",
                target_chain,
                receiver.claim_function(
                    claim_data["chain_id"],
                    claim_data["block_hash"],
                    claim_data["proof_index"],
                    claim_data["proof_blob"],
                ),
                account,
            )
