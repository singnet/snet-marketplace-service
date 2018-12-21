import re
from datetime import datetime

import requests

from repository import Repository


class ServiceStatus:
    def __init__(self, repo):
        self.repo = repo
        self.route = '/encoding'
        self.rex_for_pb_ip = '^192.|^172.|^10.'

    def ping_url(self, url):
        srch_count = re.subn(self.rex_for_pb_ip, '', url)[1]
        if srch_count == 0:
            if url[:4].lower() != 'http':
                url = 'http://' + url
            url = url + self.route
            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    return 1
            except Exception as err:
                print("Error {}".format(err))
        return 0

    def update_service_status(self):
        # new services
        endpt_insert_params = []
        query = 'SELECT S.row_id, G.group_id, E.endpoint FROM service S, service_group G, service_endpoint E ' \
                'WHERE S.row_id = G.service_id AND G.group_name = E.group_name AND S.row_id = E.service_id ' \
                'AND (S.row_id, G.group_id, E.endpoint) NOT IN (SELECT DISTINCT service_id, group_id, endpoint FROM service_status) LIMIT 5 '
        result = self.repo.execute(query)
        if result == None:
            result = []
        rowcount = len(result)
        print('ServiceStatus::insertion_count = ', rowcount)
        for rec in result:
            endpt_insert_params.append(
                [rec['row_id'], rec['group_id'], rec['endpoint'], self.ping_url(rec['endpoint']), datetime.utcnow(),
                 datetime.utcnow()])
        insert_qry = "Insert into service_status (service_id,group_id,endpoint,is_available, last_check_timestamp, row_created) values (%s, %s , %s, %s, %s, %s)"
        rows_insrtd = self.repo.bulk_query(insert_qry, endpt_insert_params)
        print('no of rows inserted: ', rows_insrtd)
        if rowcount < 5:
            limit = 5 - rowcount;
            query = 'SELECT T.row_id, E.endpoint FROM service S, service_status T, service_endpoint E, service_group G ' \
                    'WHERE S.row_id = G.service_id AND G.group_name = E.group_name AND T.service_id = E.service_id AND T.group_id = G.group_id ' \
                    'AND E.endpoint = T.endpoint AND S.row_id = E.service_id AND E.endpoint not regexp %s  ORDER BY T.last_check_timestamp ASC LIMIT %s'
            result = self.repo.execute(query, [self.rex_for_pb_ip, limit])
            if result == None:
                result = []
            rowcount = len(result)
            print('ServiceStatus::update_count = ', rowcount)
            rows_updtd = 0
            updt_qry = 'UPDATE service_status SET is_available = %s, last_check_timestamp = current_timestamp WHERE row_id = %s '
            for rec in result:
                res = self.repo.execute(updt_qry, [self.ping_url(rec['endpoint']), rec['row_id']])
                rows_updtd = rows_updtd + res[0]
            print('no of rows updated: ', rows_updtd)

