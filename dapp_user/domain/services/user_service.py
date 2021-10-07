import json
import boto3
import grpc
from urllib.parse import unquote, urlparse
from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.utils import generate_lambda_response
from dapp_user.config import DELETE_USER_WALLET_ARN, GET_FREE_CALLS_METERING_ARN, \
    GET_SIGNATURE_TO_GET_FREE_CALL_FROM_DAEMON, REGION_NAME
from dapp_user.constant import Status
from dapp_user.domain.factory.user_factory import UserFactory
from dapp_user.infrastructure.repositories.user_repository import UserRepository
from dapp_user.stubs import state_service_pb2, state_service_pb2_grpc
from dapp_user.exceptions import EmailNotVerifiedException
from resources.certificates.root_certificate import certificate

logger = get_logger(__name__)

class UserService:
    def __init__(self):
        self.user_factory = UserFactory()
        self.user_repo = UserRepository()
        self.boto_client = BotoUtils(REGION_NAME)

    def add_or_update_user_preference(self, payload, username):
        user_preference_list = self.user_factory.parse_raw_user_preference_data(payload=payload)
        response = []
        for user_preference in user_preference_list:
            if user_preference.status and user_preference.opt_out_reason is not None:
                raise Exception("Invalid Payload.")
            user_data = self.user_repo.get_user_data_for_given_username(username=username)
            if len(user_data) == 0:
                raise Exception("User is not registered.")
            if user_preference.status is False:
                self.user_repo.disable_preference(
                    user_preference=user_preference, user_row_id=user_data[0]["row_id"])
                response.append(Status.DISABLED.value)
            else:
                self.user_repo.enable_preference(
                    user_preference=user_preference, user_row_id=user_data[0]["row_id"])
                response.append(Status.ENABLED.value)

        return response

    def get_user_preference(self, username):
        user_data = self.user_repo.get_user_data_for_given_username(username=username)
        if len(user_data) == 0:
            raise Exception("User is not registered.")
        user_preference_raw_data = self.user_repo.get_user_preferences(user_row_id=user_data[0]["row_id"])
        preferences = self.user_factory.parse_user_preference_raw_data(user_preference_raw_data)
        return [preference.to_dict() for preference in preferences]

    def delete_user(self, username):
        self.user_repo.delete_user(username)
        self._unlink_wallets_from_user(username)

    def _unlink_wallets_from_user(self, username):
        delete_user_wallet_event = {
            "path": "/wallet/delete",
            "queryStringParameters": {
                "username": username
            },
            "httpMethod": "POST"
        }

        delete_user_wallet_response = self.boto_client.invoke_lambda(
            lambda_function_arn=DELETE_USER_WALLET_ARN,
            invocation_type='RequestResponse',
            payload=json.dumps(delete_user_wallet_event)
        )

        logger.info(f"create_channel_response {delete_user_wallet_response}")
        if delete_user_wallet_response["statusCode"] != 201:
            raise Exception(f"Failed to delete user wallet")

    def _get_no_of_free_calls_from_daemon(self, email, token_to_get_free_call, expiry_date_block, signature,
                                          current_block_number, daemon_endpoint):

        request = state_service_pb2.FreeCallStateRequest()
        request.user_id = email
        request.token_for_free_call = token_to_get_free_call
        request.token_expiry_date_block = expiry_date_block
        request.signature = signature
        request.current_block = current_block_number

        endpoint_object = urlparse(daemon_endpoint)
        if endpoint_object.port is not None:
            channel_endpoint = endpoint_object.hostname + ":" + str(endpoint_object.port)
        else:
            channel_endpoint = endpoint_object.hostname

        if endpoint_object.scheme == "http":
            channel = grpc.insecure_channel(channel_endpoint)
        elif endpoint_object.scheme == "https":
            channel = grpc.secure_channel(channel_endpoint, grpc.ssl_channel_credentials(root_certificates=certificate))
        else:
            raise ValueError('Unsupported scheme in service metadata ("{}")'.format(endpoint_object.scheme))

        stub = state_service_pb2_grpc.FreeCallStateServiceStub(channel)
        response = stub.GetFreeCallsAvailable(request)
        logger.info(
            f"No of free  free call for {email} {daemon_endpoint} {current_block_number} is {response.free_calls_available}")
        return response.free_calls_available

    def get_free_call(self, event):
        # passing event here as metering contract is that it need the entire event object
        # metering will eventually go out  then we will clean this up.
        try:
            payload_dict = event['queryStringParameters']
            email = payload_dict['username']
            lambda_client = boto3.client('lambda')
            org_id = payload_dict['organization_id']
            service_id = payload_dict['service_id']
            group_id = unquote(payload_dict['group_id'])
            response = lambda_client.invoke(FunctionName=GET_SIGNATURE_TO_GET_FREE_CALL_FROM_DAEMON,
                                            InvocationType='RequestResponse',
                                            Payload=json.dumps(
                                                {"queryStringParameters": {"username": email,
                                                                           "org_id": org_id,
                                                                           "service_id": service_id,
                                                                           "group_id": group_id}}
                                            ))

            result = json.loads(response.get('Payload').read())
            signature_response = json.loads(result['body'])

            if signature_response["status"] == "success":
                logger.info(f"Got signature to make free call to daemon for {email} : {signature_response['data']}")
                token_to_get_free_call = signature_response["data"].get("token_to_get_free_call", "")
                expiry_date_block = signature_response["data"].get("expiry_date_block", "")
                signature = signature_response["data"].get("signature", "")
                current_block_number = signature_response["data"].get("current_block_number", "")
                daemon_endpoint = signature_response["data"].get("daemon_endpoint", "")
                free_calls_allowed= signature_response["data"].get("free_calls_allowed",0)
                free_call_available = self._get_no_of_free_calls_from_daemon(email,
                                                                             bytes.fromhex(token_to_get_free_call),
                                                                             expiry_date_block,
                                                                             bytes.fromhex(signature),
                                                                             current_block_number, daemon_endpoint)

                response = {"username": email, "org_id": org_id,
                            "service_id": service_id,
                            "total_calls_made": free_calls_allowed - free_call_available,
                            "free_calls_allowed": free_calls_allowed}

                return generate_lambda_response(200, response, cors_enabled=True)
            else:
                raise Exception("Error while getting signature to make free call to daemon")

        except Exception as e:
            logger.info(f"Failed to get freecall from daemon  {email} {org_id} {service_id} error {str(e)}")
            lambda_client = boto3.client('lambda')
            response = lambda_client.invoke(FunctionName=GET_FREE_CALLS_METERING_ARN, InvocationType='RequestResponse',
                                            Payload=json.dumps(event))
            result = json.loads(response.get('Payload').read())
            return result

    def register_user(self, user_attribute, client_id):
        user = self.user_factory.create_user_domain_model(payload=user_attribute, client_id=client_id)
        if not user.email_verified:
            raise EmailNotVerifiedException()
        return self.user_repo.register_user_data(user)
