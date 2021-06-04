import json
import tempfile
from common.boto_utils import BotoUtils
from common.logger import get_logger
from utility.config import NODEJS_PROTO_LAMBDA_ARN, SUPPORTED_ENVIRONMENT, REGION_NAME, PYTHON_PROTO_LAMBDA_ARN
from utility.application.handlers.proto_stubs_handler import generate_python_stubs

TEMP_FILE_DIR = tempfile.gettempdir()
boto_utils = BotoUtils(region_name=REGION_NAME)
logger = get_logger(__name__)

class GenerateStubService:
    def __init__(self):
        pass

    def manage_proto_compilation(self, proto_s3_url, stub_s3_url):
        try:
            stub_bucket, stub_bucket_key = boto_utils.get_bucket_and_key_from_url(url=stub_s3_url)
            self.clear_old_stub_files(stub_bucket=stub_bucket, stub_bucket_key=stub_bucket_key)
            error_msg = "Error in generating {} stubs for \n proto_url :: {} \n error :: {}"
            error_messages = []
            for environment in SUPPORTED_ENVIRONMENT:
                if environment is 'python':
                    response = self.invoke_python_stubs_lambda(proto_s3_url=proto_s3_url, stub_s3_url=stub_s3_url)
                if environment is 'nodejs':
                    response = self.invoke_node_stubs_lambda(proto_s3_url=proto_s3_url, stub_s3_url=stub_s3_url)
                if response.get("statusCode",{}) != 200:
                    msg = error_msg.format(environment,proto_s3_url,response)
                    logger.info(msg)
                    error_messages.append(msg)
                if error_messages:
                    raise Exception(error_messages)
            return {"message":"success"}
        except Exception as e:
            raise e(f"proto lambda invocation failed {repr(e)}")

    @staticmethod
    def invoke_node_stubs_lambda(stub_s3_url, proto_s3_url):
        payload = json.dumps({
            "stub_s3_url": stub_s3_url,
            "proto_s3_url": proto_s3_url
        })
        response = boto_utils.invoke_lambda(
            invocation_type="RequestResponse",
            payload=payload,
            lambda_function_arn=NODEJS_PROTO_LAMBDA_ARN
        )
        return response

    @staticmethod
    def invoke_python_stubs_lambda(stub_s3_url, proto_s3_url):
        payload = json.dumps({
            "stub_s3_url": stub_s3_url,
            "proto_s3_url": proto_s3_url
        })
        response = boto_utils.invoke_lambda(
            invocation_type="RequestResponse",
            payload=payload,
            lambda_function_arn=PYTHON_PROTO_LAMBDA_ARN
        )
        return response

    @staticmethod
    def clear_old_stub_files(stub_bucket, stub_bucket_key):
        try:
            to_delete_objects = boto_utils.get_objects_from_s3(bucket=stub_bucket, key=stub_bucket_key)
            for delete_obj in to_delete_objects:
                boto_utils.delete_objects_from_s3(bucket=stub_bucket, key=delete_obj["Key"], key_pattern=stub_bucket_key)
        except Exception as e:
            msg = f"Error in deleting stub files :: {repr(e)}"
            logger.info(msg)
            raise Exception(msg)