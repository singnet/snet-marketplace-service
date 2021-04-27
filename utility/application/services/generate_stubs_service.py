import os
import re
import subprocess
import tempfile
import uuid
from pathlib import Path, PurePath

import pkg_resources
from grpc_tools.protoc import main as protoc
from snet import snet_cli

from common import utils
from common.boto_utils import BotoUtils
from utility.config import PROTO_DIRECTORY_REGEX_PATTERN, PROTO_STUB_TARGET_LANGUAGES

TEMP_FILE_DIR = tempfile.gettempdir()
boto_utils = BotoUtils(region_name=None)


class GenerateStubService:
    def __init__(self):
        pass

    def generate_service_proto_stubs(self, proto_s3_url, stub_s3_url):
        try:
            proto_bucket, proto_bucket_key = boto_utils.get_bucket_and_key_from_url(url=proto_s3_url)
            stub_bucket, stub_bucket_key = boto_utils.get_bucket_and_key_from_url(url=stub_s3_url)

            to_delete_objects = boto_utils.get_objects_from_s3(bucket=stub_bucket, key=stub_bucket_key)
            for delete_obj in to_delete_objects:
                boto_utils.delete_objects_from_s3(bucket=stub_bucket, key=delete_obj["Key"], key_pattern=stub_bucket_key)

            proto_objects = boto_utils.get_objects_from_s3(bucket=proto_bucket, key=proto_bucket_key)

            if len(proto_objects) == 0:
                raise Exception("Proto file is not found")

            s3_key_pattern = re.compile(PROTO_DIRECTORY_REGEX_PATTERN)
            for obj in proto_objects:
                if re.match(s3_key_pattern, obj['Key']):
                    # File details and temp locations
                    filename_with_key, file_extension = os.path.splitext(obj['Key'])
                    temp_path = os.path.join(TEMP_FILE_DIR, uuid.uuid4().hex + '_proto_')
                    temp_downloaded_path = temp_path + file_extension
                    temp_extracted_path = temp_path + 'extracted'
                    temp_generated_stub_location = os.path.join(temp_extracted_path, 'stubs')
                    # Download and unzip
                    if file_extension == '.zip':
                        boto_utils.s3_download_file(bucket=proto_bucket,
                                                    key=obj['Key'],
                                                    filename=temp_downloaded_path)
                        utils.extract_zip_file(zip_file_path=temp_downloaded_path,
                                               extracted_path=temp_extracted_path)
                        # Generate stubs
                        proto_location = None
                        for filename in os.listdir(temp_extracted_path):
                            if filename.endswith(".proto"):
                                proto_location = os.path.join(temp_extracted_path, filename)
                                filename_without_extn = os.path.splitext(filename)[0]
                            if proto_location:
                                for language in PROTO_STUB_TARGET_LANGUAGES:
                                    result, file_location = self.generate_stubs(
                                        entry_path=Path(temp_extracted_path),
                                        codegen_dir=os.path.join(temp_generated_stub_location, language),
                                        target_language=language,
                                        proto_file_path=Path(proto_location),
                                        proto_file_name=filename_without_extn
                                    )
                            else:
                                raise Exception("Proto file is not found")
                        # Zip and upload generated files
                        for folder in os.listdir(temp_generated_stub_location):
                            file_to_be_uploaded = os.path.join(temp_generated_stub_location, folder)
                            upload_file_name = f"{folder}{file_extension}"
                            utils.zip_file(
                                source_path=Path(file_to_be_uploaded),
                                zipped_path=os.path.join(temp_generated_stub_location, folder)
                            )
                            boto_utils.s3_upload_file(
                                filename=file_to_be_uploaded + file_extension,
                                bucket=stub_bucket,
                                key=stub_bucket_key + '/' + upload_file_name
                            )
        except Exception as error:
            raise error

    @staticmethod
    def generate_stubs(entry_path, target_language, codegen_dir, proto_file_path, proto_file_name):
        RESOURCES_PATH = PurePath(os.path.dirname(snet_cli.__file__)).joinpath("resources")
        proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')
        compiler_args = [
            "-I{}".format(entry_path),
            "-I{}".format(proto_include)
        ]
        if not os.path.exists(codegen_dir):
            os.makedirs(codegen_dir, exist_ok=True)
        if target_language == "python":
            compiler_args.insert(0, "protoc")
            compiler_args.append("--python_out={}".format(codegen_dir))
            compiler_args.append("--grpc_python_out={}".format(codegen_dir))
            compiler = protoc
        elif target_language == "nodejs":
            protoc_node_compiler_path = Path(
                RESOURCES_PATH.joinpath("node_modules").joinpath("grpc-tools").joinpath("bin").joinpath(
                    "protoc.js")).absolute()
            grpc_node_plugin_path = Path(
                RESOURCES_PATH.joinpath("node_modules").joinpath("grpc-tools").joinpath("bin").joinpath(
                    "grpc_node_plugin")).resolve()
            if not os.path.isfile(protoc_node_compiler_path) or not os.path.isfile(grpc_node_plugin_path):
                print("Missing required node.js protoc compiler. Retrieving from npm...")
                subprocess.run(["npm", "install"], cwd=RESOURCES_PATH)
            compiler_args.append("--js_out=import_style=commonjs,binary:{}".format(codegen_dir))
            compiler_args.append("--grpc_out={}".format(codegen_dir))
            compiler_args.append("--plugin=protoc-gen-grpc={}".format(grpc_node_plugin_path))
            compiler = lambda args: subprocess.run([str(protoc_node_compiler_path)] + args)
        compiler_args.append(str(proto_file_path))
        return (True, codegen_dir) if not compiler(compiler_args) else (False, None)
