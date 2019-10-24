import base64
import json
import logging
from datetime import datetime as dt

import log_setup

from parse_events.constant import EVNTS_LIMIT
from parse_events.config import NETWORKS, IPFS_URL, ASSETS_BUCKET_NAME, S3_BUCKET_ACCESS_KEY, S3_BUCKET_SECRET_KEY, ASSETS_PREFIX, SLACK_HOOK
from common.ipfs_util import IPFSUtil
from common.repository import Repository
from common.s3_util import S3Util

from common.utils import Utils
from repository.service_metadata_repository import ServiceMetadataRepository

logger = logging.getLogger()
log_setup.configure_log(logger)


class HandleContractsDB:
    def __init__(self, err_obj, net_id):
        self.err_obj = err_obj
        self.repo = Repository(net_id, NETWORKS)
        self.util_obj = Utils()
        self.ipfs_utll = IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
        self.s3_util = S3Util(S3_BUCKET_ACCESS_KEY, S3_BUCKET_SECRET_KEY)

    def get_servic_row_id(self, org_id, service_id):
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
    def _create_or_updt_org(self, org_id, org_name, owner_address, org_metadata_uri, conn):
        upsert_qry = "Insert into organization (org_id, organization_name, owner_address, org_metadata_uri, row_updated, row_created) " \
                     "VALUES ( %s, %s, %s, %s, %s , %s) " \
                     "ON DUPLICATE KEY UPDATE organization_name = %s, owner_address = %s, org_metadata_uri = %s, row_updated = %s  "
        upsert_params = [org_id, org_name, owner_address, org_metadata_uri, dt.utcnow(), dt.utcnow(), org_name, owner_address, org_metadata_uri,
                         dt.utcnow()]
        print('upsert_qry: ', upsert_qry)
        qry_resp = conn.execute(upsert_qry, upsert_params)
        print('_create_or_updt_org::row upserted: ', qry_resp)

    def _del_org_groups(self, org_id, conn):
        delete_query = conn.execute(
            "DELETE FROM org_group WHERE org_id = %s ", [org_id])

    def _create_org_groups(self, org_id, groups, conn):
        insert_qry = "Insert into org_group (org_id, group_id, group_name, payment, row_updated, row_created) " \
                     "VALUES ( %s, %s, %s, %s, %s, %s ) "
        cnt = 0
        for group in groups:
            insert_params = [org_id, group['group_id'], group['group_name'], json.dumps(
                group['payment']), dt.utcnow(), dt.utcnow()]
            qry_res = conn.execute(insert_qry, insert_params)
            cnt = cnt + qry_res[0]
        print('_create_org_groups::row inserted', cnt)

    def _create_or_updt_members(self, org_id, members, conn):
        upsrt_members = "INSERT INTO members (org_id, member, row_created, row_updated)" \
                        "VALUES ( %s, %s, %s, %s )" \
                        "VALUES ( %s, %s, %s, %s )" \
                        "ON DUPLICATE KEY UPDATE row_updated = %s "
        cnt = 0
        for member in members:
            upsrt_members_params = [org_id, member,
                                    dt.utcnow(), dt.utcnow(), dt.utcnow()]
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
                                 q_dta['amount'], 0.0, q_dta['nonce'], q_dta['expiration'], q_dta['signer'], dt.utcnow(
        ),
            dt.utcnow(), q_dta['amount'], 0.0, q_dta['nonce'], q_dta['expiration'], dt.utcnow()]
        qry_res = conn.execute(upsrt_mpe_chnl, upsrt_mpe_chnl_params)
        print('_create_channel::row upserted', qry_res)

    def _del_srvc(self, org_id, service_id, conn):
        del_srvc = 'DELETE FROM service WHERE service_id = %s AND org_id = %s '
        qry_res = conn.execute(del_srvc, [service_id, org_id])
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
        print("_del_srvc_dpndts::service_id: ",
              service_id, '|org_id: ', org_id)
        del_srvc_grps = 'DELETE FROM service_group WHERE service_id = %s AND org_id = %s '
        del_srvc_grps_count = conn.execute(del_srvc_grps, [service_id, org_id])

        del_srvc_endpts = 'DELETE FROM service_endpoint WHERE service_id = %s AND org_id = %s '
        del_srvc_endpts_count = conn.execute(
            del_srvc_endpts, [service_id, org_id])

        self._del_tags(org_id=org_id, service_id=service_id, conn=conn)
        print('_del_srvc_dpndts::del_srvc_grps: ', del_srvc_grps_count,
              '|del_srvc_endpts: ', del_srvc_endpts_count)

    def _create_or_updt_srvc(self, org_id, service_id, ipfs_hash, conn):
        upsrt_srvc = "INSERT INTO service (org_id, service_id, is_curated, ipfs_hash, row_created, row_updated) " \
                     "VALUES (%s, %s, %s, %s, %s, %s) " \
                     "ON DUPLICATE KEY UPDATE ipfs_hash = %s, row_updated = %s "
        upsrt_srvc_params = [org_id, service_id, 0, ipfs_hash,
                             dt.utcnow(), dt.utcnow(), ipfs_hash, dt.utcnow()]
        qry_res = conn.execute(upsrt_srvc, upsrt_srvc_params)
        print('_create_or_updt_srvc::row upserted', qry_res)
        return qry_res[len(qry_res) - 1]

    def _create_or_updt_srvc_mdata(self, srvc_rw_id, org_id, service_id, ipfs_data, assets_url, conn):
        upsrt_srvc_mdata = "INSERT INTO service_metadata (service_row_id, org_id, service_id, " \
                           "display_name, model_ipfs_hash, description, url, json, encoding, type, " \
                           "mpe_address, assets_hash , assets_url, service_rating, row_updated, row_created) " \
                           "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) " \
                           "ON DUPLICATE KEY UPDATE service_row_id = %s, " \
                           "display_name = %s, model_ipfs_hash = %s, description = %s, url = %s, json = %s, " \
                           "encoding = %s, type = %s, mpe_address = %s, row_updated = %s ,assets_hash = %s ,assets_url = %s"

        srvc_desc = ipfs_data.get('service_description', {})
        desc = srvc_desc.get('description', '')
        url = srvc_desc.get('url', '')
        json_str = ipfs_data.get('json', '')
        assets_hash = json.dumps(ipfs_data.get('assets', {}))
        assets_url_str = json.dumps(assets_url)
        upsrt_srvc_mdata_params = [srvc_rw_id, org_id, service_id, ipfs_data['display_name'],
                                   ipfs_data['model_ipfs_hash'], desc, url, json_str, ipfs_data['encoding'],
                                   ipfs_data['service_type'], ipfs_data['mpe_address'], assets_hash, assets_url_str, '{"rating": 0.0 , "total_users_rated": 0 }', dt.utcnow(
        ), dt.utcnow(),
            srvc_rw_id, ipfs_data['display_name'],
            ipfs_data['model_ipfs_hash'], desc, url, json_str, ipfs_data['encoding'],
            ipfs_data['service_type'], ipfs_data['mpe_address'], dt.utcnow(), assets_hash, assets_url_str]

        qry_res = conn.execute(upsrt_srvc_mdata, upsrt_srvc_mdata_params)
        print('_create_or_updt_srvc_mdata::row upserted', qry_res)

    def _create_grp(self, srvc_rw_id, org_id, service_id, grp_data, conn):
        insrt_grp = "INSERT INTO service_group (service_row_id, org_id, service_id, group_id, group_name," \
                    "pricing, row_updated, row_created)" \
                    "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        insrt_grp_params = [srvc_rw_id, org_id, service_id, grp_data['group_id'], grp_data['group_name'],
                            grp_data['pricing'], dt.utcnow(), dt.utcnow()]

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
                    "VALUES(%s, %s, %s, %s, %s, %s) " \
                    "ON DUPLICATE KEY UPDATE tag_name = %s, row_updated = %s "
        insrt_tag_params = [srvc_rw_id, org_id, service_id,
                            tag_name, dt.utcnow(), dt.utcnow(), tag_name, dt.utcnow()]
        qry_res = conn.execute(insrt_tag, insrt_tag_params)
        print('_create_tags::qry_res: ', qry_res)

    def _updt_raw_evts(self, row_id, type, err_cd, err_msg, conn):
        try:
            if type == 'REG':
                updt_evts = 'UPDATE registry_events_raw SET processed = 1, error_code = %s, error_msg = %s WHERE row_id = %s '
            elif type == 'MPE':
                updt_evts = 'UPDATE mpe_events_raw SET processed = 1, error_code = %s, error_msg = %s WHERE row_id = %s '
            updt_evts_resp = self.repo.execute(
                updt_evts, [err_cd, err_msg, row_id])
            print('updt_raw_evts::row updated: ', updt_evts_resp, '|', type)
        except Exception as e:
            self.util_obj.report_slack(
                type=1, slack_msg=repr(e), SLACK_HOOK=SLACK_HOOK)
            print('Error in updt_reg_evts_raw::error: ', e)

    def updt_raw_evts(self, row_id, type, err_cd, err_msg):
        conn = self.repo
        self._updt_raw_evts(row_id, type, err_cd, err_msg, conn)

    def del_org(self, org_id):
        self.repo.auto_commit = False
        conn = self.repo
        try:
            self._del_org(org_id=org_id, conn=conn)
            self._del_org_groups(org_id=org_id, conn=conn)
            srvcs = self._get_srvcs(org_id=org_id)
            for rec in srvcs:
                self._del_srvc(
                    org_id=org_id, service_id=rec['service_id'], conn=conn)
            self._commit(conn=conn)
        except Exception as e:
            self.util_obj.report_slack(
                type=1, slack_msg=repr(e), SLACK_HOOK=SLACK_HOOK)
            self._rollback(conn=conn, err=repr(e))

    def del_srvc(self, org_id, service_id):
        self._del_srvc(org_id=org_id, service_id=service_id, conn=self.repo)

    def create_channel(self, q_dta):
        if q_dta['groupId'][0:2] == '0x':
            q_dta['groupId'] = q_dta['groupId'][2:]
        q_dta['groupId'] = base64.b64encode(
            bytes.fromhex(q_dta['groupId'])).decode('utf8')
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

    def _push_asset_to_s3_using_hash(self, hash, org_id, service_id):
        io_bytes = self.ipfs_utll.read_bytesio_from_ipfs(hash)
        filename = hash.split("/")[1]
        new_url = self.s3_util.push_io_bytes_to_s3(ASSETS_PREFIX + "/" + org_id + "/" + service_id + "/" + filename, ASSETS_BUCKET_NAME,
                                                   io_bytes)
        return new_url

    def _comapre_assets_and_push_to_s3(self, existing_assets_hash, new_assets_hash, existing_assets_url, org_id,
                                       service_id):
        """

        :param existing_assets_hash: contains asset_type and its has value stored in ipfs
        :param new_assets_hash:  contains asset type and its updated hash value in ipfs
        :param existing_assets_url:  contains asset type and s3_url value for given asset_type
        :param org_id:
        :param service_id:
        :return: dict of asset_type and new_s3_url
        """
        # this function compare assets and deletes and update the new assets

        assets_url_mapping = {}

        if not existing_assets_hash:
            existing_assets_hash = {}
        if not existing_assets_url:
            existing_assets_url = {}
        if not new_assets_hash:
            new_assets_hash = {}

        for new_asset_type, new_asset_hash in new_assets_hash.items():

            if isinstance(new_asset_hash, list):
                # if this asset_type contains list of assets than remove all existing assetes from s3 and add all new assets to s3
                #
                new_urls_list = []

                # remove all existing assets if exits
                if new_asset_type in existing_assets_url:
                    for url in existing_assets_url[new_asset_type]:
                        self.s3_util.delete_file_from_s3(url)

                # add new files to s3 and update the url
                for hash in new_assets_hash[new_asset_type]:
                    new_urls_list.append(
                        self._push_asset_to_s3_using_hash(hash, org_id, service_id))

                assets_url_mapping[new_asset_type] = new_urls_list

            elif isinstance(new_asset_hash, str):
                # if this asset_type has single value
                if new_asset_type in existing_assets_hash and existing_assets_hash[new_asset_type] == new_asset_hash:
                    # file is not updated , add existing url
                    assets_url_mapping[new_asset_type] = existing_assets_url[new_asset_type]

                else:
                    if new_asset_type in existing_assets_url:
                        url_of_file_to_be_removed = existing_assets_url[new_asset_type]
                        self.s3_util.delete_file_from_s3(
                            url_of_file_to_be_removed)

                    hash_of_file_to_be_pushed_to_s3 = new_assets_hash[new_asset_type]

                    assets_url_mapping[new_asset_type] = self._push_asset_to_s3_using_hash(
                        hash_of_file_to_be_pushed_to_s3, org_id, service_id)

            else:
                logger.info(
                    "unknown type assets for org_id %s  service_id %s", org_id, service_id)

        return assets_url_mapping

    def _get_new_assets_url(self, org_id, service_id, new_ipfs_data):
        new_assets_hash = new_ipfs_data.get('assets', {})
        existing_assets_hash = {}
        existing_assets_url = {}

        service_metadata_repo = ServiceMetadataRepository()
        existing_service_metadata = service_metadata_repo.get_service_metatdata_by_servcie_id_and_org_id(
            service_id, org_id)

        if existing_service_metadata:
            existing_assets_hash = existing_service_metadata.assets_hash
            existing_assets_url = existing_service_metadata.assets_url
        assets_url_mapping = self._comapre_assets_and_push_to_s3(existing_assets_hash, new_assets_hash, existing_assets_url, org_id,
                                                                 service_id)
        return assets_url_mapping

    def process_srvc_data(self, org_id, service_id, ipfs_hash, ipfs_data, tags_data):
        self.repo.auto_commit = False
        conn = self.repo
        try:

            assets_url = self._get_new_assets_url(
                org_id, service_id, ipfs_data)

            self._del_srvc_dpndts(
                org_id=org_id, service_id=service_id, conn=conn)
            qry_data = self._create_or_updt_srvc(
                org_id=org_id, service_id=service_id, ipfs_hash=ipfs_hash, conn=conn)
            service_row_id = qry_data['last_row_id']
            print('service_row_id == ', service_row_id)
            self._create_or_updt_srvc_mdata(srvc_rw_id=service_row_id, org_id=org_id, service_id=service_id,
                                            ipfs_data=ipfs_data, assets_url=assets_url, conn=conn)
            grps = ipfs_data.get('groups', [])
            group_insert_count = 0
            for grp in grps:
                qry_data = self._create_grp(srvc_rw_id=service_row_id, org_id=org_id, service_id=service_id, conn=conn,
                                            grp_data={
                                                'group_id': grp['group_id'],
                                                'group_name': grp['group_name'],
                                                'pricing': json.dumps(grp['pricing'])
                                            })
                group_insert_count = group_insert_count + qry_data[0]
                endpts = grp.get('endpoints', [])
                endpt_insert_count = 0
                for endpt in endpts:
                    qry_data = self._create_edpts(srvc_rw_id=service_row_id, org_id=org_id, service_id=service_id,
                                                  conn=conn,
                                                  endpt_data={
                                                      'endpoint': endpt,
                                                      'group_id': grp['group_id'],
                                                  })
                    endpt_insert_count = endpt_insert_count + qry_data[0]
                print('rows insert in endpt: ', endpt_insert_count)
            print('rows insert in grp: ', group_insert_count)

            if (tags_data is not None and tags_data[0]):
                tags = tags_data[3]
                for tag in tags:
                    tag = tag.decode('utf-8')
                    tag = tag.rstrip("\u0000")
                    self._create_tags(srvc_rw_id=service_row_id, org_id=org_id, service_id=service_id, tag_name=tag,
                                      conn=conn)
            self._commit(conn=conn)

        except Exception as e:
            self.util_obj.report_slack(
                type=1, slack_msg=repr(e), SLACK_HOOK=SLACK_HOOK)
            self._rollback(conn=conn, err=repr(e))

    def process_org_data(self, org_id, org_data, ipfs_data, org_metadata_uri):
        self.repo.auto_commit = False
        conn = self.repo
        try:

            if (org_data is not None and org_data[0]):
                self._create_or_updt_org(
                    org_id=org_id, org_name=ipfs_data["org_name"], owner_address=org_data[3], org_metadata_uri=org_metadata_uri, conn=conn)
                self._del_org_groups(org_id=org_id, conn=conn)
                self._create_org_groups(
                    org_id=org_id, groups=ipfs_data["groups"], conn=conn)
                self._del_members(org_id=org_id, conn=conn)
                self._create_or_updt_members(org_id, org_data[4], conn)
                self._commit(conn)
        except Exception as e:
            self.util_obj.report_slack(
                type=1, slack_msg=repr(e), SLACK_HOOK=SLACK_HOOK)
            self._rollback(conn=conn, err=repr(e))

    def update_tags(self, org_id, service_id, tags_data):
        self.repo.auto_commit = False
        conn = self.repo
        try:
            self._del_tags(org_id=org_id, service_id=service_id, conn=conn)
            if (tags_data is not None and tags_data[0]):
                tags = tags_data[3]
                srvc_data = self._get_srvc_row_id(
                    service_id=service_id, org_id=org_id)
                srvc_rw_id = srvc_data[0]['row_id']
                for tag in tags:
                    tag = tag.decode('utf-8')
                    tag = tag.rstrip("\u0000")
                    self._create_tags(srvc_rw_id=srvc_rw_id, org_id=org_id, service_id=service_id, tag_name=tag,
                                      conn=conn)
                self._commit(conn)
        except Exception as e:
            self.util_obj.report_slack(
                type=1, slack_msg=repr(e), SLACK_HOOK=SLACK_HOOK)
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
