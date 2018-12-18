from datetime import datetime

import requests
import re

from repository import Repository


class ServiceStatus:
    def __init__(self, repo):
        self.repo = repo
        self.route = '/encoding'
        self.rex_for_pb_ip = '^192.|^172.|^10.'

    def ping_url(self, url):
        srch_count = re.subn(self.rex_for_pb_ip,'',url)[1]
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
        endpt_updt_params = []
        query = 'SELECT S.row_id, G.group_id, E.endpoint FROM service S, service_group G, service_endpoint E ' \
                'WHERE S.row_id = G.service_id AND G.group_name = E.group_name AND S.row_id = E.service_id ' \
                'AND (S.row_id, G.group_id, E.endpoint) NOT IN (SELECT DISTINCT service_id, group_id, endpoint FROM service_status) LIMIT 5 '
        result = self.repo.execute(query)
        if result == None:
            result = []
        rowcount = len(result)
        print('for insertion: rowcount = ', rowcount)
        print(len(result))
        for rec in result:
            endpt_insert_params.append([rec['row_id'], rec['group_id'], rec['endpoint'], self.ping_url(rec['endpoint']), datetime.utcnow(), datetime.utcnow()])
        insert_qry = "Insert into service_status (service_id,group_id,endpoint,is_available, last_check_timestamp, row_created) values (%s, %s , %s, %s, %s, %s)"
        self.repo.bulk_query(insert_qry,endpt_insert_params)
        if rowcount < 5:
            limit = 5 - rowcount;
            query = 'SELECT T.row_id, G.group_id, E.endpoint FROM service S, service_status T, service_endpoint E, service_group G ' \
                    'WHERE S.row_id = G.service_id AND G.group_name = E.group_name AND T.service_id = E.service_id AND T.group_id = G.group_id ' \
                    'AND E.endpoint = T.endpoint AND S.row_id = E.service_id AND E.endpoint not regexp %s  ORDER BY T.row_updated ASC LIMIT %s'
            result = self.repo.execute(query, [self.rex_for_pb_ip, limit])
            if result == None:
                result = []
            rowcount = len(result)
            print('for updation: rowcount = ', rowcount)
            for rec in result:
                endpt_updt_params.append([self.ping_url(rec['endpoint']), rec['row_id'], rec['group_id'], rec['endpoint']])
            updt_qry = 'UPDATE service_status SET is_available = %s WHERE service_id = %s AND group_id = %s AND endpoint = %s '
            self.repo.bulk_query(updt_qry, endpt_updt_params)

