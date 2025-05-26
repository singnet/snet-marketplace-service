from signer.settings import settings
from signer.infrastructure.signers import Signer
from signer.application.schemas import (
    GetFreeCallSignatureRequest,
    GetSignatureForOpenChannelForThirdPartyRequest,
    GetSignatureForRegularCallRequest,
    GetSignatureForStateServiceRequest,
    GetFreeCallTokenRequest,
    GetSignatureForFreeCallFromDaemonRequest
)


class SignerService:
    def __init__(self):
        self.signer = Signer()

    def get_signature_for_free_call(self, username: str, request: GetFreeCallSignatureRequest):
        return self.signer.signature_for_free_call(
            username=username,
            org_id=request.org_id,
            service_id=request.service_id,
            group_id=request.group_id
        )

    def get_signature_for_state_service(self, username: str, request: GetSignatureForStateServiceRequest):
        return self.signer.signature_for_state_service(
            username=username,
            channel_id=request.channel_id
        )

    def get_signature_for_regular_call(self, username: str, request: GetSignatureForRegularCallRequest):
        return self.signer.signature_for_regular_call(
            username=username,
            channel_id=request.channel_id,
            nonce=request.nonce,
            amount=request.amount
        )
    
    def get_signature_for_open_channel_for_third_party(self, request: GetSignatureForOpenChannelForThirdPartyRequest):
        return self.signer.signature_for_open_channel_for_third_party(
            recipient=request.recipient,
            group_id=request.group_id,
            amount_in_cogs=request.amount_in_cogs,
            expiration=request.expiration,
            message_nonce=request.message_nonce,
            sender_private_key=request.signer_key,
            executor_wallet_address=request.executor_wallet_address,
        )

    def get_free_call_token(self, username: str, request: GetFreeCallTokenRequest):
        return self.signer.token_to_make_free_call(
            email=username,
            org_id=request.org_id,
            service_id=request.service_id,
            group_id=request.group_id,
            user_public_key=request.public_key
        )

    def get_freecall_signer_address(self):
        return {
            "free_call_signer_address": settings.signer.KEY
        }
    
    def get_signature_for_free_call_from_daemon(
        self,
        username: str,
        request: GetSignatureForFreeCallFromDaemonRequest
    ):
        return self.signer.token_to_get_free_call(
            email=username,
            org_id=request.org_id,
            service_id=request.service_id,
            group_id=request.group_id,
        )

