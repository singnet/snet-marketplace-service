from common.constant import StatusCode
from common.logger import get_logger
from common.utils import generate_lambda_response
from utility.application.services.generate_stubs_service import GenerateStubService
from utility.config import SERVICE_ASSETS_BUCKET

logger = get_logger(__name__)


def generate_proto_stubs(event, context):
    logger.info(f"Generate proto buffs for service {event}")
    stub_s3_url = event['stub_s3_url']
    proto_s3_url = event['proto_s3_url']
    response = GenerateStubService(s3_bucket_access_key=SERVICE_ASSETS_BUCKET["access_key"],
                                   s3_bucket_secret_key=SERVICE_ASSETS_BUCKET["secret_key"],
                                   ).\
        generate_service_proto_stubs(stub_s3_url=stub_s3_url, proto_s3_url=proto_s3_url)
    return generate_lambda_response(StatusCode.OK, {"status": "success", "data": response, "error": {}},
                                    cors_enabled=True)
