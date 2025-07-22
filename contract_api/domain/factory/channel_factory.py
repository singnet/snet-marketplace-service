from typing import Sequence

from contract_api.domain.models.channel import ChannelDomain
from contract_api.infrastructure.models import MpeChannel


class ChannelFactory:

    @staticmethod
    def channel_from_db_model(
            channel_db_model: MpeChannel
    ) -> ChannelDomain:
        return ChannelDomain(
            row_id = channel_db_model.row_id,
            channel_id = channel_db_model.channel_id,
            sender = channel_db_model.sender,
            signer = channel_db_model.signer,
            recipient = channel_db_model.recipient,
            group_id = channel_db_model.group_id,
            balance_in_cogs = channel_db_model.balance_in_cogs,
            nonce = channel_db_model.nonce,
            expiration = channel_db_model.expiration,
            pending = channel_db_model.pending,
            consumed_balance = channel_db_model.consumed_balance,
            created_on = channel_db_model.created_on,
            updated_on = channel_db_model.updated_on
        )

    @staticmethod
    def channels_from_db_model(
            channel_db_model_list: Sequence[MpeChannel]
    ) -> list[ChannelDomain]:
        channel_list = []
        for channel_db in channel_db_model_list:
            channel_list.append(ChannelFactory.channel_from_db_model(channel_db))

        return channel_list
