from pydantic import BaseModel, Field


class NftMetadata(BaseModel):
    description: str
    uri: str
    mint_by: str


class Token(BaseModel):
    id: str
    contract_address: str
    network_id: str
    contract_id: str
    contract_token_id: int
    name: str
    standard: str
    nft_metadata: NftMetadata
    is_check_on_blockchain: bool


class Contract(BaseModel):
    id: str
    name: str
    network_id: str
    standard: str
    contract_address: str
    abi: str


class MintData(BaseModel):
    contract: Contract
    token: Token

    @classmethod
    def from_data(cls, data):
        nft_metadata = NftMetadata(
            description=data["token"]["nftMetaData"]["description"],
            uri=data["token"]["nftMetaData"]["uri"],
            mint_by=data["token"]["nftMetaData"]["mintBy"],

        )
        token = Token(
            id=data["token"]["id"],
            contract_address=data["token"]["contractAddress"],
            network_id=data["token"]["networkId"],
            contract_id=data["token"]["contractId"],
            contract_token_id=data["token"]["contractTokenId"],
            name=data["token"]["name"],
            standard=data["token"]["standard"],
            is_check_on_blockchain=data["token"]["isCheckOnBlockchain"],
            nft_metadata=nft_metadata,
        )
        contract = Contract(
            id=data["contract"]["id"],
            name=data["contract"]["name"],
            network_id=data["contract"]["networkId"],
            standard=data["contract"]["standard"],
            contract_address=data["contract"]["contractAddress"],
            abi=data["contract"]["abi"],
        )
        return cls(token=token, contract=contract)


class NativeCurrency(BaseModel):
    name: str
    symbol: str
    decimals: int


class ChainData(BaseModel):
    native_currency: NativeCurrency

    id: str
    name: str
    chain_id: int
    explorer: str

    @classmethod
    def from_chain_data(cls, data: dict):
        native_currency = NativeCurrency(
            name=data["nativeCurrency"]["name"],
            symbol=data["nativeCurrency"]["symbol"],
            decimals=data["nativeCurrency"]["decimals"],
        )
        chain_data = cls(
            id=data["id"],
            name=data["name"],
            chain_id=data["chainId"],
            explorer=data["blockExplorerURL"],
            native_currency=native_currency,
        )
        return chain_data


class AuthToken(BaseModel):
    expire: str
    token: str


class OrderDataToken(BaseModel):
    name: str = Field(..., alias='tokenName')
    id: int = Field(..., alias='tokenId')
    amount: int = Field(..., alias='tokenAmount')
    description: str
    source_contract_address: str = Field(..., alias='sourceContractAddress')
    target_contract_address: str or None = Field("", alias='targetContractAddress')


class OrderData(BaseModel):
    tokens: list[OrderDataToken]

    id: str
    standard: str
    address_from: str = Field(..., alias='from')
    address_to: str = Field(..., alias='to')

    recipient_chain: int = Field(..., alias='recipientChain')
    source_chain_id: int = Field(..., alias='sourceChainId')
    target_chain_id: int = Field(..., alias='targetChainId')
    source_chain_name: str = Field(..., alias='sourceChainName')
    target_chain_name: str = Field(..., alias='targetChainName')

    deposit_hash: str = Field(..., alias='depositHash')
    claim_hash: str = Field(..., alias='claimHash')
    bridge_status: int = Field(..., alias='bridgeStatus')
    deposit_at: str = Field(..., alias='depositAt')
    claim_confirm_at: str or None = Field("", alias='claimConfirmAt')
