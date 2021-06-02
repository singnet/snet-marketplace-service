import json
import os
import re
import tempfile
import uuid
from pathlib import Path

import pkg_resources
from grpc_tools.protoc import main as protoc

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from utility.config import PROTO_DIRECTORY_REGEX_PATTERN, PROTO_STUB_TARGET_LANGUAGES, PROTO_STUBS_BUCKET_REGION, \
    NODEJS_PROTO_LAMBDA_ARN

TEMP_FILE_DIR = tempfile.gettempdir()
boto_utils = BotoUtils(region_name=PROTO_STUBS_BUCKET_REGION)
logger = get_logger(__name__)


class GenerateStubService:
    def __init__(self):
        pass

    def generate_service_proto_stubs(self, proto_s3_url, stub_s3_url):
        try:
            proto_bucket, proto_bucket_key = boto_utils.get_bucket_and_key_from_url(url=proto_s3_url)
            stub_bucket, stub_bucket_key = boto_utils.get_bucket_and_key_from_url(url=stub_s3_url)

            self.clear_old_stub_files(stub_bucket=stub_bucket, stub_bucket_key=stub_bucket_key)

            for language in PROTO_STUB_TARGET_LANGUAGES:
                if language == 'python':
                    proto_objects = boto_utils.get_objects_from_s3(bucket=proto_bucket, key=proto_bucket_key)
                    if len(proto_objects) == 0:
                        raise Exception("Proto file is not found")
                    s3_key_pattern = re.compile(PROTO_DIRECTORY_REGEX_PATTERN)
                    for obj in proto_objects:
                        if re.match(s3_key_pattern, obj['Key']):
                            # File handling details
                            filename_with_key, file_extension = os.path.splitext(obj['Key'])
                            temp_path = os.path.join(TEMP_FILE_DIR, uuid.uuid4().hex + '_proto_')
                            temp_downloaded_path = temp_path + file_extension
                            temp_extracted_path = temp_path + 'extracted'
                            temp_generated_stub_location = os.path.join(temp_extracted_path, 'stubs')

                            if file_extension == '.zip':
                                # Download and extract files
                                boto_utils.s3_download_file(bucket=proto_bucket,
                                                            key=obj['Key'],
                                                            filename=temp_downloaded_path)
                                utils.extract_zip_file(zip_file_path=temp_downloaded_path,
                                                       extracted_path=temp_extracted_path)

                            # Generate stubs from extracted files
                            proto_location = None
                            for filename in os.listdir(temp_extracted_path):
                                if filename.endswith(".proto"):
                                    proto_location = os.path.join(temp_extracted_path, filename)
                                if proto_location:
                                    self.generate_python_stubs(
                                        entry_path=Path(temp_extracted_path),
                                        codegen_dir=os.path.join(temp_generated_stub_location, language),
                                        proto_file_path=Path(proto_location),
                                    )
                                else:
                                    raise Exception("Proto file is not found")

                            # Zip and upload stubs to s3
                            for folder in os.listdir(temp_generated_stub_location):
                                file_to_be_uploaded = os.path.join(temp_generated_stub_location, folder)
                                upload_file_name = f"{folder}{file_extension}"
                                utils.zip_file(
                                    source_path=Path(file_to_be_uploaded),
                                    zipped_path=os.path.join(temp_generated_stub_location, upload_file_name)
                                )
                                boto_utils.s3_upload_file(
                                    filename=file_to_be_uploaded + file_extension,
                                    bucket=stub_bucket,
                                    key=stub_bucket_key + '/' + upload_file_name
                                )
                if language == "nodejs":
                    self.generate_node_stubs(stub_s3_url=stub_s3_url, proto_s3_url=proto_s3_url)
        except Exception as error:
            raise error

    @staticmethod
    def generate_python_stubs(entry_path, codegen_dir, proto_file_path):
        proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')
        compiler_args = [
            "-I{}".format(entry_path),
            "-I{}".format(proto_include)
        ]
        if not os.path.exists(codegen_dir):
            os.makedirs(codegen_dir, exist_ok=True)
        compiler_args.insert(0, "protoc")
        compiler_args.append("--python_out={}".format(codegen_dir))
        compiler_args.append("--grpc_python_out={}".format(codegen_dir))
        compiler = protoc
        compiler_args.append(str(proto_file_path))
        return (True, codegen_dir) if not compiler(compiler_args) else (False, None)

    @staticmethod
    def generate_node_stubs(stub_s3_url, proto_s3_url):
        payload = json.dumps({
            "stub_s3_url": stub_s3_url,
            "proto_s3_url": proto_s3_url
        })
        boto_utils.invoke_lambda(
            invocation_type="RequestResponse",
            payload=payload,
            lambda_function_arn=NODEJS_PROTO_LAMBDA_ARN
        )

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
