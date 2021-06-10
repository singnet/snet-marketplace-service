import json
import os
import uuid
import tempfile
from common.boto_utils import BotoUtils
from common.logger import get_logger
from utility.config import NODEJS_PROTO_LAMBDA_ARN, SUPPORTED_ENVIRONMENT, REGION_NAME, PYTHON_PROTO_LAMBDA_ARN
from utility.application.handlers.proto_stubs_handler import generate_python_stubs
from common import utils
from utility.config import PROTO_DIRECTORY_REGEX_PATTERN

TEMP_FILE_DIR = tempfile.gettempdir()
boto_utils = BotoUtils(region_name=REGION_NAME)
logger = get_logger(__name__)

class GenerateStubService:
    def __init__(self):
        pass

    def manage_proto_compilation(self, input_s3_path, output_s3_path):
        try:
            base = os.path.join(TEMP_FILE_DIR, uuid.uuid4().hex)
            extracted = os.path.join(base,"extracted")
            stub_bucket, stub_bucket_key = boto_utils.get_bucket_and_key_from_url(url=output_s3_path)
            proto_bucket, proto_bucket_key = boto_utils.get_bucket_and_key_from_url(url=input_s3_path)
            # clear existing proto files
            self.clear_s3_files(bucket=stub_bucket, key=stub_bucket_key[:-1])
            self.clear_s3_files(bucket=proto_bucket, key=f"{proto_bucket_key}proto_extracted")
            # extract and upload the proto files
            compressed_proto_files = boto_utils.get_objects_from_s3(bucket=proto_bucket, key=proto_bucket_key)
            for file in compressed_proto_files:
                if utils.match_regex_string(path=f"s3://{proto_bucket}/{file['Key']}", regex_pattern=PROTO_DIRECTORY_REGEX_PATTERN):
                    name, extension = utils.get_file_name_and_extension_from_path(file['Key'])
                    download_folder = os.path.join(f"{base}_{name}{extension}")
                    boto_utils.s3_download_file(
                        bucket=proto_bucket, key=file['Key'], filename=download_folder
                    )
                    utils.extract_zip_file(zip_file_path=download_folder, extracted_path=os.path.join(extracted,name))
            boto_utils.upload_folder_contents_to_s3(
                folder_path=extracted,
                bucket=proto_bucket,
                key=proto_bucket_key+'proto_extracted'
            )
            # call lambdas for processing protos
            error_messages = []
            error_msg = "Error in compiling {} proto stubs at {}.Response :: {}"
            for environment in SUPPORTED_ENVIRONMENT:
                if environment is 'python':
                    response = self.invoke_python_stubs_lambda(input_s3_path=input_s3_path+"proto_extracted/", output_s3_path=output_s3_path)
                if environment is 'nodejs':
                    response = self.invoke_node_stubs_lambda(input_s3_path=input_s3_path+"proto_extracted/", output_s3_path=output_s3_path)
                if response.get("statusCode",{}) != 200:
                    msg = error_msg.format(environment,input_s3_path,response)
                    logger.info(msg)
                    error_messages.append(msg)
                if error_messages:
                    raise Exception(error_messages)
            return {"message":"success"}
        except Exception as e:
            raise e(f"proto lambda invocation failed {repr(e)}")

    @staticmethod
    def invoke_node_stubs_lambda(input_s3_path, output_s3_path):
        payload = json.dumps({
            "input_s3_path": input_s3_path,
            "output_s3_path": output_s3_path
        })
        response = boto_utils.invoke_lambda(
            invocation_type="RequestResponse",
            payload=payload,
            lambda_function_arn=NODEJS_PROTO_LAMBDA_ARN
        )
        return response

    @staticmethod
    def invoke_python_stubs_lambda(input_s3_path, output_s3_path):
        payload = json.dumps({
            "input_s3_path": input_s3_path,
            "output_s3_path": output_s3_path
        })
        response = boto_utils.invoke_lambda(
            invocation_type="RequestResponse",
            payload=payload,
            lambda_function_arn=PYTHON_PROTO_LAMBDA_ARN
        )
        return response

    @staticmethod
    def clear_s3_files(bucket, key):
        try:
            to_delete_objects = boto_utils.get_objects_from_s3(bucket=bucket, key=key)
            for delete_obj in to_delete_objects:
                boto_utils.delete_objects_from_s3(bucket=bucket, key=delete_obj["Key"], key_pattern=key)
        except Exception as e:
            msg = f"Error in deleting stub files :: {repr(e)}"
            logger.info(msg)
            raise Exception(msg)