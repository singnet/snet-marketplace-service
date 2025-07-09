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

    def to_response(self):
        result = super().to_response()
        for key in ["balance_in_cogs", "pending", "consumed_balance"]:
            result[key] = int(result[key])
        return result


