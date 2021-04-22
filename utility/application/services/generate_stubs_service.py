import os
import re
import subprocess
import tempfile
import uuid
from pathlib import Path, PurePath

import pkg_resources
from grpc_tools.protoc import main as protoc
from snet import snet_cli

from common import file_utils
from common.s3_util import S3Util
from utility.config import PROTO_DIRECTORY_REGEX_PATTERN, PROTO_STUB_TARGET_LANGUAGES

TEMP_FILE_DIR = tempfile.gettempdir()


class GenerateStubService:
    def __init__(self, s3_bucket_access_key, s3_bucket_secret_key):
        self.s3_utils = S3Util(s3_bucket_access_key, s3_bucket_secret_key)

    def generate_service_proto_stubs(self, proto_s3_url, stub_s3_url):
        try:
            proto_bucket, proto_bucket_key = self.s3_utils.get_bucket_and_key_from_url(url=proto_s3_url)
            stub_bucket, stub_bucket_key = self.s3_utils.get_bucket_and_key_from_url(url=stub_s3_url)

            self.s3_utils.delete_objects_from_s3(bucket=stub_bucket, key=stub_bucket_key)
            file_objects = self.s3_utils.get_objects_from_s3(bucket=proto_bucket, key=proto_bucket_key)

            if len(file_objects) == 0:
                raise Exception("Proto file is not found")

            s3_key_pattern = re.compile(PROTO_DIRECTORY_REGEX_PATTERN)
            for obj in file_objects:
                if re.match(s3_key_pattern, obj['Key']):
                    # file details
                    filename_with_key, file_extension = os.path.splitext(obj['Key'])
                    # temp locations
                    temp_path = TEMP_FILE_DIR + '\\' + uuid.uuid4().hex + '_proto_'
                    temp_extracted_path = temp_path + 'extracted'
                    temp_downloaded_path = temp_path + file_extension
                    temp_generated_stub_location = temp_extracted_path + '\\stubs'

                    if file_extension == '.zip':
                        # download and extract files from s3 and store in temp location
                        self.s3_utils.download_s3_object(bucket=proto_bucket, key=obj['Key'], target_directory=temp_downloaded_path)
                        file_utils.unzip_file(source_path=temp_downloaded_path, destination_path=temp_extracted_path)

                        # if proto file present generate stub zip and upload to s3
                        proto_location = None
                        for filename in os.listdir(temp_extracted_path):
                            if filename.endswith(".proto"):
                                proto_location = os.path.join(temp_extracted_path, filename)
                                filename_without_extn = os.path.splitext(filename)[0]
                            if proto_location:
                                for language in PROTO_STUB_TARGET_LANGUAGES:
                                    result, file_location = self.generate_stubs(
                                        entry_path=Path(temp_extracted_path),
                                        codegen_dir=Path(temp_generated_stub_location + '\\' + language),
                                        target_language=language,
                                        proto_file_path=proto_location,
                                        proto_file_name=filename_without_extn
                                    )
                                    if not result:
                                        raise Exception("Error in generating stub")
                            else:
                                raise Exception("Proto file is not found")

                        # zip and upload generated files
                        for folder in os.listdir(temp_generated_stub_location):
                            file_to_be_uploaded = temp_generated_stub_location + '\\' + \
                                                               f'{language}'
                            upload_file_name = f"{language}{file_extension}"
                            file_utils.zip_file(
                                destination=file_to_be_uploaded,
                                source=os.path.join(temp_generated_stub_location, folder)
                            )
                            self.s3_utils.push_file_to_s3(
                                file_path=file_to_be_uploaded + file_extension,
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
                    "grpc_node_plugin.exe")).resolve()
            if not os.path.isfile(protoc_node_compiler_path) or not os.path.isfile(grpc_node_plugin_path):
                print("Missing required node.js protoc compiler. Retrieving from npm...")
                subprocess.run(["npm", "install"], cwd=RESOURCES_PATH)
            compiler_args.append("--js_out=import_style=commonjs,binary:{}".format(codegen_dir))
            compiler_args.append("--grpc_out={}".format(codegen_dir))
            compiler_args.append("--plugin=protoc-gen-grpc={}".format(grpc_node_plugin_path))
            compiler = lambda args: subprocess.run([str(protoc_node_compiler_path)] + args)
        compiler_args.append(str(proto_file_path))
        return (True, codegen_dir) if not compiler(compiler_args) else (False, None)
