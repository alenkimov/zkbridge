import asyncio
import secrets

import aiohttp

from bot.image import get_random_image
from bot.zk_bridge_api.http import (
    upload_image,
    get_networks,
    get_mint_data,
    check_mint,
    check_receipt,
)
from bot.zk_bridge_api import get_auth_token, ZkbridgeContract
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
        chain_from = chains[config.CHAIN_NAME_FROM]
        chain_to = chains[config.CHAIN_NAME_TO]

        async with aiohttp.ClientSession() as session:
            for account in accounts:
                # Получаем токен авторизации
                auth_token = await get_auth_token(session, account)
                # Создаем случайное изображение, грузим его на сервер и получаем ссылку
                image = get_random_image()
                image_url = await upload_image(session, auth_token, image)
                # Генерируем случайное имя и описание
                nft_name, nft_description = (secrets.token_hex(16) for _ in range(2))
                # Запрашиваем информацию для минта NFT
                mint_data = await get_mint_data(
                    session,
                    auth_token,
                    image_url,
                    nft_name,
                    nft_description,
                    chain_from.zkbridge_id,
                    config.TOKEN_STANDARD,
                )
                # Создаем экземпляр контракта zkBridgeCreator согласно полученной информации о минте
                zk_bridge_creator = ZkbridgeContract(
                    chain_from,
                    mint_data.contract.contract_address,
                    mint_data.contract.abi,
                )
                # Минтим NFT согласно полученной информации о минте
                tx = zk_bridge_creator.mint(account, mint_data.token.contract_token_id)
                # Спустя минуту даем zkBridge информацию о нашей NFT
                await asyncio.sleep(60)
                tx_hash = tx.transactionHash.hex()
                await check_mint(session, auth_token, tx_hash, mint_data.token.id)
                await check_receipt(session, auth_token, chain_from.zkbridge_id, account.address, tx_hash)

                print(tx)


if __name__ == '__main__':
    asyncio.run(main())
