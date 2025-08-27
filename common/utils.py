import datetime as dt
import decimal
import json
import os
import os.path
import re
import shutil
import tarfile
import uuid
from typing import Generator, Iterable, TypeVar
import zipfile
from urllib.parse import urlparse

import requests

from common.constant import COGS_TO_AGI, ResponseStatus
from common.logger import get_logger

IGNORED_LIST = ['row_id', 'row_created', 'row_updated']
logger = get_logger(__name__)


class Utils:
    def clean(self, value_list):
        for value in value_list:
            self.clean_row(value)

    def clean_row(self, row):
        for item in IGNORED_LIST:
            if item in row:
                del row[item]

        for key in row:
            if isinstance(row[key], decimal.Decimal) or isinstance(row[key], dt.datetime):
                row[key] = str(row[key])
            elif isinstance(row[key], bytes):
                if row[key] == b'\x01':
                    row[key] = 1
                elif row[key] == b'\x00':
                    row[key] = 0
                else:
                    raise Exception("Unsupported bytes object. Key " +
                                    str(key) + " value " + str(row[key]))

        return row

    def remove_http_https_prefix(self, url):
        url = url.replace("https://", "")
        url = url.replace("http://", "")
        return url

    def cogs_to_agi(self, cogs):
        with decimal.localcontext() as ctx:
            ctx.prec = 8
            """ 1 AGI equals to 100000000 cogs"""
            agi = decimal.Decimal(cogs) * decimal.Decimal(COGS_TO_AGI)
            return agi


def make_response(status_code, body, header=None):
    return {
        "statusCode": status_code,
        "headers": header,
        "body": body
    }


def validate_dict(data_dict, required_keys, strict=False):
    for key in required_keys:
        if key not in data_dict:
            return False

    if strict:
        return validate_dict(required_keys, data_dict.keys())

    return True


def validate_dict_list(data_list, required_keys):
    for data in data_list:
        if not validate_dict(data, required_keys):
            return False
    return True


def make_response_body(status, data, error):
    return {
        "status": status,
        "data": data,
        "error": error
    }


def generate_lambda_response(status_code, message, headers=None, cors_enabled=False):
    response = {
        'statusCode': status_code,
        'body': json.dumps(message),
        'headers': {'Content-Type': 'application/json'}
    }
    if cors_enabled:
        response["headers"].update({
            "X-Requested-With": '*',
            "Access-Control-Allow-Headers": 'Access-Control-Allow-Origin, Content-Type, X-Amz-Date, Authorization,'
                                            'X-Api-Key,x-requested-with',
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": 'GET,OPTIONS,POST'
        })
    if headers is not None:
        response["headers"].update(headers)
    return response


def extract_payload(method, event):
    method_found = True
    payload_dict = None
    path_parameters = event.get("pathParameters", None)
    if method == 'POST':
        payload_dict = json.loads(event['body'])
    elif method == 'GET':
        payload_dict = event.get('queryStringParameters', {})
    else:
        method_found = False
    return method_found, path_parameters, payload_dict


def format_error_message(status, error, payload, net_id, handler=None, resource=None):
    return json.dumps(
        {'status': status, 'error': error, 'resource': resource, 'payload': payload, 'network_id': net_id,
         'handler': handler})

def json_to_file(payload, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps(payload, indent=4))


def datetime_to_string(given_time):
    return given_time.strftime("%Y-%m-%d %H:%M:%S")


def date_time_for_filename():
    return dt.datetime.now(dt.UTC).strftime("%Y%m%d%H%M%S")


def download_file_from_url(file_url, file_dir):
    response = requests.get(file_url)
    filename = urlparse(file_url).path.split("/")[-1]
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    with open(f"{file_dir}/{filename}", 'wb') as asset_file:
        asset_file.write(response.content)
    return filename



def send_email_notification(recipients, notification_subject, notification_message, notification_arn, boto_util):
    for recipient in recipients:
        try:
            if bool(recipient):
                send_notification_payload = {"body": json.dumps({
                    "message": notification_message,
                    "subject": notification_subject,
                    "notification_type": "support",
                    "recipient": recipient})}
                boto_util.invoke_lambda(lambda_function_arn=notification_arn, invocation_type="RequestResponse",
                                        payload=json.dumps(send_notification_payload))
                logger.info(f"email_sent to {recipient}")
        except:
            logger.error(f"Error happened while sending email to recipient {recipient}")


def extract_zip_file(zip_file_path, extracted_path):
    if zip_file_path.endswith(".zip"):
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_path)
    if zip_file_path.endswith("tar.gz"):
        tar = tarfile.open(zip_file_path, "r:gz")
        tar.extractall(path=extracted_path)
        tar.close()
    if zip_file_path.endswith("tar"):
        tar = tarfile.open(zip_file_path, "r:")
        tar.extractall(path=extracted_path)
        tar.close()


def zip_file(source_path, zipped_path):
    outZipFile = zipfile.ZipFile(zipped_path, 'w', zipfile.ZIP_DEFLATED)
    for dir_path, dir_names, filenames in os.walk(source_path):
        for filename in filenames:
            filepath = os.path.join(dir_path, filename)
            parent_path = os.path.relpath(filepath, source_path)
            arc_name = parent_path
            outZipFile.write(filepath, arc_name)
    outZipFile.close()
    return zipped_path


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def match_regex_string(path, regex_pattern):
    key_pattern = re.compile(regex_pattern)
    match = re.match(key_pattern, path)
    return match


def get_file_name_and_extension_from_path(path):
    base = os.path.basename(path)
    return os.path.splitext(base)


def if_external_link(link):
    return link.startswith("https://") or link.startswith("http://")


def copy_directory(source, target):
    if not os.path.exists(target):
        os.makedirs(target)
    for filename in os.listdir(source):
        shutil.copy(os.path.join(source, filename), target)


def create_text_file(target_path, context):
    f = open(target_path, "a")
    f.write(context)
    f.close()


def format_response(status, response):
    if status == ResponseStatus.SUCCESS:
        return {"status": status, "data": response}
    elif status == ResponseStatus.FAILED:
        error_data = {
            "code": response.get("code", 0000),
            "message": response.get("message", "Unexpected error"),
            "details": response.get("details", {})
        }
        return {"status": status, "error": error_data}
    else:
        return {}


T = TypeVar("T")

def chunked(items: Iterable[T], size: int) -> Generator[list[T], None, None]:
    """
    Splits an iterable into chunks of the given size.

    Args:
        items: Any iterable of T (e.g., List[NewUser])
        size: Batch size

    Yields:
        Lists of size up to `size`, each containing items of type T
    """
    items = list(items)  # support generators/iterables too
    for i in range(0, len(items), size):
        yield items[i:i + size]


def generate_uuid() -> str:
    return str(uuid.uuid4())


def dict_keys_to_camel_case(snake_keys_dict: dict, recursively: bool = False) -> dict:
    result = {}
    for key, value in snake_keys_dict.items():
        if isinstance(value, dict) and recursively:
            value = dict_keys_to_camel_case(value, recursively)
        result[snake_to_camel(key)] = value
    return result


def snake_to_camel(snake_str: str) -> str:
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])