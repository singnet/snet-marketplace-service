from common.blockchain_util import BlockChainUtil
from common.constant import ProviderType, TokenSymbol
from common.request_context import RequestContext
from signer.application.schemas import (
    GetFreeCallSignatureRequest,
    GetSignatureForOpenChannelForThirdPartyRequest,
    GetSignatureForRegularCallRequest,
    GetSignatureForStateServiceRequest,
)
from signer.exceptions import DaemonUnavailable, ZeroFreeCallsAvailable
from signer.infrastructure.contract_api_client import ContractAPIClient
from signer.infrastructure.daemon_client import DaemonClient, GetFreeCallTokenError
from signer.infrastructure.repositories.free_call_token_repository import (
    FreeCallTokenInfoRepository,
)
from signer.infrastructure.signers import Signer
from signer.settings import settings


class SignerService:
    def __init__(self):
        self.obj_blockchain_utils = BlockChainUtil(
            provider_type=ProviderType.http.value,
            provider=settings.network.networks[settings.network.id].http_provider,
        )
        self.contract_api_client = ContractAPIClient()
        self.daemon_client = DaemonClient()
        self.free_call_token_repository = FreeCallTokenInfoRepository()

    def __get_token_from_origin(self, origin: str) -> TokenSymbol:
        if "agix" in origin:
            return TokenSymbol.AGIX
        return TokenSymbol.FET

    def get_free_call_signature(
        self, req_ctx: RequestContext, request: GetFreeCallSignatureRequest
    ):
        token_name = self.__get_token_from_origin(req_ctx.origin)
        signer = Signer(token_name)

        current_block = self.obj_blockchain_utils.get_current_block_no()

        free_call_token_info = self.free_call_token_repository.get_free_call_token_info_by_username(
            username=req_ctx.username,
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
            signature_to_get_free_call_token = signer.generate_signature_to_get_free_call_token(
                address=settings.signer.address,
                username=req_ctx.username,
                organization_id=request.organization_id,
                service_id=request.service_id,
                group_id=request.group_id,
                current_block=current_block,
            )

            daemon_endpoint, free_calls_count = (
                self.contract_api_client.get_daemon_endpoint_and_free_call_for_group(
                    org_id=request.organization_id,
                    service_id=request.service_id,
                    group_id=request.group_id,
                )
            )

            if free_calls_count == 0:
                raise ZeroFreeCallsAvailable()

            try:
                new_token, expiration_block_number = self.daemon_client.get_free_call_token(
                    address=settings.signer.address,
                    signature=signature_to_get_free_call_token,
                    current_block=current_block,
                    username=req_ctx.username,
                    daemon_endpoint=daemon_endpoint,
                    token_lifetime_in_blocks=settings.signer.expiration_block_count,
                )
            except GetFreeCallTokenError:
                raise DaemonUnavailable()

            free_call_token_info = (
                self.free_call_token_repository.insert_or_update_free_call_token_info(
                    username=req_ctx.username,
                    organization_id=request.organization_id,
                    service_id=request.service_id,
                    group_id=request.group_id,
                    expiration_block_number=current_block + settings.signer.expiration_block_count,
                    new_token=new_token,
                )
            )

        signature = signer.generate_signature_for_free_call(
            address=settings.signer.address,
            username=req_ctx.username,
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
        self, req_ctx: RequestContext, request: GetSignatureForStateServiceRequest
    ):
        token_name = self.__get_token_from_origin(req_ctx.origin)
        signer = Signer(token_name)

        return signer.signature_for_state_service(
            username=req_ctx.username, channel_id=request.channel_id
        )

    def get_signature_for_regular_call(
        self, req_ctx: RequestContext, request: GetSignatureForRegularCallRequest
    ):
        token_name = self.__get_token_from_origin(req_ctx.origin)
        signer = Signer(token_name)

        return signer.signature_for_regular_call(
            username=req_ctx.username,
            channel_id=request.channel_id,
            nonce=request.nonce,
            amount=request.amount,
        )

    def get_signature_for_open_channel_for_third_party(
        self, req_ctx: RequestContext, request: GetSignatureForOpenChannelForThirdPartyRequest
    ):
        token_name = self.__get_token_from_origin(origin=req_ctx.origin)
        signer = Signer(token_name)

        return signer.signature_for_open_channel_for_third_party(
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
