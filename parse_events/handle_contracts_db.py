import base64
from datetime import datetime as dt

from common.constant import EVNTS_LIMIT
from common.repository import Repository
from common.utils import Utils

class HandleContractsDB:
    def __init__(self, err_obj, net_id):
        self.err_obj = err_obj
        self.repo = Repository(net_id)
        self.util_obj = Utils()

    # read operations
    def read_registry_events(self):
        query = 'select * from registry_events_raw where processed = 0 order by block_no asc limit ' + EVNTS_LIMIT
        evts_dta = self.repo.execute(query)
        print('read_registry_events::read_count: ', len(evts_dta))
        return evts_dta

    def read_mpe_events(self):
        query = 'select * from mpe_events_raw where processed = 0 order by block_no asc limit ' + EVNTS_LIMIT
        evts_dta = self.repo.execute(query)
        print('read_mpe_events::read_count: ', len(evts_dta))
        return evts_dta

    def _get_srvc_row_id(self, org_id, service_id):
        print('get_srvc_row_id::service_id: ', service_id)
        query = 'SELECT row_id FROM service WHERE service_id = %s AND org_id = %s '
        srvc_data = self.repo.execute(query, [service_id, org_id])
        print('get_srvc_row_id::srvc_data: ', srvc_data)
        return srvc_data

    def _get_srvcs(self, org_id):
        query = 'SELECT * FROM service WHERE org_id = %s '
        srvc_data = self.repo.execute(query, (org_id))
        print('_get_srvcs::srvc_data: ', srvc_data)
        return srvc_data

    # write operations
    def _create_or_updt_org(self, org_id, org_data, conn):
        upsert_qry = "Insert into organization (org_id, organization_name, owner_address, row_updated, row_created) " \
                     "VALUES ( %s, %s, %s, %s, %s ) " \
                     "ON DUPLICATE KEY UPDATE organization_name = %s, owner_address = %s, row_updated = %s  "
        upsert_params = [org_id, org_data[2], org_data[3], dt.utcnow(), dt.utcnow(), org_data[2], org_data[3],
                         dt.utcnow()]
        print('upsert_qry: ', upsert_qry)
        qry_resp = conn.execute(upsert_qry, upsert_params)
        print('_create_or_updt_org::row upserted: ', qry_resp)

    def _create_or_updt_members(self, org_id, members, conn):
        upsrt_members = "INSERT INTO members (org_id, member, row_created, row_updated)" \
                        "VALUES ( %s, %s, %s, %s )" \
                        "ON DUPLICATE KEY UPDATE row_updated = %s "
        cnt = 0
        for member in members:
            upsrt_members_params = [org_id, member, dt.utcnow(), dt.utcnow(), dt.utcnow()]
            qry_res = conn.execute(upsrt_members, upsrt_members_params)
            cnt = cnt + qry_res[0]
        print('create_or_updt_members::row upserted', cnt)

    def _create_channel(self, q_dta, conn):
        upsrt_mpe_chnl = "INSERT INTO mpe_channel (channel_id, sender, recipient, groupId, balance_in_cogs, pending, nonce, " \
                         "expiration, signer, row_created, row_updated) " \
                         "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
                         "ON DUPLICATE KEY UPDATE balance_in_cogs = %s, pending = %s, nonce = %s, " \
                         "expiration = %s, row_updated = %s"
        upsrt_mpe_chnl_params = [q_dta['channelId'], q_dta['sender'], q_dta['recipient'], q_dta['groupId'],
                                 q_dta['amount'], 0.0, q_dta['nonce'], q_dta['expiration'], q_dta['signer'], dt.utcnow(),
                                 dt.utcnow(), q_dta['amount'], 0.0, q_dta['nonce'], q_dta['expiration'], dt.utcnow()]
        qry_res = conn.execute(upsrt_mpe_chnl, upsrt_mpe_chnl_params)
        print('_create_channel::row upserted', qry_res)

    def _del_srvc(self, org_id, service_id, conn):
        del_srvc = 'DELETE FROM service WHERE service_id = %s AND org_id = %s '
        qry_res = conn.execute(del_srvc, [org_id, service_id])
        print('_del_srvc::rows deleted: ', qry_res)

    def _del_org(self, org_id, conn):
        del_org = 'DELETE FROM organization WHERE org_id = %s '
        qry_res = conn.execute(del_org, org_id)
        print('_del_org::rows deleted: ', qry_res)

    def _del_members(self, org_id, conn):
        del_org = 'DELETE FROM members WHERE org_id = %s '
        qry_res = conn.execute(del_org, org_id)
        print('_del_members::rows deleted: ', qry_res)

    def _del_tags(self, org_id, service_id, conn):
        del_srvc_tags = 'DELETE FROM service_tags WHERE service_id = %s AND org_id = %s '
        del_srvc_tags_count = conn.execute(del_srvc_tags, [service_id, org_id])
        print('_del_tags::del_srvc_tags: ', del_srvc_tags_count)

    def _del_srvc_dpndts(self, org_id, service_id, conn):
        print("_del_srvc_dpndts::service_id: ", service_id, '|org_id: ', org_id)
        del_srvc_grps = 'DELETE FROM service_group WHERE service_id = %s AND org_id = %s '
        del_srvc_grps_count = conn.execute(del_srvc_grps, [service_id, org_id])

        del_srvc_endpts = 'DELETE FROM service_endpoint WHERE service_id = %s AND org_id = %s '
        del_srvc_endpts_count = conn.execute(del_srvc_endpts, [service_id, org_id])

        self._del_tags(org_id=org_id, service_id=service_id, conn=conn)
        print('_del_srvc_dpndts::del_srvc_grps', del_srvc_grps_count, 'del_srvc_endpts', del_srvc_endpts_count)

    def _create_or_updt_srvc(self, org_id, service_id, ipfs_hash, conn):
        upsrt_srvc = "INSERT INTO service (org_id, service_id, is_curated, ipfs_hash, row_created, row_updated) " \
                     "VALUES (%s, %s, %s, %s, %s, %s) " \
                     "ON DUPLICATE KEY UPDATE ipfs_hash = %s, row_updated = %s "
        upsrt_srvc_params = [org_id, service_id, 0, ipfs_hash, dt.utcnow(), dt.utcnow(), ipfs_hash, dt.utcnow()]
        qry_res = conn.execute(upsrt_srvc, upsrt_srvc_params)
        print('_create_or_updt_srvc::row upserted', qry_res)
        return qry_res[len(qry_res) - 1]

    def _create_or_updt_srvc_mdata(self, srvc_rw_id, org_id, service_id, ipfs_data, conn):
        upsrt_srvc_mdata = "INSERT INTO service_metadata (service_row_id, org_id, service_id, price_model, " \
                           "price_in_cogs, display_name, model_ipfs_hash, description, url, json, encoding, type, " \
                           "mpe_address, row_updated, row_created) " \
                           "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
                           "ON DUPLICATE KEY UPDATE service_row_id = %s, price_model  = %s, price_in_cogs = %s, " \
                           "display_name = %s, model_ipfs_hash = %s, description = %s, url = %s, json = %s, " \
                           "encoding = %s, type = %s, mpe_address = %s, row_updated = %s "
        price = ipfs_data['pricing']
        price_model = price.get('price_model', '')
        price_in_cogs = price.get('price_in_cogs', '')
        desc = ipfs_data.get('description', '')
        url = ipfs_data.get('url', '')
        json_str = ipfs_data.get('json', '')
        upsrt_srvc_mdata_params = [srvc_rw_id, org_id, service_id, price_model, price_in_cogs, ipfs_data['display_name'],
                                   ipfs_data['model_ipfs_hash'], desc, url, json_str, ipfs_data['encoding'],
                                   ipfs_data['service_type'], ipfs_data['mpe_address'], dt.utcnow(), dt.utcnow(),
                                   srvc_rw_id, price_model, price_in_cogs, ipfs_data['display_name'],
                                   ipfs_data['model_ipfs_hash'],desc, url, json_str, ipfs_data['encoding'],
                                   ipfs_data['service_type'], ipfs_data['mpe_address'], dt.utcnow()]

        qry_res = conn.execute(upsrt_srvc_mdata, upsrt_srvc_mdata_params)
        print('_create_or_updt_srvc_mdata::row upserted', qry_res)

    def _create_grp(self, srvc_rw_id, org_id, service_id, grp_data, conn):
        insrt_grp = "INSERT INTO service_group (service_row_id, org_id, service_id, group_id, group_name, " \
                    "payment_address, row_updated, row_created)" \
                    "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        insrt_grp_params = [srvc_rw_id, org_id, service_id, grp_data['group_id'], grp_data['group_name'],
                            grp_data['payment_address'], dt.utcnow(), dt.utcnow()]

        return conn.execute(insrt_grp, insrt_grp_params)

    def _create_edpts(self, srvc_rw_id, org_id, service_id, endpt_data, conn):
        insrt_endpt = "INSERT INTO service_endpoint (service_row_id, org_id, service_id, group_id, endpoint, " \
                      "row_created, row_updated) " \
                      "VALUES(%s, %s, %s, %s, %s, %s, %s)"
        insrt_endpt_params = [srvc_rw_id, org_id, service_id, endpt_data['group_id'], endpt_data['endpoint'],
                              dt.utcnow(), dt.utcnow()]
        return conn.execute(insrt_endpt, insrt_endpt_params)

    def _create_tags(self, srvc_rw_id, org_id, service_id, tag_name, conn):
        insrt_tag = "INSERT INTO service_tags (service_row_id, org_id, service_id, tag_name, row_created, row_updated) " \
                    "VALUES(%s, %s, %s, %s, %s, %s)"
        insrt_tag_params = [srvc_rw_id, org_id, service_id, tag_name, dt.utcnow(), dt.utcnow()]
        qry_res = conn.execute(insrt_tag, insrt_tag_params)

    def _updt_raw_evts(self, row_id, type, err_cd, err_msg, conn):
        try:
            if type == 'REG':
                updt_evts = 'UPDATE registry_events_raw SET processed = 1, error_code = %s, error_msg = %s WHERE row_id = %s '
            elif type == 'MPE':
                updt_evts = 'UPDATE mpe_events_raw SET processed = 1, error_code = %s, error_msg = %s WHERE row_id = %s '
            updt_evts_resp = self.repo.execute(updt_evts, [err_cd, err_msg, row_id])
            print('updt_raw_evts::row updated: ', updt_evts_resp, '|', type)
        except Exception as e:
            self.util_obj.report_slack(type=1, slack_msg=repr(e))
            print('Error in updt_reg_evts_raw::error: ', e)

    def updt_raw_evts(self, row_id, type, err_cd, err_msg):
        conn = self.repo
        self._updt_raw_evts(row_id, type, err_cd, err_msg, conn)

    def del_org(self, org_id):
        self.repo.auto_commit = False
        conn = self.repo
        try:
            self._del_org(org_id=org_id, conn=conn)
            srvcs = self._get_srvcs(org_id=org_id)
            for rec in srvcs:
                self._del_srvc(org_id=org_id, service_id=rec['service_id'], conn=conn)
            self._commit(conn=conn)
        except Exception as e:
            self.util_obj.report_slack(type=1, slack_msg=repr(e))
            self._rollback(conn=conn, err=repr(e))

    def del_srvc(self, org_id, service_id):
        self._del_srvc(org_id=org_id, service_id=service_id, conn=self.repo)

    def create_channel(self, q_dta):
        q_dta['groupId'] = base64.b64encode(bytes.fromhex(q_dta['groupId'].lstrip('0x'))).decode('utf8')
        self._create_channel(q_dta, self.repo)

    def update_channel(self, channel_id, group_id, channel_data):
        print('update_channel::channel_id: ', channel_id)
        self._create_channel(q_dta={
            'sender': channel_data[1],
            'recipient': channel_data[3],
            'nonce': int(channel_data[0]),
            'expiration': channel_data[6],
            'signer': channel_data[2],
            'groupId': group_id,
            'channelId': channel_id,
            'amount': channel_data[5]
        }, conn=self.repo)

    def process_srvc_data(self, org_id, service_id, ipfs_hash, ipfs_data):
        self.repo.auto_commit = False
        conn = self.repo
        try:
            self._del_srvc_dpndts(org_id=org_id, service_id=service_id, conn=conn)
            qry_data = self._create_or_updt_srvc(org_id=org_id, service_id=service_id, ipfs_hash=ipfs_hash, conn=conn)
            service_row_id = qry_data['last_row_id']
            print('service_row_id == ', service_row_id)
            self._create_or_updt_srvc_mdata(srvc_rw_id=service_row_id, org_id=org_id, service_id=service_id,
                                            ipfs_data=ipfs_data, conn=conn)
            grps = ipfs_data.get('groups', [])
            cnt = 0
            grp_name_id_dict = {}
            for grp in grps:
                grp_name_id_dict[grp['group_name']] = grp['group_id']
                qry_data = self._create_grp(srvc_rw_id=service_row_id, org_id=org_id, service_id=service_id, conn=conn,
                                            grp_data={
                                                'group_id': grp['group_id'],
                                                'group_name': grp['group_name'],
                                                'payment_address': grp['payment_address']
                                            })
                cnt = cnt + qry_data[0]
            print('rows insert in grp: ', cnt)

            endpts = ipfs_data.get('endpoints', [])
            cnt = 0
            for endpt in endpts:
                qry_data = self._create_edpts(srvc_rw_id=service_row_id, org_id=org_id, service_id=service_id,
                                              conn=conn,
                                              endpt_data={
                                                  'endpoint': endpt['endpoint'],
                                                  'group_id': grp_name_id_dict[endpt['group_name']]
                                              })
                cnt = cnt + qry_data[0]
            print('rows insert in endpt: ', cnt)

            tags = ipfs_data.get('tags', [])
            print('tags==', tags)
            for tag in tags:
                self._create_tags(service_row_id=service_row_id, org_id=org_id, service_id=service_id, tag_name=tag,
                                  conn=conn)
            self._commit(conn=conn)
        except Exception as e:
            self.util_obj.report_slack(type=1, slack_msg=repr(e))
            self._rollback(conn=conn, err=repr(e))

    def process_org_data(self, org_id, org_data):
        self.repo.auto_commit = False
        conn = self.repo
        try:

            if (org_data is not None and org_data[0]):
                self._create_or_updt_org(org_id, org_data, conn)
                self._del_members(org_id=org_id, conn=conn)
                self._create_or_updt_members(org_id, org_data[4], conn)
                self._commit(conn)
        except Exception as e:
            self.util_obj.report_slack(type=1, slack_msg=repr(e))
            self._rollback(conn=conn, err=repr(e))

    def update_tags(self, org_id, service_id, tags_data):
        self.repo.auto_commit = False
        conn = self.repo
        try:
            if (tags_data is not None and tags_data[0]):
                tags = tags_data[3]
                srvc_data = self._get_srvc_row_id(service_id=service_id, org_id=org_id)
                srvc_rw_id = srvc_data[0]['row_id']
                for tag in tags:
                    tag = tag.decode("utf-8")
                    print('tag===',tag)
                    self._create_tags(srvc_rw_id=srvc_rw_id, org_id=org_id, service_id=service_id, tag_name=tag,
                                      conn=conn)
                self._commit(conn)
        except Exception as e:
            self.util_obj.report_slack(type=1, slack_msg=repr(e))
            self._rollback(conn=conn, err=repr(e))

    #
    def _commit(self, conn):
        conn.auto_commit = True
        conn.connection.commit()
        print('_commit')
        print(conn.connection)

    def _rollback(self, conn, err):
        print('_rollback ::error: ', err)
        conn.auto_commit = True
        conn.connection.rollback()
