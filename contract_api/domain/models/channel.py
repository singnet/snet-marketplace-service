from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChannelDomain:
    row_id: int
    channel_id: int
    sender: str
    signer: str
    recipient: str
    group_id: str
    balance_in_cogs: int
    nonce: int
    expiration: int
    pending: int
    consumed_balance: int
    created_on: datetime
    updated_on: datetime

    def to_response(self) -> dict:
        return {
            "channel_id": self.channel_id,
            "sender": self.sender,
            "signer": self.signer,
            "recipient": self.recipient,
            "group_id": self.group_id,
            "balance_in_cogs": self.balance_in_cogs,
            "nonce": self.nonce,
            "expiration": self.expiration,
            "pending": self.pending,
            "consumed_balance": self.consumed_balance,
        }