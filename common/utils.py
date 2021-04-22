import datetime
import decimal
import glob
import hashlib
import hmac
import io
import json
import os
import os.path
import shutil
import sys
import tarfile
import traceback
import zipfile
from urllib.parse import urlparse
from zipfile import ZipFile

import requests
import web3
from web3 import Web3

from common.constant import COGS_TO_AGI, StatusCode
from common.exceptions import OrganizationNotFound
from common.logger import get_logger

IGNORED_LIST = ['row_id', 'row_created', 'row_updated']
logger = get_logger(__name__)


class Utils:

    def report_slack(self, slack_msg, SLACK_HOOK):
        url = SLACK_HOOK['hostname'] + SLACK_HOOK['path']
        payload = {"username": "webhookbot", "text": slack_msg, "icon_emoji": ":ghost:"}
        slack_response = requests.post(url=url, data=json.dumps(payload))
        logger.info(f"slack response :: {slack_response.status_code}, {slack_response.text}")

    def clean(self, value_list):
        for value in value_list:
            self.clean_row(value)

    def clean_row(self, row):
        for item in IGNORED_LIST:
            if item in row:
                del row[item]

        for key in row:
            if isinstance(row[key], decimal.Decimal) or isinstance(row[key], datetime.datetime):
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

    def get_current_block_no(self, ws_provider):
        w3Obj = Web3(web3.providers.WebsocketProvider(ws_provider))
        return w3Obj.eth.blockNumber

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


def handle_exception_with_slack_notification(*decorator_args, **decorator_kwargs):
    logger = decorator_kwargs["logger"]
    NETWORK_ID = decorator_kwargs.get("NETWORK_ID", None)
    SLACK_HOOK = decorator_kwargs.get("SLACK_HOOK", None)
    IGNORE_EXCEPTION_TUPLE = decorator_kwargs.get("IGNORE_EXCEPTION_TUPLE", ())

    def decorator(func):
        def wrapper(*args, **kwargs):
            handler_name = decorator_kwargs.get("handler_name", func.__name__)
            path = kwargs.get("event", {}).get("path", None)
            path_parameters = kwargs.get("event", {}).get("pathParameters", {})
            query_string_parameters = kwargs.get("event", {}).get("queryStringParameters", {})
            body = kwargs.get("event", {}).get("body", "{}")
            payload = {"pathParameters": path_parameters,
                       "queryStringParameters": query_string_parameters,
                       "body": json.loads(body)}
            try:
                return func(*args, **kwargs)
            except IGNORE_EXCEPTION_TUPLE as e:
                logger.exception("Exception is part of IGNORE_EXCEPTION list. Error description: %s", repr(e))
                return generate_lambda_response(
                    status_code=500,
                    message=format_error_message(
                        status="failed", error=repr(e), payload=payload, net_id=NETWORK_ID, handler=handler_name),
                    cors_enabled=True)
            except OrganizationNotFound as e:
                logger.exception(f"Organization no found {repr(e)}")
                return generate_lambda_response(
                    StatusCode.INTERNAL_SERVER_ERROR,
                    {"status": "success", "data": "", "error": {"code": "", "message": "ORG_NOT_FOUND"}},
                    cors_enabled=True
                )
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                slack_msg = f"\n```Error Reported !! \n" \
                            f"network_id: {NETWORK_ID}\n" \
                            f"path: {path}, \n" \
                            f"handler: {handler_name} \n" \
                            f"pathParameters: {path_parameters} \n" \
                            f"queryStringParameters: {query_string_parameters} \n" \
                            f"body: {body} \n" \
                            f"x-ray-trace-id: None \n" \
                            f"error_description: {repr(traceback.format_tb(tb=exc_tb))}```"

                logger.exception(f"{slack_msg}")
                Utils().report_slack(slack_msg=slack_msg, SLACK_HOOK=SLACK_HOOK)
                return generate_lambda_response(
                    status_code=500,
                    message=format_error_message(
                        status="failed", error=repr(e), payload=payload, net_id=NETWORK_ID, handler=handler_name),
                    cors_enabled=True)

        return wrapper

    return decorator


def json_to_file(payload, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps(payload, indent=4))


def datetime_to_string(given_time):
    return given_time.strftime("%Y-%m-%d %H:%M:%S")


def date_time_for_filename():
    return datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")


def hash_to_bytesuri(s):
    """
    Convert in and from bytes uri format used in Registry contract
    """
    # TODO: we should pad string with zeros till closest 32 bytes word because of a bug in processReceipt (in snet_cli.contract.process_receipt)
    s = "ipfs://" + s
    return s.encode("ascii").ljust(32 * (len(s) // 32 + 1), b"\0")


def ipfsuri_to_bytesuri(uri):
    # we should pad string with zeros till closest 32 bytes word because of a bug in processReceipt (in snet_cli.contract.process_receipt)
    return uri.encode("ascii").ljust(32 * (len(uri) // 32 + 1), b"\0")


def publish_file_in_ipfs(file_url, file_dir, ipfs_client, wrap_with_directory=True):
    filename = download_file_from_url(file_url=file_url, file_dir=file_dir)
    file_type = os.path.splitext(filename)[1]
    if file_type.lower() == ".zip":
        return publish_zip_file_in_ipfs(filename, file_dir, ipfs_client)
    ipfs_hash = ipfs_client.write_file_in_ipfs(f"{file_dir}/{filename}", wrap_with_directory)
    return ipfs_hash


def publish_zip_file_in_ipfs(filename, file_dir, ipfs_client):
    file_in_tar_bytes = convert_zip_file_to_tar_bytes(file_dir=file_dir, filename=filename)
    return ipfs_client.ipfs_conn.add_bytes(file_in_tar_bytes.getvalue())


def download_file_from_url(file_url, file_dir):
    response = requests.get(file_url)
    filename = urlparse(file_url).path.split("/")[-1]
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    with open(f"{file_dir}/{filename}", 'wb') as asset_file:
        asset_file.write(response.content)
    return filename


def convert_zip_file_to_tar_bytes(file_dir, filename):
    with ZipFile(f"{file_dir}/{filename}", 'r') as zipObj:
        listOfFileNames = zipObj.namelist()
        zipObj.extractall(file_dir, listOfFileNames)
    if not os.path.isdir(file_dir):
        raise Exception("Directory %s doesn't exists" % file_dir)
    files = glob.glob(os.path.join(file_dir, "*.proto"))
    if len(files) == 0:
        raise Exception("Cannot find any %s files" % (os.path.join(file_dir, "*.proto")))
    files.sort()
    tar_bytes = io.BytesIO()
    tar = tarfile.open(fileobj=tar_bytes, mode="w")
    for f in files:
        tar.add(f, os.path.basename(f))
    tar.close()
    return tar_bytes


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
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_path)


def zip_file(source_path, zipped_path):
    shutil.make_archive(zipped_path, 'zip', source_path)


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def validate_signature(signature, message, key, opt_params):
    derived_signature = opt_params.get("slack_signature_prefix", "") \
                        + hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(derived_signature, signature)
