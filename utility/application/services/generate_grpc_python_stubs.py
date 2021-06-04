import os
import tempfile
import uuid
from pathlib import Path

import pkg_resources
from grpc_tools.protoc import main as protoc

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from contract_api.config import REGION_NAME
from utility.config import PROTO_DIRECTORY_REGEX_PATTERN, SLACK_HOOK
from utility.exceptions import ProtoNotFound

TEMP_FILE_DIR = "D:\\tmp"
boto_utils = BotoUtils(region_name=REGION_NAME)
logger = get_logger(__name__)


def generate_python_stubs(proto_s3_url, stub_s3_url):
    try:
        # Get compressed_proto_files from s3 location
        proto_bucket, proto_bucket_key = boto_utils.get_bucket_and_key_from_url(url=proto_s3_url)
        stub_bucket, stub_bucket_key = boto_utils.get_bucket_and_key_from_url(url=stub_s3_url)
        compressed_proto_files = boto_utils.get_objects_from_s3(bucket=proto_bucket, key=proto_bucket_key)

        if len(compressed_proto_files) == 0:
            raise Exception(f"Proto files are missing in location :: {proto_s3_url}")

        # Temp location file handling details
        temp = os.path.join(TEMP_FILE_DIR, uuid.uuid4().hex + '_proto_')
        temp_downloaded_path = temp + '.zip'
        temp_extracted_path = temp + 'extracted'
        temp_result_path = os.path.join(temp_extracted_path, 'stubs')

        for file in compressed_proto_files:
            if utils.validate_file_url(path=f"s3://{proto_bucket}/{file['Key']}", regex_pattern=PROTO_DIRECTORY_REGEX_PATTERN):
                folder_name ,file_extension = utils.get_file_name_and_extension_from_path(path=file['Key'])
                # download and extract
                utils.download_extract_zip_files_from_s3(
                    boto_utils=boto_utils,
                    bucket=proto_bucket,
                    key=file['Key'],
                    download_location=temp_downloaded_path,
                    extract_location=temp_extracted_path
                )

                # Generate stubs
                proto_location = None
                for filename in os.listdir(temp_extracted_path):
                    if filename.endswith(".proto"):
                        proto_location = os.path.join(temp_extracted_path, filename)
                    if proto_location:
                        compile_proto(
                            entry_path=Path(temp_extracted_path),
                            codegen_dir=os.path.join(temp_result_path, f"python/{folder_name}"),
                            proto_file_path=Path(proto_location),
                        )
                    else:
                        raise ProtoNotFound

        # zip and upload to s3
        utils.zip_and_upload_to_s3(boto_utils=boto_utils,
                                   bucket=stub_bucket,
                                   key=f"{stub_bucket_key}python{file_extension}",
                                   zipped_path= os.path.join(temp_extracted_path,f"python{file_extension}"),
                                   source=Path(temp_result_path)
                                   )
        return {"message":"success"}
    except ProtoNotFound as protoException:
        message = (f"Proto file is not found for proto_s3_url :: {proto_s3_url}")
        logger.info(message)
        utils.report_slack(slack_msg=message, SLACK_HOOK=SLACK_HOOK)
    except Exception as e:
        raise e(f"Error in generating python proto stubs {repr(e)}")


def compile_proto(entry_path, codegen_dir, proto_file_path):
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





