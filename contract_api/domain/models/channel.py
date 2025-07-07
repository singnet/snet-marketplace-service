from dataclasses import dataclass

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewChannelDomain:
    channel_id: int
    sender: str
    signer: str
    recipient: str
    group_id: str
    balance_in_cogs: int
    nonce: int
    expiration: int


@dataclass
class ChannelDomain(NewChannelDomain, BaseDomain):
    pending: int
    consumed_balance: int

