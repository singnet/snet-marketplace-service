from typing import Optional

from sqlalchemy import select, update, delete

from contract_api.domain.factory.channel_factory import ChannelFactory
from contract_api.domain.models.channel import ChannelDomain, NewChannelDomain
from contract_api.infrastructure.models import MpeChannel, OrgGroup, Organization
from contract_api.infrastructure.repositories.base_repository import BaseRepository


class ChannelRepository(BaseRepository):
    def get_channels(self, wallet_address: str) -> list[dict]:
        query = select(
            MpeChannel.channel_id,
            MpeChannel.balance_in_cogs,
            Organization.org_id,
            Organization.organization_name,
            Organization.org_assets_url
        ).join(
            OrgGroup, MpeChannel.group_id == OrgGroup.group_id
        ).join(
            Organization, OrgGroup.org_id == Organization.org_id
        ).where(
            MpeChannel.sender == wallet_address
        )

        result = self.session.execute(query)
        result_list = list(result.mappings().all())
        return result_list

    def get_group_channels(self, user_address: str, org_id: str, group_id: str) -> list[ChannelDomain]:
        query = select(
            MpeChannel
        ).join(
            OrgGroup, MpeChannel.group_id == OrgGroup.group_id
        ).where(
            OrgGroup.org_id == org_id,
            OrgGroup.group_id == group_id,
            MpeChannel.sender == user_address,
            MpeChannel.recipient == OrgGroup.payment["payment_address"]
        )

        result = self.session.execute(query)
        channels_db = result.scalars().all()

        return ChannelFactory.channels_from_db_model(channels_db)

    def get_channel(self, channel_id: int) -> Optional[ChannelDomain]:
        query = select(
            MpeChannel
        ).where(
            MpeChannel.channel_id == channel_id
        ).limit(1)

        result = self.session.execute(query)
        channel_db = result.scalar_one_or_none()

        if channel_db is None:
            return None

        return ChannelFactory.channel_from_db_model(channel_db)

    @BaseRepository.write_ops
    def update_consumed_balance(self, channel_id: int, consumed_balance: int) -> None:
        query = update(
            MpeChannel
        ).where(
            MpeChannel.channel_id == channel_id
        ).values(
            consumed_balance=consumed_balance
        )

        self.session.execute(query)
        self.session.commit()

    @BaseRepository.write_ops
    def upsert_channel(self, channel: NewChannelDomain) -> None:
        query = select(
            MpeChannel
        ).where(
            MpeChannel.channel_id == channel.channel_id
        ).limit(1)

        result = self.session.execute(query)
        channel_db = result.scalar_one_or_none()

        if channel_db is not None:
            query = update(
                MpeChannel
            ).where(
                MpeChannel.channel_id == channel.channel_id
            ).values(
                balance_in_cogs=channel.balance_in_cogs,
                pending=0,
                nonce=channel.nonce,
                expiration=channel.expiration
            )
            self.session.execute(query)
        else:
            self.session.add(
                MpeChannel(
                    channel_id=channel.channel_id,
                    sender=channel.sender,
                    signer = channel.signer,
                    recipient=channel.recipient,
                    group_id=channel.group_id,
                    balance_in_cogs=channel.balance_in_cogs,
                    pending=0,
                    nonce=channel.nonce,
                    expiration=channel.expiration
                )
            )

        self.session.commit()

    def delete_channel(self, channel_id: int) -> None:
        query = delete(
            MpeChannel
        ).where(
            MpeChannel.channel_id == channel_id
        )

        self.session.execute(query)
        self.session.commit()
