from common.blockchain_util import BlockChainUtil
from common.constant import ProviderType
from signer.settings import settings
from signer.infrastructure.signers import Signer
from signer.application.schemas import (
    GetFreeCallSignatureRequest,
    GetFreeCallUsageRequest,
    GetSignatureForOpenChannelForThirdPartyRequest,
    GetSignatureForRegularCallRequest,
    GetSignatureForStateServiceRequest,
    # GetSignatureForFreeCallFromDaemonRequest
)
from signer.infrastructure.contract_api_client import ContractAPIClient
from signer.infrastructure.daemon_client import DaemonClient


class SignerService:
    def __init__(self):
        self.signer = Signer()
        self.obj_blockchain_utils = BlockChainUtil(
            provider_type=ProviderType.http.value,
            provider=settings.network.networks[settings.network.id].http_provider,
        )
        self.contract_api_client = ContractAPIClient()
        self.daemon_client = DaemonClient()

    def get_free_call_usage(self, username: str, request: GetFreeCallUsageRequest):
        current_block = self.obj_blockchain_utils.get_current_block_no()

        daemon_endpoint, free_calls_allowed = self.contract_api_client.get_daemon_endpoint_and_free_call_for_group(
            org_id=request.org_id,
            service_id=request.service_id,
            group_id=request.group_id
        )

        if request.free_call_token_hex is None:
            free_call_token = self._obtain_new_free_call_token(request, username, daemon_endpoint, current_block)
        else:
            free_call_token = bytes.fromhex(request.free_call_token_hex)
            free_calls_available = self._get_available_calls(
                request, username, daemon_endpoint, free_call_token, current_block
            )
            if free_calls_available is not None:
                return self._build_free_call_usage_response(
                    free_calls_available,
                    free_calls_allowed,
                    free_call_token.hex()
                )

            # Retry with a new token
            free_call_token = self._obtain_new_free_call_token(request, username, daemon_endpoint, current_block)

        free_calls_available = self._get_available_calls(
            request, username, daemon_endpoint, free_call_token, current_block
        )

        return self._build_free_call_usage_response(free_calls_available, free_calls_allowed, free_call_token)

    def _obtain_new_free_call_token(
        self,
        request: GetFreeCallUsageRequest,
        username: str,
        daemon_endpoint: str,
        current_block: int,
    ):
        signature = self.signer.generate_signature_to_get_free_call_token(
            address=settings.signer.ADDRESS,
            username=username,
            organization_id=request.org_id,
            service_id=request.service_id,
            group_id=request.group_id,
            current_block=current_block
        )

        return self.daemon_client.get_free_call_token(
            address=settings.signer.ADDRESS,
            signature=signature,
            username=username,
            daemon_endpoint=daemon_endpoint
        )

    def _get_available_calls(
        self,
        request: GetFreeCallUsageRequest,
        username: str,
        daemon_endpoint: str,
        free_call_token: bytes,
        current_block: int
    ):
        signature = self.signer.generate_signature_for_free_call(
            address=settings.signer.ADDRESS,
            username=username,
            organization_id=request.org_id,
            service_id=request.service_id,
            group_id=request.group_id,
            current_block=current_block,
            token=free_call_token
        )
        return self.daemon_client.get_free_calls_available(
            address=settings.signer.ADDRESS,
            username=username,
            free_call_token=free_call_token,
            signature=signature,
            current_block_number=current_block,
            daemon_endpoint=daemon_endpoint
        )

    def _build_free_call_usage_response(
        self,
        free_calls_available: int,
        free_calls_allowed: int,
        token: str,
    ):
        return {
            "free_calls_available": free_calls_available,
            "free_calls_made": free_calls_allowed - free_calls_available,
            "free_calls_allowed": free_calls_allowed,
            "free_call_token_hex": token,
        }

    def get_free_call_signature(
        self, username: str, request: GetFreeCallSignatureRequest
    ):
        current_block = self.obj_blockchain_utils.get_current_block_no()

        free_call_token = bytes.fromhex(request.free_call_token_hex)

        expiration_block_number = self.__get_expiration_block_number_from_free_call_token(free_call_token)
        if expiration_block_number <= current_block:
            signature_to_get_free_call_token = self.signer.generate_signature_to_get_free_call_token(
                address=settings.signer.ADDRESS,
                username=username,
                organization_id=request.org_id,
                service_id=request.service_id,
                group_id=request.group_id,
                current_block=expiration_block_number
            )

            daemon_endpoint, _ = self.contract_api_client.get_daemon_endpoint_and_free_call_for_group(
                org_id=request.org_id,
                service_id=request.service_id,
                group_id=request.group_id
            )

            free_call_token = self.daemon_client.get_free_call_token(
                address=settings.signer.ADDRESS,
                signature=signature_to_get_free_call_token,
                username=username,
                daemon_endpoint=daemon_endpoint,
            )

        signature = self.signer.generate_signature_for_free_call(
            address=settings.signer.ADDRESS,
            username=username,
            organization_id=request.org_id,
            service_id=request.service_id,
            group_id=request.group_id,
            current_block=current_block,
            token=free_call_token
        )

        return {
            "user_id": username,
            "address": settings.signer.ADDRESS,
            "block_number": current_block,
            "signature": signature,
            "free_call_token_hex": free_call_token.hex(),
            "expiration_block_number": expiration_block_number
        }

    def __get_expiration_block_number_from_free_call_token(self, token: bytes) -> int:
        try:
            i = token.rfind(b"_")
            if i == -1:
                raise ValueError("invalid token format: no '_' found")

            block_str = token[i+1:].decode("ascii")
            expiration_block_number = int(block_str)

            return expiration_block_number
        except Exception as e:
            raise ValueError(f"invalid token format: {e}")

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

    def get_freecall_signer_address(self):
        return {
            "free_call_signer_address": settings.signer.KEY
        }
    
    # def get_signature_for_free_call_from_daemon(
    #     self,
    #     username: str,
    #     request: GetSignatureForFreeCallFromDaemonRequest
    # ):
    #     return self.__token_to_get_free_call(
    #         username=username,
    #         org_id=request.org_id,
    #         service_id=request.service_id,
    #         group_id=request.group_id,
    #     ).to_response()

