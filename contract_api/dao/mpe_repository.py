import base64
import datetime as dt

from contract_api.dao.common_repository import CommonRepository
from contract_api.application.schemas.consumer_schemas import MpeEventConsumerRequest


class MPERepository(CommonRepository):

    def __init__(self, connection):
        super().__init__(connection)

    def upsert_channel(self, mpe_data):
        upsert_mpe_channel = "INSERT INTO mpe_channel (channel_id, sender, recipient, groupId, balance_in_cogs, pending, nonce, " \
                             "expiration, signer, row_created, row_updated) " \
                             "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
                             "ON DUPLICATE KEY UPDATE balance_in_cogs = %s, pending = %s, nonce = %s, " \
                             "expiration = %s, row_updated = %s"
        current_datetime = dt.datetime.now(dt.UTC)
        upsert_mpe_channel_params = [mpe_data.channel_id, mpe_data.sender, mpe_data.recipient,
                                     mpe_data.group_id, mpe_data.amount, 0, mpe_data.nonce,
                                     mpe_data.expiration, mpe_data.signer, current_datetime,
                                     current_datetime, mpe_data.amount, 0, mpe_data.nonce, mpe_data.expiration,
                                     current_datetime]
        self.connection.execute(upsert_mpe_channel, upsert_mpe_channel_params)

    def create_channel(self, mpe_data):
        if mpe_data.group_id[0:2] == '0x':
            mpe_data.group_id = mpe_data.group_id[2:]
        mpe_data.group_id = base64.b64encode(mpe_data.group_id)
        self.upsert_channel(mpe_data)

    def update_channel(self, channel_id, group_id, channel_data):
        self.upsert_channel(
            mpe_data=MpeEventConsumerRequest(
                channel_id=channel_id,
                group_id=group_id,
                sender=channel_data[1],
                signer=channel_data[2],
                recipient=channel_data[3],
                nonce=channel_data[0],
                expiration=channel_data[6],
                amount=channel_data[5]
            )
        )


    def get_mpe_channels(self, channel_id):
        select_mp_channel = "SELECT row_id, channel_id, sender, recipient, groupId, balance_in_cogs, pending, nonce, consumed_balance, expiration, signer, row_created, row_updated from mpe_channel where channel_id = %s"
        params = [channel_id]

        query_response = self.connection.execute(select_mp_channel, params)
        return query_response

    def delete_mpe_channel(self, channel_id):
        select_mp_channel = "delete from mpe_channel where channel_id = %s"
        params = [channel_id]

        query_response = self.connection.execute(select_mp_channel, params)
        return query_response

    def update_consumed_balance(self, channel_id, consumed_balance):
        self.connection.execute(
            "UPDATE `mpe_channel` SET consumed_balance = %s WHERE channel_id = %s", [consumed_balance, channel_id]
        )