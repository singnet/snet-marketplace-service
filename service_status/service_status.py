import re
from datetime import datetime
from common.utils import Utils
from service_status.state_service_pb2_grpc import PaymentChannelStateServiceStub
from service_status.state_service_pb2 import ChannelStateRequest
import grpc


class ServiceStatus:
    def __init__(self, repo, net_id):
        self.repo = repo
        self.route = '/encoding'
        self.rex_for_pb_ip = '^(http://)*(https://)*127.0.0.1|^(http://)*(https://)*localhost|^(http://)*(https://)*192.|^(http://)*(https://)*172.|^(http://)*(https://)*10.'
        self.obj_util = Utils()
        self.net_id = net_id

    def _make_grpc_call(self, url, secure=1):
        channel = None
        try:
            if secure==1:
                channel = grpc.secure_channel(url, grpc.ssl_channel_credentials())
            else:
                channel = grpc.insecure_channel(url)

            stub = PaymentChannelStateServiceStub(channel)
            try:
                response = stub.GetChannelState(ChannelStateRequest())
            except grpc.RpcError as err:
                err_code = str(err.code())
                print(err_code)
                if err_code == "StatusCode.UNAVAILABLE":
                    return 0
                return 1
            return 1
        except Exception as e:
            print("error in making grpc call::url: ", url, "|err: ", e)
            return 0

    def ping_url(self, url):
        srch_count = re.subn(self.rex_for_pb_ip, '', url)[1]
        if srch_count == 0:
            secure = 1
            if url[:4].lower() == 'http' and url[:5].lower() != 'https':
                secure = 0
            url = self.obj_util.remove_http_https_prefix(url=url)
            return self._make_grpc_call(url=url, secure=secure)
        return 0

    def update_service_status(self):
        # new services
        endpt_insert_params = []
        query = 'SELECT S.row_id, S.org_id, S.service_id, G.group_id, E.endpoint FROM service S, service_group G, service_endpoint E ' \
                'WHERE S.row_id = G.service_row_id AND G.group_id = E.group_id AND S.row_id = E.service_row_id ' \
                'AND (S.row_id, G.group_id, E.endpoint) NOT IN (SELECT DISTINCT service_row_id, group_id, endpoint FROM service_status) LIMIT 5 '
        print('query: ', query)
        result = self.repo.execute(query)
        if result == None:
            result = []
        rowcount = len(result)
        print('ServiceStatus::insertion_count = ', rowcount)
        for rec in result:
            endpt_insert_params.append(
                [rec['row_id'], rec['org_id'], rec['service_id'], rec['group_id'], rec['endpoint'],
                 self.ping_url(rec['endpoint']), datetime.utcnow(),
                 datetime.utcnow()])
        insert_qry = "Insert into service_status (service_row_id, org_id, service_id, group_id,endpoint,is_available, last_check_timestamp, row_created) values (%s, %s , %s, %s, %s, %s, %s, %s)"
        print('insert_qry: ', insert_qry)
        rows_insrtd = self.repo.bulk_query(insert_qry, endpt_insert_params)
        print('no of rows inserted: ', rows_insrtd)
        if rowcount < 5:
            limit = 5 - rowcount;
            query = 'SELECT T.row_id, E.endpoint FROM service S, service_status T, service_endpoint E, service_group G ' \
                    'WHERE S.row_id = G.service_row_id AND G.group_id = E.group_id AND T.service_row_id = E.service_row_id AND T.group_id = G.group_id ' \
                    'AND E.endpoint = T.endpoint AND S.row_id = E.service_row_id AND E.endpoint not regexp %s  ORDER BY T.last_check_timestamp ASC LIMIT %s'
            print('query: ', query)
            result = self.repo.execute(query, [self.rex_for_pb_ip, limit])
            if result == None:
                result = []
            rowcount = len(result)
            print('ServiceStatus::update_count = ', rowcount)
            rows_updtd = 0
            updt_qry = 'UPDATE service_status SET is_available = %s, last_check_timestamp = current_timestamp WHERE row_id = %s '
            print('query: ', updt_qry)
            for rec in result:
                res = self.repo.execute(updt_qry, [self.ping_url(rec['endpoint']), rec['row_id']])
                rows_updtd = rows_updtd + res[0]
            print('no of rows updated: ', rows_updtd)