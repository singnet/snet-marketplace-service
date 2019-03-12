import json
import datetime
import decimal
import requests

from common.constant import SLACK_HOOK
IGNORED_LIST = ['row_id', 'row_created', 'row_updated']

class Utils:
    def __init__(self):
        self.msg_type = {
            0 : 'info:: ',
            1 : 'err:: '
        }

    def report_slack(self, type, slack_msg):
        url = SLACK_HOOK['hostname'] + SLACK_HOOK['path']
        prefix = self.msg_type.get(type, "")
        print(url)
        payload = {"channel": "#contract-index-alerts",
                   "username": "webhookbot",
                   "text": prefix + slack_msg,
                   "icon_emoji": ":ghost:"
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
            if isinstance(row[key], decimal.Decimal) or isinstance(row[key], datetime.datetime):
                row[key] = str(row[key])
            elif isinstance(row[key], bytes):
                if row[key] == b'\x01':
                    row[key] = 1
                elif row[key] == b'\x00':
                    row[key] = 0
                else:
                    raise Exception("Unsupported bytes object. Key " + str(key) + " value " + str(row[key]))

        return row

    def remove_http_https_prefix(self, url):
        url = url.replace("https://","")
        url = url.replace("http://","")
        return url
