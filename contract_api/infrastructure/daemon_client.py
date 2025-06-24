from urllib.parse import urlparse

import grpc
from contract_api.infrastructure.stubs import state_service_pb2, state_service_pb2_grpc
from resources.certificates.root_certificate import certificate
from common.logger import get_logger


logger = get_logger(__name__)


class DaemonClient:
    @staticmethod
    def __make_endpoint_channel(daemon_endpoint: str):
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

    def get_channel_state(
            self,
            daemon_endpoint: str,
            channel_id: int,
            signature: str,
            current_block_number: int
    ):
        grpc_channel = self.__make_endpoint_channel(daemon_endpoint)
        stub = state_service_pb2_grpc.PaymentChannelStateServiceStub(grpc_channel)

        request = state_service_pb2.ChannelStateRequest(
            channel_id = channel_id.to_bytes(4, "big"),
            signature = bytes.fromhex(signature),
            current_block = current_block_number
        )

        try:
            response = stub.GetChannelState(request)
        except Exception as e:
            logger.error(str(e))
            raise Exception(f"Failed to get channel state with id {channel_id} via grpc")

        return int.from_bytes(response.current_signed_amount, "big")
