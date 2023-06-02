import time
import json
import requests
from typing import Callable
import re


class ExplorerError(RuntimeError):
    def __init__(self, message, data) -> None:
        super().__init__(message)

        self.data = data

    def __str__(self) -> str:
        return f"{super().__str__()}.\nReturned result: {self.data}"


class ExplorerAction:
    def __init__(self, module: "ExplorerModule", action: str) -> None:
        self.module = module
        self.action = action

    def __call__(self, **params):
        params["module"] = str(self.module)
        params["action"] = self.action
        if self.module.explorer.api_key is not None:
            params["apikey"] = self.module.explorer.api_key

        if "apikey" not in params:
            # stupid throttling
            time.sleep(5)

        r = requests.get(self.module.explorer.api_url, params=params)
        result = r.json()
        if result["status"] != "1":
            raise ExplorerError(result["message"], result["result"])
        return result["result"]


class ExplorerModule:
    def __init__(self, explorer: "Explorer", module: str) -> None:
        self.explorer = explorer
        self.name = module

    def __str__(self) -> str:
        return self.name

    def __getattr__(self, action: str) -> Callable:
        return ExplorerAction(self, action)


class Explorer:
    def __init__(self, url, api_key=None) -> None:
        self.url = url
        self.api_url = self._convert_url(url)
        self.api_key = api_key

    def __getattr__(self, module: str) -> ExplorerModule:
        return ExplorerModule(self, module)

    def fetch_abi(self, address: str):
        contract_info = self.contract.getsourcecode(address=address)[0]
        abi = json.loads(contract_info["ABI"])
        if contract_info["Proxy"] == "1":
            implementation_info = self.contract.getsourcecode(
                address=contract_info["Implementation"]
            )[0]
            abi = json.loads(implementation_info["ABI"])
        return abi

    @staticmethod
    def _convert_url(url):
        pattern = r"https?://([\w.-]+)/?"
        match = re.match(pattern, url)

        if match:
            domain = match.group(1)
            converted_url = f"https://api.{domain}/api"
            return converted_url
        else:
            raise ValueError("Wrong explorer URL")

    def get_link_by_txn_hash(self, txn_hash: str):
        return f"{self.url}/tx/{txn_hash}"
