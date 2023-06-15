import asyncio
import random
from contextlib import contextmanager
from typing import Iterable
from PIL import Image

import aiohttp
from better_web3 import Chain
from eth_account.signers.local import LocalAccount
from eth_typing import HexStr
from web3 import Web3
from better_web3.utils import sign_message
from better_web3.exceptions import ChainException
from web3.contract.contract import ContractFunction
from web3.types import TxReceipt, Wei

from bot.config import config
from bot.input import get_image_filenames, used_images, rewrite_used_images, IMAGES_DIR
from bot.utils import generate_random_image, generate_simple_sentence, random_resize, image_to_bytes
from bot.chains import chains
from bot.zk_bridge import ZkBridgeAPI, ZkBridgeCreator, ADDITIONAL_DATA
from bot.zk_bridge.contracts import receivers, senders, mailers
from bot.zk_bridge.config import MAILERS_DATA
from bot.logger import logger
from bot.types_ import NetMode
from bot.zk_bridge.types_ import TokenStandard
from bot.zk_bridge.models import MintData


def account_info_one_line(index: int, address: str, chain_id: int = None) -> str:
    if chain_id is not None: return f"[{index}] [{address}] (chain_id={chain_id})"
    return f"[{index}] [{address}]"


def _execute_transaction(
        chain: Chain,
        account: LocalAccount,
        fn: ContractFunction,
        *,
        value: Wei = None,
) -> tuple[TxReceipt, HexStr]:
    tx = chain.build_tx(fn, from_=account.address, value=value)
    tx_hash = chain.sign_and_send_tx(account, tx)
    tx_receipt = chain.wait_for_tx_receipt(tx_hash)
    return tx_receipt, tx_hash


@contextmanager
def logged_action(index: int, account_address: str, success_message: str, error_message: str):
    account_info = account_info_one_line(index, account_address)
    try:
        yield
        logger.success(f"{account_info} {success_message}")
    except Exception as e:
        logger.error(f"{account_info} {error_message}: unexpected error.")
        logger.exception(e)
        raise


def execute_logged_transaction(
        chain: Chain,
        account: LocalAccount,
        fn: ContractFunction,
        *,
        value: Wei = None,
        index: int = 1,
        success_message: str = "Successful transaction",
        error_message: str = "Transaction failed",
) -> HexStr:
    account_info = account_info_one_line(index, account.address, chain.chain_id)
    try:
        tx_receipt, tx_hash = _execute_transaction(chain, account, fn, value=value)
        tx_hash_link = chain.explorer.get_link_by_tx_hash(tx_hash)
        tx_fee_wei = tx_receipt.gasUsed * tx_receipt.effectiveGasPrice
        tx_fee = Web3.from_wei(tx_fee_wei, "ether")
        message = (f"{account_info} {success_message}"
                   f"\nFee: {tx_fee} {chain.native_token.symbol}"
                   f"\nHash: {tx_hash_link}")
        if value is not None:
            message += f"\nSent: {Web3.from_wei(value, 'ether')} {chain.native_token.symbol}"
        logger.success(message)
        return tx_hash
    except ChainException as e:
        logger.error(f"{account_info} {error_message}. {e}.")
        raise
    except Exception as e:
        logger.error(f"{account_info} {error_message}: unexpected error.")
        logger.exception(e)
        raise


async def auth(
        index: int,
        zk_bridge: ZkBridgeAPI,
        account: LocalAccount,
):
    with logged_action(index, account.address,
                       "Authorization token obtained",
                       "Failed to obtain authorization token"):
        validation_message = await zk_bridge.get_validation_message(account.address)
        signed_message = sign_message(validation_message, account)
        await zk_bridge.get_and_set_auth_token(account.address, signed_message)


async def mint(
        index: int,
        zk_bridge: ZkBridgeAPI,
        account: LocalAccount,
        net_mode: NetMode,
        chain_name: str,
        standard: TokenStandard,
) -> MintData:
    chain = chains[net_mode][chain_name]
    additional_chain_data = ADDITIONAL_DATA[net_mode][chain_name]

    all_images = get_image_filenames()
    if not all_images:
        logger.warning(f"{account_info_one_line(index, account.address)}"
                       f" The folder with images {IMAGES_DIR} is empty!")

    unused_images = all_images.difference(used_images)
    if not unused_images:
        image = generate_random_image()
        logger.warning(f"{account_info_one_line(index, account.address)}"
                       f" In the image folder {IMAGES_DIR} all images have already been used! Random image generated.")
    else:
        unused_image = unused_images.pop()
        image = Image.open(IMAGES_DIR / unused_image)
        used_images.add(unused_image)
        rewrite_used_images(used_images)
        if unused_images:
            logger.info(f"{account_info_one_line(index, account.address)}"
                        f" Unused images last: {len(unused_images)}")
        else:
            logger.warning(f"{account_info_one_line(index, account.address)}"
                           f" That was the last image! The next images will be generated automatically!")
    if config.RESIZE_PICTURE:
        image = random_resize(image)
    image_bytes = image_to_bytes(image)

    with logged_action(index, account.address,
                       "Image generated and uploaded",
                       "Failed to upload image"):
        image_url = await zk_bridge.upload_image(image_bytes)
    logger.info(f"{account_info_one_line(index, account.address)} Image URL: {image_url}")

    nft_name, nft_description = generate_simple_sentence(), generate_simple_sentence()

    with logged_action(index, account.address,
                       "Mint data obtained",
                       "Failed to get mint data"):
        mint_data = await zk_bridge.get_mint_data(
            image_url, nft_name, nft_description, additional_chain_data["id"], standard)

    creator = ZkBridgeCreator(
        chain, mint_data.contract.contract_address, mint_data.contract.abi)
    mint_fn = creator.mint_function(account.address, mint_data.token.contract_token_id)
    mint_tx_hash = execute_logged_transaction(
        chain, account, mint_fn,
        index=index,
        success_message="NFT minted",
        error_message="Failed to mint NFT",
    )

    # Для того чтобы NFT отображалась на сайте zkBridge нужно послать следующие два запроса:
    with logged_action(index, account.address,
                       "Mint confirmed by zkBridge",
                       "Failed to confirm mint. NFT may not be visible on the zkBridge"):
        await zk_bridge.check_mint(mint_tx_hash, mint_data.token.id)
    with logged_action(index, account.address,
                       "NFT receipt confirmed by zkBridge",
                       "Failed to confirm receipt. NFT may not be visible on the zkBridge"):
        await zk_bridge.check_receipt(
            additional_chain_data["id"], mint_data.contract.contract_address,mint_tx_hash)

    return mint_data


async def bridge(
        index: int,
        zk_bridge: ZkBridgeAPI,
        account: LocalAccount,
        net_mode: NetMode,
        source_chain_name: str,
        target_chain_name: str,
        mint_data: MintData
):
    is_testnet = net_mode == "testnet"

    source_chain = chains[net_mode][source_chain_name]
    target_chain = chains[net_mode][target_chain_name]

    sender = senders[net_mode][source_chain_name]
    receiver = receivers[net_mode][target_chain_name]

    source_additional_chain_data = ADDITIONAL_DATA[net_mode][source_chain_name]
    target_additional_chain_data = ADDITIONAL_DATA[net_mode][target_chain_name]

    creator = ZkBridgeCreator(
        source_chain,
        mint_data.contract.contract_address,
        mint_data.contract.abi,
    )

    approve_fn = creator.approve_function(sender.address, mint_data.token.contract_token_id)
    approve_tx_hash = execute_logged_transaction(
        source_chain, account, approve_fn,
        index=index,
        success_message="NFT transfer approved",
        error_message="Failed to approve NFT transfer",
    )

    transfer_fn = sender.transfer_function(
            mint_data.contract.contract_address,
            mint_data.token.contract_token_id,
            target_additional_chain_data["app_id"],
            account.address,
        )
    transfer_tx_hash = execute_logged_transaction(
        source_chain, account, transfer_fn,
        index=index,
        success_message="NFT transferred",
        error_message="Failed to transfer NFT",
    )

    with logged_action(index, account.address,
                       "Order created",
                       "Failed to create order"):
        await zk_bridge.create_order(
            account.address,
            account.address,
            source_chain.chain_id,
            target_chain.chain_id,
            approve_tx_hash,
            creator.address,
            mint_data.token.contract_token_id,
        )

    with logged_action(index, account.address,
                       "Claim data obtained",
                       "Failed to request claim data"):
        claim_data = await zk_bridge.generate(
            transfer_tx_hash,
            source_additional_chain_data["app_id"],
            is_testnet=is_testnet,
        )

    sleep_time = 60
    logger.info(f"{account_info_one_line(index, account.address)} sleeping ({sleep_time})")
    await asyncio.sleep(sleep_time)

    claim_fn = receiver.claim_function(
            claim_data["chain_id"],
            claim_data["block_hash"],
            claim_data["proof_index"],
            claim_data["proof_blob"],
        )
    execute_logged_transaction(
        target_chain, account, claim_fn,
        index=index,
        success_message="NFT claimed",
        error_message="Failed to claim NFT",
    )


async def send_random_message(
        index: int,
        zk_bridge: ZkBridgeAPI,
        account: LocalAccount,
        net_mode: NetMode,
        source_chain_name: str,
        target_chain_name: str,
):
    source_chain = chains[net_mode][source_chain_name]

    mailer = mailers[net_mode][source_chain_name]

    source_additional_chain_data = ADDITIONAL_DATA[net_mode][source_chain_name]
    target_additional_chain_data = ADDITIONAL_DATA[net_mode][target_chain_name]

    source_mailer_data = MAILERS_DATA[source_additional_chain_data["short_name"]]
    target_mailer_data = MAILERS_DATA[target_additional_chain_data["short_name"]]

    message_text = generate_simple_sentence()

    # Отправка транзакции через execute_transaction не подходит, так как надо указывать значение value

    fn = mailer.send_message(
            target_additional_chain_data["app_id"],
            target_mailer_data["receive_contract_address"],
            target_additional_chain_data["lz_chain_id"],
            target_mailer_data["layer_zero_receive_contract_address"],
            account.address,
            message_text,
        )

    tx_hash = execute_logged_transaction(
        source_chain, account, fn,
        value=source_mailer_data["value"],
        index=index,
        success_message="Sent message",
        error_message="Failed to send message",
    )

    with logged_action(index, account.address,
                       "api/msg requested",
                       "Failed to request api/msg"):
        await zk_bridge.msg(
            message_text,
            send_contract_address=target_mailer_data["send_contract_address"],
            receiver_address=account.address,
            sender_address=account.address,
            receiver_app_id=target_additional_chain_data["app_id"],
            sender_app_id=source_additional_chain_data["app_id"],
            sender_tx_hash=tx_hash,
        )


async def mint_and_bridge(
        accounts: Iterable[LocalAccount],
        net_mode: NetMode,
        source_chain_name: str,
        target_chain_name: str,
        standard: TokenStandard
):
    source_chain = chains[net_mode][source_chain_name]
    account_addresses = [account.address for account in accounts]
    balances = source_chain.get_balances(account_addresses)

    async with aiohttp.ClientSession() as session:
        for i, account in enumerate(accounts, start=1):
            account_balance = Web3.from_wei(balances[account.address], "ether")
            balance_info = (f"{account_info_one_line(i, account.address, source_chain.chain_id)}"
                            f" Balance: {account_balance} {source_chain.native_token.symbol}")
            if account_balance == 0:
                logger.warning(balance_info)
                continue
            zk_bridge = ZkBridgeAPI(session)
            try:
                logger.info(balance_info)
                await auth(i, zk_bridge, account)
                mint_data = await mint(i, zk_bridge, account, net_mode, source_chain_name, standard)
                await bridge(i, zk_bridge, account, net_mode, source_chain_name, target_chain_name, mint_data)
                sleep_time = random.randint(*config.DELAY)
                logger.info(f"Sleeping ({sleep_time}s.)")
                await asyncio.sleep(sleep_time)
            except:
                continue


async def send_messages(
        accounts: Iterable[LocalAccount],
        net_mode: NetMode,
        source_chain_name: str,
        target_chain_name: str
):
    source_chain = chains[net_mode][source_chain_name]
    target_chain = chains[net_mode][target_chain_name]
    account_addresses = [account.address for account in accounts]
    source_chain_balances = source_chain.get_balances(account_addresses)
    target_chain_balances = target_chain.get_balances(account_addresses)

    async with aiohttp.ClientSession() as session:
        for i, account in enumerate(accounts, start=1):
            source_chain_account_balance = Web3.from_wei(source_chain_balances[account.address], "ether")
            target_chain_account_balance = Web3.from_wei(target_chain_balances[account.address], "ether")
            source_chain_balance_info = (f"{account_info_one_line(i, account.address, source_chain.chain_id)}"
                                         f" Balance: {source_chain_account_balance} {source_chain.native_token.symbol}")
            target_chain_balance_info = (f"{account_info_one_line(i, account.address, target_chain.chain_id)}"
                                         f" Balance: {target_chain_account_balance} {target_chain.native_token.symbol}")
            if source_chain_account_balance == 0:
                logger.warning(source_chain_balance_info)
                continue
            if target_chain_account_balance == 0:
                logger.warning(target_chain_balance_info)
                continue
            zk_bridge = ZkBridgeAPI(session)
            try:
                logger.info(source_chain_balance_info)
                logger.info(target_chain_balance_info)
                await auth(i, zk_bridge, account)
                await send_random_message(i, zk_bridge, account, net_mode, source_chain_name, target_chain_name)
                sleep_time = random.randint(*config.DELAY)
                logger.info(f"Sleeping ({sleep_time}s.)")
                await asyncio.sleep(sleep_time)
            except:
                continue
