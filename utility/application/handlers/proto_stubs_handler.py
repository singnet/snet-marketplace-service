from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from utility.application.services.generate_grpc_python_stubs import generate_python_stubs
from utility.application.services.proto_compilation_service import GenerateStubService
from utility.config import SLACK_HOOK, NETWORK_ID
from utility.exceptions import EXCEPTIONS

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def manage_proto_compilation(event, context):
    logger.info(f"Generate proto buffs for service {event}")
    input_s3_path = event["input_s3_path"]
    output_s3_path = event["output_s3_path"]
    org_id = event["org_id"]
    service_id = event["service_id"]
    response = GenerateStubService(). \
        manage_proto_compilation(input_s3_path=input_s3_path, output_s3_path=output_s3_path, org_id=org_id, service_id=service_id)
    logger.debug(f"Manage proto compilation response :: {response}")
    return {"statusCode": StatusCode.OK, "data": response}

@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def generate_grpc_python_stubs(event, context):
    logger.info(f"Generate python stubs :: {event}")
    input_s3_path = event["input_s3_path"]
    output_s3_path = event["output_s3_path"]
    org_id = event["org_id"]
    service_id = event["service_id"]
    response = generate_python_stubs(input_s3_path=input_s3_path, output_s3_path=output_s3_path, org_id=org_id, service_id=service_id)
    logger.debug(f"Generate grpc python stubs response :: {response}")
    return {"statusCode": StatusCode.OK, "data": response}