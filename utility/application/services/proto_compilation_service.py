import json
import os
import tempfile
import uuid

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from utility.config import NODEJS_PROTO_LAMBDA_ARN, SUPPORTED_ENVIRONMENT, REGION_NAME, PYTHON_PROTO_LAMBDA_ARN

TEMP_FILE_DIR = tempfile.gettempdir()
boto_utils = BotoUtils(region_name=REGION_NAME)
logger = get_logger(__name__)

class GenerateStubService:
    def __init__(self):
        pass

    @staticmethod
    def download_extract_and_upload_proto_files(filename, input_file_extension, bucket_name, download_file_path,
                                                upload_file_path):
        base = os.path.join(TEMP_FILE_DIR, uuid.uuid4().hex)
        download = f"{base}_{filename}{input_file_extension}"
        extracted = f"{base}_{filename}"
        boto_utils.s3_download_file(
            bucket=bucket_name, key=download_file_path, filename=download
        )
        utils.extract_zip_file(zip_file_path=download, extracted_path=extracted)
        extracted = GenerateStubService.handle_extraction_path(
            filename=f"{filename}{input_file_extension}",
            extracted=extracted
        )
        boto_utils.upload_folder_contents_to_s3(
            folder_path=extracted,
            bucket=bucket_name,
            key=upload_file_path
        )

    def manage_proto_compilation(self, input_s3_path, output_s3_path, org_id, service_id):
        logger.info(f"Start manage proto compilation :: org_id: {org_id}, service_id: {service_id}")
        input_bucket_name, input_file_path = boto_utils.get_bucket_and_key_from_url(url=input_s3_path)
        if output_s3_path:
            output_bucket_name, output_file_path = boto_utils.get_bucket_and_key_from_url(url=output_s3_path)

        input_file_name, input_file_extension = utils.get_file_name_and_extension_from_path(input_file_path)
        input_s3_file_key = input_file_path.replace(input_file_name + input_file_extension, "")
        temp_proto_file_path = input_s3_file_key + "temp_proto_extracted"

        # Clear temp files from s3
        self.clear_s3_files(bucket=input_bucket_name, key=temp_proto_file_path)
        self.download_extract_and_upload_proto_files(
            filename=input_file_name,
            input_file_extension=input_file_extension,
            bucket_name=input_bucket_name,
            download_file_path=input_file_path,
            upload_file_path=temp_proto_file_path
        )

        # Compile lambdas --> move stubs to temp file
        temp_output_path = os.path.join(output_s3_path, "temp_stubs/") if output_s3_path else output_s3_path
        lambda_payload = json.dumps({
            "input_s3_path": f"s3://{input_bucket_name}/{temp_proto_file_path}",
            "output_s3_path": temp_output_path,
            "org_id": org_id,
            "service_id": service_id
        })
        response = {}
        for environment in SUPPORTED_ENVIRONMENT:
            if environment in "python":
                response = boto_utils.invoke_lambda(
                    invocation_type="RequestResponse",
                    payload=lambda_payload,
                    lambda_function_arn=PYTHON_PROTO_LAMBDA_ARN
                )
            elif environment in "nodejs":
                response = boto_utils.invoke_lambda(
                    invocation_type="RequestResponse",
                    payload=lambda_payload,
                    lambda_function_arn=NODEJS_PROTO_LAMBDA_ARN
                )
            if response.get("statusCode", {}) != 200:
                raise Exception(f"Invalid proto file found on given path :: {input_s3_path} :: response :: {response}")

        logger.debug(f"Getting response from proto compilation lambda :: {response}")

        # Move objects from temp folder to output if success
        # if no output path only remove temp extracted proto
        if output_s3_path:
            boto_utils.move_s3_objects(
                source_bucket=input_bucket_name,
                source_key=temp_proto_file_path,
                target_bucket=output_bucket_name,
                target_key=f"{input_s3_file_key}proto_extracted/",
                clear_destination=True
            )
            boto_utils.move_s3_objects(
                source_bucket=input_bucket_name,
                source_key=boto_utils.get_bucket_and_key_from_url(temp_output_path)[1],
                target_bucket=output_bucket_name,
                target_key=f"{output_file_path}stubs/",
                clear_destination=True
            )
        else:
            self.clear_s3_files(bucket=input_bucket_name, key=temp_proto_file_path)
        return {"training_indicator": response["data"]["training_indicator"]}

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
