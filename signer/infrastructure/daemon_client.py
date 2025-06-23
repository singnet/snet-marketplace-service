from urllib.parse import urlparse

import grpc
from common.logger import get_logger
from resources.certificates.root_certificate import certificate
from signer.stubs import state_service_pb2, state_service_pb2_grpc

logger = get_logger(__name__)


class GetFreeCallTokenError(Exception):
    """Raised when the get free call token request to daemon fails."""

    def __init__(self):
        message = "Error in making get free call token request to daemon"
        super().__init__(message)


class DaemonClient:
    def __make_endpoint_channel(self, daemon_endpoint: str):
        endpoint_object = urlparse(daemon_endpoint)
        if endpoint_object.hostname is None:
            raise ValueError("Invalid daemon endpoint: {}".format(daemon_endpoint))

        if endpoint_object.port is not None:
            channel_endpoint = endpoint_object.hostname + ":" + str(endpoint_object.port)
        else:
            channel_endpoint = endpoint_object.hostname

        if endpoint_object.scheme == "http":
            return grpc.insecure_channel(channel_endpoint)
        elif endpoint_object.scheme == "https":
            return grpc.secure_channel(
                channel_endpoint, grpc.ssl_channel_credentials(root_certificates=certificate)
            )
        else:
            raise ValueError(
                "Unsupported scheme in service metadata ('{}')".format(endpoint_object.scheme)
            )

    def get_free_calls_available(
        self,
        address: str,
        username: str,
        free_call_token: bytes,
        signature: bytes,
        current_block_number: int,
        daemon_endpoint: str,
    ):
        request = state_service_pb2.FreeCallStateRequest(
            address=address,
            user_id=username,
            free_call_token=free_call_token,
            signature=signature,
            current_block=current_block_number,
        )

        endpoint_channel = self.__make_endpoint_channel(daemon_endpoint)

        stub = state_service_pb2_grpc.FreeCallStateServiceStub(endpoint_channel)
        response = stub.GetFreeCallsAvailable(request)

        logger.debug("Daemon get free calls available response: ", str(response))

        return response.free_calls_available

    def get_free_call_token(
        self,
        address: str,
        signature: bytes,
        current_block: int,
        username: str,
        daemon_endpoint: str,
        token_lifetime_in_blocks: int,
    ):
        try:
            request = state_service_pb2.GetFreeCallTokenRequest(
                address=address,
                signature=signature,
                current_block=current_block,
                user_id=username,
                token_lifetime_in_blocks=token_lifetime_in_blocks,
            )

            endpoint_channel = self.__make_endpoint_channel(daemon_endpoint)

            stub = state_service_pb2_grpc.FreeCallStateServiceStub(endpoint_channel)
            response = stub.GetFreeCallToken(request)

            return response.token, response.token_expiration_block
        except grpc.RpcError as e:
            logger.error(
                "Failed to get free call token from daemon. "
                "Error: %s | address=%s | signature=%s | current_block=%d | username=%s | daemon_endpoint=%s | token_lifetime_in_blocks=%d",
                str(e),
                address,
                signature.hex() if isinstance(signature, bytes) else str(signature),
                current_block,
                username,
                daemon_endpoint,
                token_lifetime_in_blocks,
            )
            raise GetFreeCallTokenError()
