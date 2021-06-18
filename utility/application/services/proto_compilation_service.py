import json
import os
import uuid

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from utility.config import NODEJS_PROTO_LAMBDA_ARN, SUPPORTED_ENVIRONMENT, REGION_NAME, PYTHON_PROTO_LAMBDA_ARN
from utility.config import PROTO_DIRECTORY_REGEX_PATTERN

TEMP_FILE_DIR = "D:\\tmp"
# tempfile.gettempdir()
boto_utils = BotoUtils(region_name=REGION_NAME)
logger = get_logger(__name__)


class GenerateStubService:
    def __init__(self):
        pass

    def manage_proto_compilation(self, input_s3_path, output_s3_path):
        try:
            proto_bucket, proto_key = boto_utils.get_bucket_and_key_from_url(url=input_s3_path)
            file_pattern = self.get_file_regex_pattern(proto_key=proto_key)
            if file_pattern and utils.match_regex_string(path=f"s3://{proto_bucket}/{proto_key}",
                                                         regex_pattern=file_pattern):

                # clear existing files
                if output_s3_path:
                    stub_bucket, stub_bucket_key = boto_utils.get_bucket_and_key_from_url(url=output_s3_path)
                    self.clear_s3_files(bucket=stub_bucket, key=stub_bucket_key[:-1])

                name, extension = utils.get_file_name_and_extension_from_path(proto_key)
                proto_extract_key = proto_key.replace(name + extension, "") + "proto_extracted"
                self.clear_s3_files(bucket=proto_bucket, key=proto_extract_key)
                # download --> extract --> upload
                base = os.path.join(TEMP_FILE_DIR, uuid.uuid4().hex)
                download = f"{base}_proto_{name}{extension}"
                extracted = f"{base}_proto_{name}_extracted"
                boto_utils.s3_download_file(
                    bucket=proto_bucket, key=proto_key, filename=download
                )
                utils.extract_zip_file(zip_file_path=download, extracted_path=extracted)
                extracted = self.handle_extraction_path(filename=f'{name}{extension}', extracted=extracted)
                boto_utils.upload_folder_contents_to_s3(
                    folder_path=extracted,
                    bucket=proto_bucket,
                    key=proto_extract_key
                )
            else:
                raise Exception(f"Input proto file url is invalid {input_s3_path}")

            # call lambdas for processing protos
            error_messages = []
            stub_urls = []
            error_msg = "Error in compiling {} proto stubs at {}.Response :: {}"
            for environment in SUPPORTED_ENVIRONMENT:
                if environment is 'python':
                    response = self.invoke_python_stubs_lambda(input_s3_path=f"s3://{proto_bucket}/{proto_extract_key}",
                                                               output_s3_path=output_s3_path)
                if environment is 'nodejs':
                    response = self.invoke_node_stubs_lambda(input_s3_path=input_s3_path + "proto_extracted/",
                                                             output_s3_path=output_s3_path)
                if response.get("statusCode", {}) == 200:
                    stub_urls.append(json.loads(response['body']).get('data', {}).get('s3_url', ""))
                else:
                    msg = error_msg.format(environment, input_s3_path, response)
                    logger.info(msg)
                    error_messages.append(msg)
            if error_messages:
                raise Exception(error_messages)
            return {"message": "success", "stubs_url": stub_urls}
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

    @staticmethod
    def handle_extraction_path(filename, extracted):
        if filename.endswith('tar.gz'):
            sub_folder_name = filename.replace('.tar.gz', '')
            extracted = os.path.join(extracted, sub_folder_name)
        return extracted

    @staticmethod
    def get_file_regex_pattern(proto_key):
        if proto_key.endswith("tar.gz"):
            return PROTO_DIRECTORY_REGEX_PATTERN["component"]
        if proto_key.endswith(".zip"):
            return PROTO_DIRECTORY_REGEX_PATTERN["asset"]