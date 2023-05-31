import asyncio
import secrets

import aiohttp

from bot.image import get_random_image
from bot.zk_bridge import ZkBridgeAPI, ZkBridgeContract
from bot.better_web3 import sign_message
from bot.chains import testnet, mainnet
from bot.logger import logger
from bot.config import config
from bot.input import load_accounts


chains = testnet if config.TESTNET else mainnet


async def main():
    accounts = load_accounts()
    if not accounts:
        logger.warning(f"Нет аккаунтов")
    else:
        # Выбранные пользователем сети
        source_chain = chains[config.CHAIN_NAME_FROM]
        target_chain = chains[config.CHAIN_NAME_TO]

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
                    continue

                # Генерируем случайные имя и описание
                nft_name, nft_description = (secrets.token_hex(16) for _ in range(2))
                # Запрашиваем информацию для чеканки NFT
                try:
                    mint_data = await zk_bridge.get_mint_data(
                        image_url,
                        nft_name,
                        nft_description,
                        source_chain.zkbridge_id,
                        config.TOKEN_STANDARD,
                    )
                    logger.info(
                        f"[{i}] [{account.address}]"
                        f" Информация для чеканки получена"
                    )
                except Exception as e:
                    logger.error(f"[{i}] [{account.address}] Не удалось получить информацию для чеканки")
                    continue

                # Создаем экземпляр контракта zkBridgeCreator согласно полученной информации о минте
                zk_bridge_creator = ZkBridgeContract(
                    source_chain,
                    mint_data.contract.contract_address,
                    mint_data.contract.abi,
                )

                # Минтим NFT согласно полученной информации о минте
                mint_tx = zk_bridge_creator.mint(account, mint_data.token.contract_token_id)
                mint_tx_hash = mint_tx.transactionHash.hex()
                logger.info(f"[{i}] [{account.address}] Чеканка NFT. Хеш: {mint_tx_hash}")

                # Предоставляем zkBridge информацию о нашей NFT
                is_minted = await zk_bridge.check_mint(mint_tx_hash, mint_data.token.id)
                logger.info(f"[{i}] [{account.address}] Чеканка подтверждена: {is_minted}")
                is_received = await zk_bridge.check_receipt(
                    source_chain.zkbridge_id, mint_data.contract.contract_address, mint_tx_hash)
                logger.info(f"[{i}] [{account.address}] Получение NFT подтверждено: {is_received}")

                # Аппрувим NFT для передачи
                approve_tx = zk_bridge_creator.approve(
                    account,
                    "0x5EaF12A77af42B745869675EfB0dE153Fd46c42c",  # TODO выяснить, откуда берется это адрес
                    mint_data.token.contract_token_id,
                )
                approve_tx_hash = approve_tx.transactionHash.hex()
                logger.info(f"[{i}] [{account.address}] Approve NFT. Хеш: {approve_tx_hash}")

                # Собираем ордер
                order_data = await zk_bridge.create_order(
                    account.address,
                    account.address,
                    source_chain.chain_id,
                    target_chain.chain_id,
                    approve_tx_hash,
                    zk_bridge_creator.address,
                    mint_data.token.contract_token_id,
                )
                c = 1

if __name__ == '__main__':
    asyncio.run(main())
