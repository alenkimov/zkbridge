import aiohttp
from aiohttp import FormData

from .models import MintData, ChainData
from .exceptions import ZkBridgeException


BASE_URL = "https://api.zkbridge.com/api"


async def upload_image(
        session: aiohttp.ClientSession,
        auth_token: str,
        image: bytes
) -> str:
    url = BASE_URL + "/ipfs"
    data = FormData()
    data.add_field('file', image, filename='image.png', content_type="image/png")
    headers = {"authorization": f"Bearer {auth_token}"}

    response = await session.post(url, headers=headers, data=data)
    image_url = await response.text()
    return image_url


async def get_mint_data(
        session: aiohttp.ClientSession,
        auth_token: str,
        image_url: str,
        name: str,
        description: str,
        network_id: str,
        token_standard: str,
        supply: int = 1,
) -> MintData:
    url = BASE_URL + "/nfts"

    payload = {
        "uri": image_url,
        "name": name,
        "description": description,
        "networkId": network_id,
        "tokenStandard": token_standard,
        "supply": supply,
        "extraData": {}
    }
    headers = {"authorization": f"Bearer {auth_token}"}

    response = await session.post(url, json=payload, headers=headers)
    data = await response.json()
    return MintData.from_data(data)


async def check_mint(
        session: aiohttp.ClientSession,
        auth_token: str,
        tx_hash: str,
        token_id: str,
        amount: int = 1,
) -> bool:
    url = BASE_URL + "/nfts/mint"
    payload = {
        "txnHash": tx_hash,
        "amount": amount,
        "tokenId": token_id,
    }
    headers = {"authorization": f"Bearer {auth_token}"}
    response = await session.post(url, json=payload, headers=headers)
    data = await response.json()
    if "status" in data:
        return data["status"] == "ok"
    else:
        raise ZkBridgeException(data["message"])


async def check_receipt(
        session: aiohttp.ClientSession,
        auth_token: str,
        network_id: str,
        contract_address: str,
        tx_hash: str
) -> bool:
    url = "https://api.zkbridge.com/api/nfts/receipt"

    payload = {
        "networkId": network_id,
        "contractAddress": contract_address,
        "txHash": tx_hash,
    }
    headers = {"authorization": f"Bearer {auth_token}"}
    response = await session.post(url, json=payload, headers=headers)
    data = await response.json()
    return data["status"] == "ok"


async def get_networks(
        session: aiohttp.ClientSession,
        auth_token: str,
) -> list[ChainData]:
    url = BASE_URL + "/networks"
    querystring = {"isDisplayInLaunchpad": "true"}
    headers = {"authorization": f"Bearer {auth_token}"}
    response = await session.get(url, headers=headers, params=querystring)
    data = await response.json()
    chain_data_list = [ChainData.from_chain_data(chain_data) for chain_data in data["data"]]
    return chain_data_list


async def get_validation_message(
        session: aiohttp.ClientSession,
        address: str,
) -> str:
    url = BASE_URL + "/signin/validation_message"

    payload = {"publicKey": address}
    response = await session.post(url, json=payload)
    data = await response.json()
    validation_message = data["message"]
    return validation_message


async def get_auth_token(
        session: aiohttp.ClientSession,
        address: str,
        signed_message: str,
) -> str:
    url = "https://api.zkbridge.com/api/signin"

    payload = {
        "publicKey": address,
        "signedMessage": signed_message,
    }
    response = await session.post(url, json=payload)
    data = await response.json()
    auth_token = data["token"]
    return auth_token
