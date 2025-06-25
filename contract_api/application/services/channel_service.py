import json

import boto3

from contract_api.application.schemas.channel_schemas import GetGroupChannelsRequest, GetChannelsRequest, \
    UpdateConsumedBalanceRequest
from contract_api.config import SIGNER_SERVICE_ARN, REGION_NAME
from contract_api.domain.models.channel import ChannelDomain
from contract_api.infrastructure.daemon_client import DaemonClient
from contract_api.infrastructure.repositories.channel_repository import ChannelRepository
from contract_api.infrastructure.repositories.service_repository import ServiceRepository


class ChannelService:
    def __init__(self):
        self._channel_repo = ChannelRepository()
        self._daemon_client = DaemonClient()
        self._service_repo = ServiceRepository()

    def get_channels(self, request: GetChannelsRequest):
        wallet_address = request.wallet_address
        channels = self._channel_repo.get_channels(wallet_address)
        channel_data = self._convert_channels_data_to_response(channels)

        return channel_data

    def get_group_channels(self, request: GetGroupChannelsRequest):
        user_address = request.user_address
        org_id = request.org_id
        group_id = request.group_id

        channels = self._channel_repo.get_group_channels(user_address, org_id, group_id)
        channel_data = {
            "user_address": user_address,
            "org_id": org_id,
            "group_id": group_id,
            "channels": [channel.to_response() for channel in channels]
        }

        return channel_data

    def update_consumed_balance(self, request: UpdateConsumedBalanceRequest):
        channel_id = request.channel_id
        org_id = request.org_id
        service_id = request.service_id
        signed_amount = request.signed_amount

        channel = self._channel_repo.get_channel(channel_id)

        if signed_amount is None:
            signed_amount = self._get_channel_state_from_daemon(channel, org_id, service_id)

        self._channel_repo.update_consumed_balance(channel_id, signed_amount)

        return {}

    @staticmethod
    def _convert_channels_data_to_response(channels_data: list):
        channel_details_response = {}
        for channel in channels_data:
            org_name = channel["organization_name"]
            if org_name not in channel_details_response:
                channel_details_response[org_name] = {
                    "org_id": channel["org_id"],
                    "hero_image": channel["org_assets_url"].get("hero_image", ""),
                    "channels": {
                        str(channel["channel_id"]): channel["balance_in_cogs"]
                    }
                }
            else:
                channel_details_response[org_name]["channels"][str(channel["channel_id"])] = channel["balance_in_cogs"]

        return channel_details_response

    def _get_channel_state_from_daemon(self, channel: ChannelDomain, org_id: str, service_id: str):
        channel_id = channel.channel_id
        group_id = channel.group_id

        endpoint = self._service_repo.get_service_endpoint(org_id, service_id, group_id)

        signature, current_block_number = self._get_channel_state_signature(channel_id)
        if signature.startswith("0x"):
            signature = signature[2:]
        signed_amount = self._daemon_client.get_channel_state(endpoint, channel_id, signature, current_block_number)

        return signed_amount

    @staticmethod
    def _get_channel_state_signature(channel_id):
        body = {
            'channel_id': channel_id
        }

        payload = {
            "path": "/signer/state-service",
            "body": json.dumps(body),
            "httpMethod": "POST"
        }

        lambda_client = boto3.client('lambda', region_name = REGION_NAME)
        signature_response = lambda_client.invoke(
            FunctionName = SIGNER_SERVICE_ARN,
            InvocationType = 'RequestResponse',
            Payload = json.dumps(payload)
        )

        signature_response = json.loads(signature_response.get("Payload").read())
        if signature_response["statusCode"] != 200:
            raise Exception(f"Failed to create signature for {body}")
        signature_details = json.loads(signature_response["body"])["data"]
        return signature_details["signature"], signature_details["snet-current-block-number"]
