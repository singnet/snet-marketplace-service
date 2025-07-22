import json
import os
import tempfile
import uuid
import re
from pathlib import Path
import pkg_resources
from grpc_tools.protoc import main as protoc

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.utils import create_text_file
from utility.application.schemas import StubsGenerationRequest
from utility.settings import settings
from utility.constants import PYTHON_BOILERPLATE_TEMPLATE
from utility.exceptions import ProtoNotFound

TEMP_FILE_DIR = tempfile.gettempdir()
boto_utils = BotoUtils(region_name=settings.aws.REGION_NAME)
logger = get_logger(__name__)


class StubsGeneratorService:
    def manage_proto_compilation(self, request: StubsGenerationRequest):
        input_s3_path = request.input_s3_path
        output_s3_path = request.output_s3_path
        org_id = request.org_id
        service_id = request.service_id
        logger.info(f"Start manage proto compilation :: org_id: {org_id}, service_id: {service_id}")
        input_bucket_name, input_file_path = boto_utils.get_bucket_and_key_from_url(
            url=input_s3_path
        )
        logger.info(f"input_bucket_name: {input_bucket_name}, input_file_path: {input_file_path}")

        if output_s3_path:
            output_bucket_name, output_file_path = boto_utils.get_bucket_and_key_from_url(
                url=output_s3_path
            )
            logger.info(
                f"output_bucket_name: {output_bucket_name}, output_file_path: {output_file_path}"
            )

        input_file_name, input_file_extension = utils.get_file_name_and_extension_from_path(
            input_file_path
        )
        logger.info(
            f"input_file_name: {input_file_name}, input_file_extension: {input_file_extension}"
        )

        input_s3_file_key = input_file_path.replace(input_file_name + input_file_extension, "")
        temp_proto_file_path = input_s3_file_key + "temp_proto_extracted"
        logger.info(
            f"input_s3_file_key: {input_s3_file_key}, temp_proto_file_path: {temp_proto_file_path}"
        )

        # Clear temp files from s3
        BotoUtils.clear_s3_files(bucket=input_bucket_name, key=temp_proto_file_path)
        self._download_extract_and_upload_proto_files(
            filename=input_file_name,
            input_file_extension=input_file_extension,
            bucket_name=input_bucket_name,
            download_file_path=input_file_path,
            upload_file_path=temp_proto_file_path,
        )

        # Compile lambdas --> move stubs to temp file
        temp_output_path = (
            os.path.join(output_s3_path, "temp_stubs/") if output_s3_path else output_s3_path
        )
        lambda_payload = json.dumps(
            {
                "input_s3_path": f"s3://{input_bucket_name}/{temp_proto_file_path}",
                "output_s3_path": temp_output_path,
                "org_id": org_id,
                "service_id": service_id,
            }
        )
        response = {}
        for environment in settings.compile_proto.SUPPORTED_ENVIRONMENT:
            if environment in "python":
                response = boto_utils.invoke_lambda(
                    invocation_type="RequestResponse",
                    payload=lambda_payload,
                    lambda_function_arn=settings.compile_proto.ARN.PYTHON_PROTO_LAMBDA_ARN,
                )
            elif environment in "nodejs":
                response = boto_utils.invoke_lambda(
                    invocation_type="RequestResponse",
                    payload=lambda_payload,
                    lambda_function_arn=settings.compile_proto.ARN.NODEJS_PROTO_LAMBDA_ARN,
                )
            if response.get("statusCode", {}) != 200:
                raise Exception(
                    f"Invalid proto file found on given path :: {input_s3_path} :: response :: {response}"
                )

        logger.info(f"Getting response from proto compilation lambda :: {response}")

        # Move objects from temp folder to output if success
        # if no output path only remove temp extracted proto
        if output_s3_path:
            boto_utils.move_s3_objects(
                source_bucket=input_bucket_name,
                source_key=temp_proto_file_path,
                target_bucket=output_bucket_name,
                target_key=f"{input_s3_file_key}proto_extracted/",
                clear_destination=True,
            )
            boto_utils.move_s3_objects(
                source_bucket=input_bucket_name,
                source_key=boto_utils.get_bucket_and_key_from_url(temp_output_path)[1],
                target_bucket=output_bucket_name,
                target_key=f"{output_file_path}stubs/",
                clear_destination=True,
            )
        else:
            BotoUtils.clear_s3_files(bucket=input_bucket_name, key=temp_proto_file_path)
        return {}

    def generate_python_stubs(self, request: StubsGenerationRequest):
        input_s3_path = request.input_s3_path
        output_s3_path = request.output_s3_path
        org_id = request.org_id
        service_id = request.service_id
        logger.info(f"Generate python stubs :: org_id: {org_id}, {service_id}")
        input_bucket, input_key = boto_utils.get_bucket_and_key_from_url(url=input_s3_path)
        if output_s3_path:
            output_bucket, output_key = boto_utils.get_bucket_and_key_from_url(url=output_s3_path)
        tmp_paths = self._initialize_temp_paths(service_id=service_id)
        boto_utils.download_folder_contents_from_s3(
            bucket=input_bucket, key=input_key, target=tmp_paths["proto"]
        )
        proto_location = None
        proto_names = []
        training_indicator = False
        for subdir, _, files in os.walk(tmp_paths["proto"]):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".proto"):
                    proto_names.append(os.path.basename(filepath))
                    proto_location = filepath
                    self._compile_proto(
                        entry_path=subdir,
                        codegen_dir=os.path.join(tmp_paths["stubs"]),
                        proto_file_path=proto_location,
                    )
                    training_indicator = self._find_training_indicator(proto_path=proto_location)
        if proto_location is None:
            raise ProtoNotFound

        self._prepare_readme_file(
            target_path=os.path.join(tmp_paths["base"], "readme.txt"), service_id=service_id
        )

        # generate boilerplate stubs
        utils.copy_directory(tmp_paths["stubs"], tmp_paths["boilerplate"])
        self._prepare_boilerplate_template(
            org_id=org_id, service_id=service_id, target_location=tmp_paths["boilerplate"]
        )

        if output_s3_path:
            utils.zip_file(
                source_path=Path(tmp_paths["base"]), zipped_path=Path(tmp_paths["result"])
            )
            boto_utils.s3_upload_file(
                filename=tmp_paths["result"], bucket=output_bucket, key=output_key + "python.zip"
            )
        return {"training_indicator": training_indicator}

    @staticmethod
    def _handle_extraction_path(filename, extracted):
        if filename.endswith("tar.gz"):
            sub_folder_name = filename.replace(".tar.gz", "")
            extracted = os.path.join(extracted, sub_folder_name)
        return extracted

    @staticmethod
    def _download_extract_and_upload_proto_files(
        filename, input_file_extension, bucket_name, download_file_path, upload_file_path
    ):
        base = os.path.join(TEMP_FILE_DIR, uuid.uuid4().hex)
        download = f"{base}_{filename}{input_file_extension}"
        extracted = f"{base}_{filename}"
        logger.info(f"base: {base}, download: {download}, extracted: {extracted}")

        boto_utils.s3_download_file(bucket=bucket_name, key=download_file_path, filename=download)
        utils.extract_zip_file(zip_file_path=download, extracted_path=extracted)

        boto_utils.upload_folder_contents_to_s3(
            folder_path=extracted, bucket=bucket_name, key=upload_file_path
        )

    @staticmethod
    def _initialize_temp_paths(service_id):
        base = os.path.join(TEMP_FILE_DIR, uuid.uuid4().hex)
        if not os.path.exists(base):
            os.makedirs(base)
        temporary_paths = {
            "base": base,
            "proto": os.path.join(base, f"{service_id}-proto"),
            "stubs": os.path.join(base, f"{service_id}-grpc-stubs"),
            "boilerplate": os.path.join(base, f"{service_id}-boilerplate"),
            "result": f"{base}_python.zip",
        }
        return temporary_paths

    @staticmethod
    def _compile_proto(entry_path, codegen_dir, proto_file_path):
        proto_include = pkg_resources.resource_filename("grpc_tools", "_proto")
        compiler_args = ["-I{}".format(entry_path), "-I{}".format(proto_include)]
        if not os.path.exists(codegen_dir):
            os.makedirs(codegen_dir, exist_ok=True)
        compiler_args.insert(0, "protoc")
        compiler_args.append("--python_out={}".format(codegen_dir))
        compiler_args.append("--grpc_python_out={}".format(codegen_dir))
        compiler = protoc
        compiler_args.append(str(proto_file_path))
        return (True, codegen_dir) if not compiler(compiler_args) else (False, None)

    @staticmethod
    def _prepare_readme_file(target_path, service_id):
        context = (
            f"INSTRUCTIONS:\n"
            f"1.{service_id}-proto contains proto files of the service.\n"
            f"2.{service_id}-grpc-stubs contains compiled grpc stubs required for invoking the service.\n"
            f"3.{service_id}-boilerplate contains the sample code.\n"
            f"NOTE:Please follow instructions provided in the python tab of install and run on how to invoke "
            f"the service."
        )
        utils.create_text_file(target_path=target_path, context=context)

    @staticmethod
    def _find_training_indicator(proto_path: str) -> bool:
        with open(proto_path, "r", encoding="utf-8") as file:
            text_data = file.read()
            pattern = r'option \(training\.my_method_option\)\.trainingMethodIndicator\s*=\s*"true"'
            return bool(re.search(pattern, text_data))

    def _prepare_boilerplate_template(self, target_location, org_id, service_id):
        for content in PYTHON_BOILERPLATE_TEMPLATE:
            context = self._prepare_data(
                PYTHON_BOILERPLATE_TEMPLATE[content]["content"], org_id, service_id
            )
            create_text_file(
                target_path=f"{target_location}/{content}{PYTHON_BOILERPLATE_TEMPLATE[content]['extension']}",
                context=context,
            )
        return target_location

    @staticmethod
    def _prepare_data(data, org_id, service_id):
        replace_keys = {("org_id_placeholder", org_id), ("service_id_placeholder", service_id)}
        for key in replace_keys:
            data = data.replace(key[0], key[1])
        return data
