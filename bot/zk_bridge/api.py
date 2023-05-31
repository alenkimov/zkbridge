from typing import ClassVar

from aiohttp import FormData

from bot.http_client import HTTPClient, RouteCreator
from .models import MintData, ChainData
from .exceptions import ZkBridgeException


class ZkBridgeAPI(HTTPClient):
    Route: ClassVar[RouteCreator] = RouteCreator("https://api.zkbridge.com/api")

    def __init__(self, *args, auth_token: str = None, **kwargs):
        super(ZkBridgeAPI, self).__init__(*args, **kwargs)
        self.auth_token = auth_token

    def __repr__(self):
        return f'<ZkBridgeAPI(auth_token={self.auth_token})>'

    def _get_auth_headers(self) -> dict:
        if self.auth_token is None:
            raise ValueError("Authorization token is not provided.")
        return {"authorization": f"Bearer {self.auth_token}"}

    async def upload_image(self, image: bytes) -> str:
        route = ZkBridgeAPI.Route("POST", "/ipfs")
        data = FormData()
        data.add_field('file', image, filename='image.png', content_type="image/png")
        headers = self._get_auth_headers()

        image_url = await self.request(route, headers=headers, data=data)
        return image_url

    async def get_mint_data(
        self,
        image_url: str,
        name: str,
        description: str,
        network_id: str,
        token_standard: str,
        supply: int = 1,
    ) -> MintData:
        route = ZkBridgeAPI.Route("POST", "/nfts")
        payload = {
            "uri": image_url,
            "name": name,
            "description": description,
            "networkId": network_id,
            "tokenStandard": token_standard,
            "supply": supply,
            "extraData": {}
        }
        headers = self._get_auth_headers()
        data = await self.request(route, json=payload, headers=headers)
        return MintData.from_data(data)

    @staticmethod
    def _handle_status_data(data: dict) -> bool:
        if "status" in data:
            return data["status"] == "ok"
        else:
            raise ZkBridgeException(data["message"])

    async def check_mint(
        self,
        tx_hash: str,
        token_id: str,
        amount: int = 1,
    ) -> bool:
        route = ZkBridgeAPI.Route("POST", "/nfts/mint")
        payload = {
            "txnHash": tx_hash,
            "amount": amount,
            "tokenId": token_id,
        }
        headers = self._get_auth_headers()
        data = await self.request(route, json=payload, headers=headers)
        return self._handle_status_data(data)

    async def check_receipt(
        self,
        network_id: str,
        contract_address: str,
        tx_hash: str
    ) -> bool:
        route = ZkBridgeAPI.Route("POST", "/nfts/receipt")
        payload = {
            "networkId": network_id,
            "contractAddress": contract_address,
            "txHash": tx_hash,
        }
        headers = self._get_auth_headers()
        data = await self.request(route, json=payload, headers=headers)
        return self._handle_status_data(data)

    async def get_networks(self) -> list[ChainData]:
        querystring = {"isDisplayInLaunchpad": "true"}
        route = ZkBridgeAPI.Route("GET", "/networks", **querystring)
        headers = self._get_auth_headers()
        data = await self.request(route, headers=headers)
        chain_data_list = [ChainData.from_chain_data(chain_data) for chain_data in data["data"]]
        return chain_data_list

    async def get_validation_message(self, address: str) -> str:
        route = ZkBridgeAPI.Route("POST", "/signin/validation_message")
        payload = {"publicKey": address}
        data = await self.request(route, json=payload)
        validation_message = data["message"]
        return validation_message

    async def get_auth_token(self, address: str, signed_message: str) -> str:
        route = ZkBridgeAPI.Route("POST", "/signin")
        payload = {
            "publicKey": address,
            "signedMessage": signed_message,
        }
        data = await self.request(route, json=payload)
        auth_token = data["token"]
        return auth_token

    async def get_and_set_auth_token(self, address: str, signed_message: str):
        self.auth_token = await self.get_auth_token(address, signed_message)
