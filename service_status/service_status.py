import re
from datetime import datetime

import grpc
from grpc_health.v1 import health_pb2 as heartb_pb2
from grpc_health.v1 import health_pb2_grpc as heartb_pb2_grpc

from common.utils import Utils
from service_status.constant import LIMIT
from service_status.constant import SRVC_STATUS_GRPC_TIMEOUT


class ServiceStatus:
    def __init__(self, repo, net_id):
        self.repo = repo
        self.route = "/encoding"
        self.rex_for_pb_ip = "^(http://)*(https://)*127.0.0.1|^(http://)*(https://)*localhost|^(http://)*(https://)*192.|^(http://)*(https://)*172.|^(http://)*(https://)*10."
        self.obj_util = Utils()
        self.net_id = net_id

    def _check_service_status(self, url, secure=True):
        try:
            if secure:
                channel = grpc.secure_channel(url, grpc.ssl_channel_credentials())
            else:
                channel = grpc.insecure_channel(url)

            stub = heartb_pb2_grpc.HealthStub(channel)
            response = stub.Check(
                heartb_pb2.HealthCheckRequest(service=""),
                timeout=SRVC_STATUS_GRPC_TIMEOUT,
            )
            if response != None and response.status == 1:
                print(response.status)
                return 1
            return 0
        except Exception as e:
            print("error in making grpc call::url: ", url, "|err: ", e)
            return 0

    def ping_url(self, url):
        srch_count = re.subn(self.rex_for_pb_ip, "", url)[1]
        if srch_count == 0:
            secure = True
            if url[:4].lower() == "http" and url[:5].lower() != "https":
                secure = False
            url = self.obj_util.remove_http_https_prefix(url=url)
            return self._check_service_status(url=url, secure=secure)
        return 0

    def update_service_status(self):
        try:
            query = "SELECT row_id, endpoint FROM service_endpoint WHERE endpoint not regexp %s ORDER BY last_check_timestamp ASC LIMIT %s"
            print("query: ", query)
            result = self.repo.execute(query, [self.rex_for_pb_ip, LIMIT])
            if result == None or result == []:
                raise Exception("Unable to find services.")

            update_query = "UPDATE service_endpoint SET is_available = %s, last_check_timestamp = current_timestamp WHERE row_id = %s "
            print("query: ", update_query)
            for rec in result:
                res = self.repo.execute(
                    update_query, [self.ping_url(rec["endpoint"]), rec["row_id"]]
                )
            rows_updated = rows_updated + res[0]
            print("no of rows updated: ", rows_updated)
        except Exception as e:
            print("Error in update_service_status:: ", e)
            return 0
