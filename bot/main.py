import asyncio
import secrets

import aiohttp

from bot.utils import get_random_image
from bot.better_web3 import chains
from bot.zk_bridge import (
    ZkBridgeAPI,
    ZkBridgeCreator,
    receivers,
    senders,
    ADDITIONAL_DATA,
    TOKEN_STANDARDS,
)
from bot.better_web3 import sign_message
from bot.logger import logger
from bot.config import config
from bot.input import load_accounts


async def main():
    accounts = load_accounts()
    if not accounts:
        logger.warning(f"Нет аккаунтов")
    else:
        net_mode = config.NET_MODE
        is_testnet = True if net_mode == "testnet" else False
        source_chain_name = config.SOURCE_CHAIN_NAME
        target_chain_name = config.TARGET_CHAIN_NAME

        source_chain = chains[net_mode][source_chain_name]
        target_chain = chains[net_mode][target_chain_name]

        sender = senders[net_mode][source_chain_name]
        receiver = receivers[net_mode][target_chain_name]

        source_additional_chain_data = ADDITIONAL_DATA[net_mode][source_chain_name]
        target_additional_chain_data = ADDITIONAL_DATA[net_mode][target_chain_name]

        async with aiohttp.ClientSession() as session:
            for i, account in enumerate(accounts, start=1):
                # Создаем экземпляр ZkBridgeAPI (пока без токена авторизации)
                zk_bridge = ZkBridgeAPI(session)

                # Получаем токен авторизации
                try:
                    validation_message = await zk_bridge.get_validation_message(account.address)
                    signed_message = sign_message(validation_message, account)
                    await zk_bridge.get_and_set_auth_token(account.address, signed_message)
                    logger.info(f"[{i}] [{account.address}] Токен авторизации получен")
                except Exception as e:
                    logger.error(f"[{i}] [{account.address}] Не удалось получить токен авторизации")
                    logger.exception(e)
                    continue

                # Генерируем случайное изображение
                image = get_random_image()
                # Грузим изображение на сервер и получаем ссылку
                try:
                    image_url = await zk_bridge.upload_image(image)
                    logger.info(
                        f"[{i}] [{account.address}]"
                        f" Изображение сгенерировано и загружено на сервер: {image_url}"
                    )
                except Exception as e:
                    logger.error(f"[{i}] [{account.address}] Не удалось загрузить изображение на сервер")
                    logger.exception(e)
                    continue

                # Генерируем случайные имя и описание
                nft_name, nft_description = (secrets.token_hex(16) for _ in range(2))
                # Запрашиваем информацию для чеканки NFT
                try:
                    mint_data = await zk_bridge.get_mint_data(
                        image_url,
                        nft_name,
                        nft_description,
                        source_additional_chain_data["id"],
                        config.TOKEN_STANDARD,
                    )
                    logger.info(
                        f"[{i}] [{account.address}]"
                        f" Информация для чеканки получена"
                    )
                except Exception as e:
                    logger.error(f"[{i}] [{account.address}] Не удалось получить информацию для чеканки")
                    logger.exception(e)
                    continue

                # Создаем экземпляр контракта zkBridgeCreator согласно полученной информации о минте
                creator = ZkBridgeCreator(
                    mint_data.contract.contract_address,
                    source_chain,
                    abi=mint_data.contract.abi,
                )

                # Минтим NFT согласно полученной информации о минте
                mint_tx = creator.mint(account, mint_data.token.contract_token_id)
                mint_tx_hash = mint_tx.transactionHash.hex()
                mint_txn_hash_link = creator.chain.explorer.get_link_by_txn_hash(mint_tx_hash)
                logger.info(f"[{i}] [{account.address}] Чеканка NFT. Газ: {mint_tx.gasUsed} Хеш: {mint_txn_hash_link}")

                # Предоставляем zkBridge информацию о нашей NFT
                is_minted = await zk_bridge.check_mint(mint_tx_hash, mint_data.token.id)
                logger.info(f"[{i}] [{account.address}] Чеканка подтверждена: {is_minted}")
                is_received = await zk_bridge.check_receipt(
                    source_additional_chain_data["id"],
                    mint_data.contract.contract_address,
                    mint_tx_hash,
                )
                logger.info(f"[{i}] [{account.address}] Получение NFT подтверждено: {is_received}")

                # Аппрувим NFT для передачи
                approve_tx = creator.approve(
                    account,
                    # source_bridge_data.address,
                    sender.address,
                    mint_data.token.contract_token_id,
                )
                approve_tx_hash = approve_tx.transactionHash.hex()
                approve_txn_hash_link = creator.chain.explorer.get_link_by_txn_hash(approve_tx_hash)
                logger.info(f"[{i}] [{account.address}] Approve NFT. Газ: {approve_tx.gasUsed} Хеш: {approve_txn_hash_link}")

                # Передача NFT
                transfer_tx = sender.transfer(
                    account,
                    mint_data.contract.contract_address,
                    mint_data.token.contract_token_id,
                    target_additional_chain_data["app_id"],
                    account.address,
                )
                transfer_tx_hash = transfer_tx.transactionHash.hex()
                transfer_txn_hash_link = sender.chain.explorer.get_link_by_txn_hash(transfer_tx_hash)
                logger.info(f"[{i}] [{account.address}] Трансфер NFT. Газ: {transfer_tx.gasUsed} Хеш: {transfer_txn_hash_link}")

                # Собираем ордер
                order_data = await zk_bridge.create_order(
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

                await asyncio.sleep(120)

                # Клейм
                claim_tx = receiver.claim(
                    account,
                    # source_additional_chain_data["app_id"],
                    claim_data["chain_id"],
                    claim_data["block_hash"],
                    claim_data["proof_index"],
                    claim_data["proof_blob"],
                )
                claim_tx_hash = claim_tx.transactionHash.hex()
                claim_txn_hash_link = receiver.chain.explorer.get_link_by_txn_hash(claim_tx_hash)
                logger.info(
                    f"[{i}] [{account.address}] Клейм NFT. Газ: {claim_tx.gasUsed} Хеш: {claim_txn_hash_link}")

                c = 1

if __name__ == '__main__':
    asyncio.run(main())
