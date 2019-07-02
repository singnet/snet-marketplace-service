import datetime
from collections import defaultdict

import web3
from common.repository import NETWORKS
from common.utils import Utils
from eth_account.messages import defunct_hash_message
from pymysql import MySQLError


class Registry:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_utils = Utils()

    def _get_all_service(self):
        try:
            all_orgs_srvcs_raw = self.repo.execute("SELECT O.org_id, O.owner_address, S.service_id  FROM service S, "
                                                   "organization O WHERE S.org_id = O.org_id AND S.is_curated = 1")
            all_orgs_srvcs = {}
            for rec in all_orgs_srvcs_raw:
                if rec['org_id'] not in all_orgs_srvcs.keys():
                    all_orgs_srvcs[rec['org_id']] = {'service_id': [],
                                                     'owner_address': rec['owner_address']}
                all_orgs_srvcs[rec['org_id']]['service_id'].append(rec['service_id'])
            return all_orgs_srvcs
        except Exception as e:
            print(repr(e))
            raise e

    def _get_all_members(self):
        try:
            all_orgs_members_raw = self.repo.execute("SELECT org_id, member FROM members M")
            all_orgs_members = defaultdict(list)
            for rec in all_orgs_members_raw:
                all_orgs_members[rec['org_id']].append(rec['member'])
            print(all_orgs_members)
            return all_orgs_members
        except Exception as e:
            print(repr(e))
            raise e

    def get_all_org(self):
        try:
            all_orgs_srvcs = self._get_all_service()
            all_orgs_members = self._get_all_members()
            all_orgs_data = []
            for rec in all_orgs_srvcs:
                data = {"org_id": rec,
                        "owner_address": all_orgs_srvcs[rec]['owner_address'],
                        "service_id": all_orgs_srvcs[rec]['service_id'],
                        "members": all_orgs_members.get(rec, [])}
                all_orgs_data.append(data)
            return all_orgs_data
        except Exception as e:
            print(repr(e))
            raise e

    def _prepare_subquery(self, s, q, fm):
        try:
            sub_qry = ""
            if s == "all":
                for rec in fm:
                    sub_qry += fm[rec] + " LIKE '" + str(q) + "%' OR "
                sub_qry = sub_qry[:-3]
            else:
                sub_qry += fm[s] + " LIKE '" + str(q) + "%' "
            return sub_qry.replace("org_id", "M.org_id")
        except Exception as err:
            raise err

    def _get_total_count(self, sub_qry):
        try:
            count_qry = "SELECT * FROM service A, (SELECT DISTINCT M.org_id, M.service_id FROM service_metadata M " \
                        "LEFT JOIN service_tags T ON M.service_row_id = T.service_row_id WHERE (" \
                        + sub_qry.replace('%', '%%') + ")) B WHERE A.service_id = B.service_id AND A.org_id = B.org_id " \
                                                       "AND A.is_curated=1 ";
            print(count_qry)
            res = self.repo.execute(count_qry)
            return len(res)
        except Exception as err:
            raise err

    def _srch_qry_dta(self, sub_qry, sort_by, order_by, offset, limit):
        try:
            srch_qry = "SELECT * FROM service A, (SELECT M.org_id, M.service_id, group_concat(T.tag_name) AS tags FROM " \
                       "service_metadata M LEFT JOIN service_tags T ON M.service_row_id = T.service_row_id WHERE " \
                       + sub_qry.replace('%', '%%') + " GROUP BY M.org_id, M.service_id ORDER BY %s %s ) B WHERE " \
                                                      "A.service_id = B.service_id AND A.org_id=B.org_id AND A.is_curated= 1 LIMIT %s , %s"
            print(srch_qry)
            qry_dta = self.repo.execute(srch_qry, [sort_by, order_by, int(offset), int(limit)])
            org_srvc_tuple = ()
            rslt = {}
            for rec in qry_dta:
                org_id = rec['org_id']
                service_id = rec['service_id']
                tags = rec['tags']
                org_srvc_tuple = org_srvc_tuple + ((org_id, service_id),)
                if org_id not in rslt.keys():
                    rslt[org_id] = {}
                if service_id not in rslt[org_id].keys():
                    rslt[rec['org_id']] = {'service_id': service_id,
                                           'tags': tags
                                           }

            qry_part = " AND (S.org_id, S.service_id) IN " + str(org_srvc_tuple).replace(',)', ')')
            services = self.repo.execute("SELECT M.* FROM service_metadata M, service S WHERE "
                                         "S.row_id = M.service_row_id " + qry_part)
            obj_utils = Utils()
            obj_utils.clean(services)
            votes_count = self.fetch_total_count()
            available_srvc = self._get_available_srvc()
            print(votes_count)

            for rec in services:
                org_id = rec["org_id"]
                service_id = rec["service_id"]
                tags = []
                is_available = 0
                if rslt[org_id]["tags"]is not None:
                    tags = rslt[org_id]["tags"].split(",")
                if (org_id,service_id) in available_srvc:
                    is_available = 1
                rec.update({"up_votes_count": votes_count.get(org_id, {}).get(service_id, {}).get(1, 0)})
                rec.update(
                    {"down_votes_count": votes_count.get(org_id, {}).get(service_id, {}).get(0, 0)})
                rec.update({"tags": tags})
                rec.update({"is_available": is_available})


            return services
        except Exception as err:
            raise err

    def _srch_resp_format(self, tc, offset, limit, rslt):
        try:
            return {"total_count": tc, "offset": offset, "limit": limit, "result": rslt}
        except Exception as err:
            raise err

    def get_all_srvcs(self, qry_param):
        try:
            fields_mapping = {"dn": "display_name", "tg": "tag_name", "org": "org_id"}
            s = qry_param.get('s', 'all')
            q = qry_param.get('q', '')
            offset = qry_param.get('offset', 0)
            limit = qry_param.get('limit', 15)
            sort_by = fields_mapping.get(qry_param.get('sort_by', None), "display_name")
            order_by = qry_param.get('order_by', 'asc')
            sub_qry = self._prepare_subquery(s=s, q=q, fm=fields_mapping)
            print(sub_qry)
            total_count = self._get_total_count(sub_qry=sub_qry)
            if total_count == 0:
                return self._srch_resp_format(total_count, offset, limit, [])
            q_dta = self._srch_qry_dta(sub_qry=sub_qry, sort_by=sort_by, order_by=order_by,
                                       offset=offset, limit=limit)
            return self._srch_resp_format(total_count, offset, limit, q_dta)
        except Exception as e:
            print(repr(e))
            raise e

    def get_group_info(self, org_id, service_id):
        try:
            grp_info_raw = self.repo.execute(
                "SELECT G.*, E.* FROM service_group G INNER JOIN service_endpoint E ON G.group_id = E.group_id WHERE "
                "G.org_id = %s AND G.service_id = %s ", [org_id, service_id])
            self.obj_utils.clean(grp_info_raw)
            groups = {}
            for rec in grp_info_raw:
                group_id = rec['group_id']
                if group_id not in groups.keys():
                    groups = {group_id: {"group_id": rec['group_id'],
                                         "group_name": rec['group_name'],
                                         "payment_address": rec['payment_address'],
                                         "endpoints": []
                                         }
                              }
                    groups[group_id]['endpoints'].append({"endpoint": rec['endpoint'], "is_available":
                        rec['is_available'], "last_check_timestamp": rec["last_check_timestamp"]})
            return list(groups.values())
        except Exception as e:
            print(repr(e))
            raise e

    def fetch_total_count(self):
        user_vote_count_dict = {}
        try:
            count_details = self.repo.execute(
                "SELECT org_id, service_id, vote, Count(*) AS count FROM user_service_vote GROUP BY vote, service_id, org_id")
            for rec in count_details:
                org_id = rec.get('org_id', '')
                service_id = rec.get('service_id', '')
                vote = rec.get('vote', '')
                count = rec.get('count', '')
                if not org_id in user_vote_count_dict.keys():
                    user_vote_count_dict[org_id] = {}
                if not service_id in user_vote_count_dict[org_id].keys():
                    user_vote_count_dict[org_id][service_id] = {}
                user_vote_count_dict[org_id][service_id][vote] = count
        except Exception as e:
            print(repr(e))
            raise e
        return user_vote_count_dict

    def vote_mapping(self, vote):
        return {'up_vote': (vote == 1),
                'down_vote': (vote == 0)}

    def fetch_user_feedbk(self, user_address):
        user_vote_dict = {}
        try:
            votes = self.repo.execute(
                "SELECT * FROM user_service_vote WHERE user_address = %s", (user_address))
            self.obj_utils.clean(votes)
            feedbk = self.repo.execute(
                "SELECT A.* FROM user_service_feedback A INNER JOIN (SELECT user_address,org_id, service_id,  "
                "max(row_updated) latest_dt FROM user_service_feedback WHERE user_address = %s GROUP BY user_address, "
                "org_id, service_id) B  on A.user_address = B.user_address AND A.org_id = B.org_id AND A.service_id = "
                "B.service_id AND A.row_updated = B.latest_dt", (user_address))
            self.obj_utils.clean(feedbk)
            for rec in votes:
                org_id = rec['org_id']
                service_id = rec['service_id']
                if org_id not in user_vote_dict.keys():
                    user_vote_dict[org_id] = {}
                user_vote_dict[org_id][service_id] = {'user_address': rec['user_address'],
                                                      'org_id': rec['org_id'],
                                                      'service_id': service_id
                                                      }
                user_vote_dict[org_id][service_id].update(self.vote_mapping(rec['vote']))
            for rec in feedbk:
                org_id = rec['org_id']
                service_id = rec['service_id']
                user_vote_dict[org_id][service_id]['comment'] = rec['comment']

        except Exception as e:
            print(repr(e))
            raise e
        return user_vote_dict

    def get_usr_feedbk(self, user_address):
        vote_list = []
        try:
            count_details = self.fetch_total_count()
            votes = self.fetch_user_feedbk(user_address)
            for org_id in count_details.keys():
                srvcs_data = count_details[org_id]
                for service_id in srvcs_data.keys():
                    rec = {
                        'org_id': org_id,
                        'service_id': service_id,
                        'up_vote_count': srvcs_data.get(service_id).get(1, 0),
                        'down_vote_count': srvcs_data.get(service_id).get(0, 0),
                        "up_vote": votes.get(org_id, {}).get(service_id, {}).get('up_vote', False),
                        "down_vote": votes.get(org_id, {}).get(service_id, {}).get('down_vote', False),
                        "comment": votes.get(org_id, {}).get(service_id, {}).get('comment', None)
                    }
                    vote_list.append(rec)
        except Exception as e:
            print(repr(e))
            raise e
        return vote_list

    def is_valid_feedbk(self, net_id, usr_addr, msg_txt, sign):
        try:
            provider = web3.HTTPProvider(NETWORKS[net_id]['http_provider'])
            w3 = web3.Web3(provider)
            message = w3.sha3(text=msg_txt)
            message_hash = defunct_hash_message(primitive=message)
            recovered = str(w3.eth.account.recoverHash(message_hash, signature=sign))
            return str(usr_addr).lower() == recovered.lower()
        except Exception as e:
            print(repr(e))
            raise e
        return False

    def set_usr_feedbk(self, feedbk_info, net_id):
        try:
            vote = -1
            if feedbk_info['up_vote']:
                vote = 1
            elif feedbk_info['down_vote']:
                vote = 0
            curr_dt = datetime.datetime.utcnow()
            usr_addr = feedbk_info['user_address']
            org_id = feedbk_info['org_id']
            srvc_id = feedbk_info['service_id']
            comment = feedbk_info['comment']
            msg_txt = str(usr_addr) + str(org_id) + str(feedbk_info['up_vote']).lower() + str(srvc_id) + \
                      str(feedbk_info['down_vote']).lower() + str(comment).lower()
            if self.is_valid_feedbk(net_id=net_id, usr_addr=usr_addr, msg_txt=msg_txt, sign=feedbk_info['signature']):
                self.repo.begin_transaction()
                insrt_vote = "INSERT INTO user_service_vote (user_address, org_id, service_id, vote, row_updated, row_created) " \
                             "VALUES (%s, %s, %s, %s, %s, %s) " \
                             "ON DUPLICATE KEY UPDATE vote = %s, row_updated = %s"
                insrt_vote_params = [usr_addr, org_id, srvc_id, vote, curr_dt, curr_dt, vote, curr_dt]
                self.repo.execute(insrt_vote, insrt_vote_params)

                insrt_feedbk = "INSERT INTO user_service_feedback (user_address, org_id, service_id, comment, " \
                               "row_updated, row_created)" \
                               "VALUES (%s, %s, %s, %s, %s, %s) "
                insrt_feedbk_params = [usr_addr, org_id, srvc_id, comment, curr_dt, curr_dt]
                self.repo.execute(insrt_feedbk, insrt_feedbk_params)
                self.repo.commit_transaction()
            else:
                raise Exception("signature of the vote is not valid.")
        except MySQLError as e:
            self.repo.rollback_transaction()
            raise e
        except Exception as err:
            print(repr(err))
            raise err
        return True

    def _get_available_srvc(self):
        try:
            available_srvc = []
            srvc_st_dta = self.repo.execute(
                "SELECT DISTINCT org_id, service_id  FROM service_endpoint WHERE is_available = 1")
            for rec in srvc_st_dta:
                available_srvc.append((rec['org_id'], rec['service_id']), )
            print(available_srvc)
            return available_srvc
        except Exception as err:
            print(repr(err))
