import datetime
import decimal
import json

import requests
import web3
from web3 import Web3

IGNORED_LIST = ["row_id", "row_created", "row_updated"]


class Utils:
    def __init__(self):
        self.msg_type = {0: "info:: ", 1: "err:: "}

    def report_slack(self, type, slack_msg, SLACK_HOOK):
        url = SLACK_HOOK["hostname"] + SLACK_HOOK["path"]
        prefix = self.msg_type.get(type, "")
        print(url)
        payload = {
            "channel": "#contract-index-alerts",
            "username": "webhookbot",
            "text": prefix + slack_msg,
            "icon_emoji": ":ghost:",
        }

        resp = requests.post(url=url, data=json.dumps(payload))
        print(resp.status_code, resp.text)

    def clean(self, value_list):
        for value in value_list:
            self.clean_row(value)

    def clean_row(self, row):
        for item in IGNORED_LIST:
            del row[item]

        for key in row:
            if isinstance(row[key], decimal.Decimal) or isinstance(
                    row[key], datetime.datetime):
                row[key] = str(row[key])
            elif isinstance(row[key], bytes):
                if row[key] == b"\x01":
                    row[key] = 1
                elif row[key] == b"\x00":
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


def make_response(status_code, body, header=None):
    return {"statusCode": status_code, "headers": header, "body": body}


def validate_request(required_keys, request_body):
    for key in required_keys:
        if key not in request_body:
            return False
    return True


def generate_lambda_response(status_code, message):
    return {
        "statusCode": status_code,
        "body": json.dumps(message),
        "headers": {
            "Content-Type": "application/json",
            "X-Requested-With": "*",
            "Access-Control-Allow-Headers":
            "Access-Control-Allow-Origin, Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS,POST",
        },
    }


def extract_payload(method, event):
    method_found = True
    payload_dict = None
    if method == "POST":
        payload_dict = json.loads(event["body"])
    elif method == "GET":
        payload_dict = event.get("queryStringParameters", {})
    else:
        method_found = False
    return method_found, payload_dict


def validate_dict(event, required_keys):
    valid = True
    for key in required_keys:
        if key not in event:
            valid = False
    return valid


def format_error_message(status, error, resource, payload, net_id):
    return json.dumps({
        "status": status,
        "error": error,
        "resource": resource,
        "payload": payload,
        "network_id": net_id,
    })
