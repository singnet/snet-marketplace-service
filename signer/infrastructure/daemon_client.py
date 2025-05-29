from urllib.parse import urlparse

import grpc
from signer.stubs import state_service_pb2, state_service_pb2_grpc
from resources.certificates.root_certificate import certificate


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

        return response.free_calls_available

    def get_free_call_token(
        self,
        address: str,
        signature: bytes,
        username: str,
        daemon_endpoint: str,
    ):
        request = state_service_pb2.GetFreeCallTokenRequest(
            address=address,
            signature=signature,
            user_id=username,
        )

        endpoint_channel = self.__make_endpoint_channel(daemon_endpoint)

        stub = state_service_pb2_grpc.FreeCallStateServiceStub(endpoint_channel)
        response = stub.GetFreeCallToken(request)

        return response.free_call_token
