import json

import requests

from common.constant import SLACK_HOOK


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
