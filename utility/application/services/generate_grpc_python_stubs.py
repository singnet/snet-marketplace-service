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
from utility.config import SLACK_HOOK
from utility.exceptions import ProtoNotFound

TEMP_FILE_DIR = tempfile.gettempdir()
boto_utils = BotoUtils(region_name=REGION_NAME)
logger = get_logger(__name__)


def generate_python_stubs(input_s3_path, output_s3_path):
    try:
        input_bucket, input_key = boto_utils.get_bucket_and_key_from_url(url=input_s3_path)
        if output_s3_path:
            output_bucket, output_key = boto_utils.get_bucket_and_key_from_url(url=output_s3_path)
        tmp_paths = initialize_temp_paths()
        boto_utils.download_folder_contents_from_s3(bucket=input_bucket, key=input_key, target=tmp_paths["base"])
        proto_location = None
        for subdir, dirs, files in os.walk(tmp_paths["base"]):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".proto"):
                    proto_location = filepath
                    compile_proto(
                        entry_path=subdir,
                        codegen_dir=os.path.join(tmp_paths["result"]),
                        proto_file_path=proto_location
                    )
        if proto_location is None:
            raise ProtoNotFound
        if output_s3_path:
            file_to_be_uploaded = os.path.join(tmp_paths["base"], f"python.zip")
            utils.zip_file(source_path=Path(tmp_paths["result"]), zipped_path=file_to_be_uploaded)
            boto_utils.s3_upload_file(filename=file_to_be_uploaded, bucket=output_bucket, key=output_key + f"python.zip")
        return {"message": "success"}
    except ProtoNotFound as protoException:
        message = f"Proto file is not found for location :: {input_s3_path}"
        logger.info(message)
        utils.report_slack(slack_msg=message, SLACK_HOOK=SLACK_HOOK)
    except Exception as e:
        raise e(f"Error in generating python proto stubs {repr(e)}")


def initialize_temp_paths():
    base = os.path.join(TEMP_FILE_DIR, uuid.uuid4().hex)
    if not os.path.exists(base):
        os.makedirs(base)
    temporary_paths = {
        "base": base,
        "upload": os.path.join(base, "upload"),
        "result": os.path.join(base, 'stubs', 'python')}
    return temporary_paths


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
