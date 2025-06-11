from common.blockchain_util import BlockChainUtil
from common.constant import ProviderType
from signer.settings import settings
from signer.infrastructure.signers import Signer
from signer.application.schemas import (
    GetFreeCallSignatureRequest,
    GetSignatureForOpenChannelForThirdPartyRequest,
    GetSignatureForRegularCallRequest,
    GetSignatureForStateServiceRequest,
)
from signer.exceptions import ZeroFreeCallsAvailable
from signer.infrastructure.contract_api_client import ContractAPIClient
from signer.infrastructure.daemon_client import DaemonClient
from signer.infrastructure.repositories.free_call_token_repository import FreeCallTokenInfoRepository


class SignerService:
    def __init__(self):
        self.signer = Signer()
        self.obj_blockchain_utils = BlockChainUtil(
            provider_type=ProviderType.http.value,
            provider=settings.network.networks[settings.network.id].http_provider,
        )
        self.contract_api_client = ContractAPIClient()
        self.daemon_client = DaemonClient()
        self.free_call_token_repository = FreeCallTokenInfoRepository()

    def get_free_call_signature(self, username: str, request: GetFreeCallSignatureRequest):
        current_block = self.obj_blockchain_utils.get_current_block_no()

        free_call_token_info = self.free_call_token_repository.get_free_call_token_info_by_username(
            username=username,
            organization_id=request.organization_id,
            service_id=request.service_id,
            group_id=request.group_id,
        )

        expiration_block_number = (
            free_call_token_info.expiration_block_number if free_call_token_info else None
        )

        if (
            free_call_token_info is None
            or expiration_block_number is None
            or expiration_block_number <= current_block
        ):
            signature_to_get_free_call_token = (
                self.signer.generate_signature_to_get_free_call_token(
                    address=settings.signer.address,
                    username=username,
                    organization_id=request.organization_id,
                    service_id=request.service_id,
                    group_id=request.group_id,
                    current_block=current_block,
                )
            )

            daemon_endpoint, free_calls_count = self.contract_api_client.get_daemon_endpoint_and_free_call_for_group(
                org_id=request.organization_id,
                service_id=request.service_id,
                group_id=request.group_id
            )

            if free_calls_count == 0:
                raise ZeroFreeCallsAvailable()

            new_token, expiration_block_number = self.daemon_client.get_free_call_token(
                address=settings.signer.address,
                signature=signature_to_get_free_call_token,
                current_block=current_block,
                username=username,
                daemon_endpoint=daemon_endpoint,
                token_lifetime_in_blocks=settings.signer.expiration_block_count,
            )

            free_call_token_info = (
                self.free_call_token_repository.insert_or_update_free_call_token_info(
                    username=username,
                    organization_id=request.organization_id,
                    service_id=request.service_id,
                    group_id=request.group_id,
                    expiration_block_number=current_block + settings.signer.expiration_block_count,
                    new_token=new_token,
                )
            )

        signature = self.signer.generate_signature_for_free_call(
            address=settings.signer.address,
            username=username,
            organization_id=request.organization_id,
            service_id=request.service_id,
            group_id=request.group_id,
            current_block=current_block,
            token=free_call_token_info.token,
        )

        return {
            "signer_address": settings.signer.address,
            "signature_hex": bytes.hex(signature),
            "free_call_token_hex": bytes.hex(free_call_token_info.token),
            "expiration_block_number": expiration_block_number,
            "current_block_number": current_block,
        }

    def get_signature_for_state_service(
        self, username: str, request: GetSignatureForStateServiceRequest
    ):
        return self.signer.signature_for_state_service(
            username=username, channel_id=request.channel_id
        )

    def get_signature_for_regular_call(
        self, username: str, request: GetSignatureForRegularCallRequest
    ):
        return self.signer.signature_for_regular_call(
            username=username,
            channel_id=request.channel_id,
            nonce=request.nonce,
            amount=request.amount,
        )

    def get_signature_for_open_channel_for_third_party(
        self, request: GetSignatureForOpenChannelForThirdPartyRequest
    ):
        return self.signer.signature_for_open_channel_for_third_party(
            recipient=request.recipient,
            group_id=request.group_id,
            amount_in_cogs=request.amount_in_cogs,
            expiration=request.expiration,
            message_nonce=request.message_nonce,
            sender_private_key=request.signer_key,
            executor_wallet_address=request.executor_wallet_address,
        )

    def get_freecall_signer_address(self):
        return {"free_call_signer_address": settings.signer.address}
