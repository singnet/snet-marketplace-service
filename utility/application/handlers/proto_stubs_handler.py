from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from utility.application.services.generate_grpc_python_stubs import generate_python_stubs
from utility.application.services.proto_compilation_service import GenerateStubService
from utility.config import SLACK_HOOK, NETWORK_ID
from utility.exceptions import EXCEPTIONS

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def manage_proto_compilation(event, context):
    logger.info(f"Generate proto buffs for service {event}")
    stub_s3_url = event['stub_s3_url']
    proto_s3_url = event['proto_s3_url']
    response = GenerateStubService(). \
        manage_proto_compilation(stub_s3_url=stub_s3_url, proto_s3_url=proto_s3_url)
    return generate_lambda_response(StatusCode.OK, {"status": "success", "data": response, "error": {}},
                                    cors_enabled=True)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def generate_grpc_python_stubs(event, context):
    logger.info(f"Generate python stubs :: {event}")
    stub_s3_url = event['stub_s3_url']
    proto_s3_url = event['proto_s3_url']
    response = generate_python_stubs(stub_s3_url=stub_s3_url, proto_s3_url=proto_s3_url)
    return generate_lambda_response(StatusCode.OK, {"status": "success", "data": response, "error": {}},
                                    cors_enabled=True)
