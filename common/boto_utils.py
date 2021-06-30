import json
import os
from urllib.parse import urlparse

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from common.logger import get_logger

logger = get_logger(__name__)

class BotoUtils:
    def __init__(self, region_name):
        self.region_name = region_name

    def get_ssm_parameter(self, parameter, config=Config(retries={'max_attempts': 1})):
        """ Format config=Config(connect_timeout=1, read_timeout=0.1, retries={'max_attempts': 1}) """
        ssm = boto3.client('ssm', region_name=self.region_name, config=config)
        parameter = ssm.get_parameter(Name=parameter, WithDecryption=True)
        return parameter["Parameter"]["Value"]

    def invoke_lambda(self, lambda_function_arn, invocation_type, payload, config=Config(retries={'max_attempts': 1})):
        """ Format config=Config(connect_timeout=1, read_timeout=0.1, retries={'max_attempts': 1}) """
        lambda_client = boto3.client('lambda', region_name=self.region_name, config=config)
        lambda_response = lambda_client.invoke(FunctionName=lambda_function_arn, InvocationType=invocation_type,
                                               Payload=payload)
        if invocation_type == "Event":
            return lambda_response
        return json.loads(lambda_response.get('Payload').read())

    def s3_upload_file(self, filename, bucket, key):
        s3_client = boto3.client('s3')
        s3_client.upload_file(filename, bucket, key)

    def s3_download_file(self, bucket, key, filename):
        s3_client = boto3.client('s3')
        s3_client.download_file(bucket, key, filename)

    def get_parameter_value_from_secrets_manager(self, secret_name):
        config = Config(retries=dict(max_attempts=2))
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=self.region_name, config=config)
        try:
            parameter_value = client.get_secret_value(SecretId=secret_name)['SecretString']
        except ClientError as e:
            logger.error(f"Failed to fetch credentials {e}")
            raise e

        response = json.loads(parameter_value)
        return response[secret_name]

    @staticmethod
    def delete_objects_from_s3(bucket, key, key_pattern):
        if key_pattern in key:
                s3_client = boto3.client('s3')
                s3_client.delete_object(Bucket=bucket, Key=key)

    @staticmethod
    def get_objects_from_s3(bucket, key):
        s3 = boto3.client('s3')
        objects = []
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=key)
        for page in pages:
            if page.get("Contents", None):
                for obj in page['Contents']:
                    objects.append(obj)
        return objects

    @staticmethod
    def get_bucket_and_key_from_url(url):
        parsed_url = urlparse(url)
        return parsed_url.hostname.split(".")[0], parsed_url.path[1:]

    def upload_folder_contents_to_s3(self, folder_path, bucket, key):
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    folder_name = root.replace(str(folder_path), "")
                    folder_name = folder_name.replace(os.path.sep, "")
                    if folder_name:
                        folder_name = folder_name + "/"
                    self.s3_upload_file(filename=os.path.join(root, file), bucket=bucket,
                                        key=f"{key}/{folder_name}{file}")
        except Exception as e:
            raise e

    def download_folder_contents_from_s3(self, bucket, key, target):
        try:
            keys = self.get_objects_from_s3(bucket=bucket, key=key)
            for object_key in keys:
                path, filename = os.path.split(object_key['Key'])
                file_or_folder = object_key['Key'].replace(key,"")
                sub_folder_structure = ""
                if "/" in file_or_folder:
                    sub_folder_structure = path.replace(key, "")
                target_path = os.path.join(target, sub_folder_structure)
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                self.s3_download_file(bucket=bucket, key=object_key['Key'], filename=os.path.join(target_path, filename))
        except Exception as e:
            raise e

    @staticmethod
    def get_code_build_details(build_ids):
        try:
            build_client = boto3.client('codebuild')
            return build_client.batch_get_builds(ids=build_ids)
        except build_client.exceptions.InvalidInputException as e:
            raise Exception(f"build id is not found {build_ids}")

    @staticmethod
    def trigger_code_build(build_details):
        try:
            cb = boto3.client('codebuild')
            build = cb.start_build(**build_details)
            return build
        except Exception as e:
            raise e

    def move_s3_objects(self, source_bucket, source_key, target_bucket, target_key, clear_destination=False):
        s3 = boto3.resource('s3')
        source_objects = self.get_objects_from_s3(bucket=source_bucket, key=source_key)
        dest_bucket = s3.Bucket(target_bucket)
        if clear_destination:
            destination_key = target_key[:-1] if target_key.endswith('/') else target_key
            target_objects = self.get_objects_from_s3(bucket=target_bucket, key=destination_key)
            for key in target_objects:
                self.delete_objects_from_s3(bucket=target_bucket, key=key['Key'], key_pattern=destination_key)
        for source_key in source_objects:
            copy_source = {'Bucket': source_bucket, 'Key': source_key['Key']}
            dest_bucket.copy(copy_source, target_key + os.path.basename(source_key['Key']))
            s3.Object(source_bucket, source_key['Key']).delete()
