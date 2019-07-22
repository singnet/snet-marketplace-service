import datetime
from collections import defaultdict
from common.utils import Utils
from pymysql import MySQLError
from contract_api.filter import Filter

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
            return all_orgs_members
        except Exception as e:
            print(repr(e))
            raise e

    def get_all_org(self):
        """ Method to get list and high level details of all organization."""
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
                sub_qry = sub_qry[:-3] if sub_qry.endswith("OR ") else sub_qry
            else:
                sub_qry += fm[s] + " LIKE '" + str(q) + "%' "
            return sub_qry.replace("org_id", "M.org_id")
        except Exception as err:
            raise err

    def _get_total_count(self, sub_qry, filter_query, values):
        try:
            if filter_query != "":
                filter_query = " AND " + filter_query
            search_count_query = "SELECT count(*) as search_count FROM service A, (SELECT DISTINCT M.org_id, M.service_id FROM " \
                                 "service_metadata M LEFT JOIN service_tags T ON M.service_row_id = T.service_row_id WHERE (" \
                                 + sub_qry.replace('%', '%%') + ")" + filter_query +  ") B WHERE A.service_id = B.service_id " \
                                 "AND A.org_id = B.org_id AND A.is_curated = 1 ";

            res = self.repo.execute(search_count_query, values)
            return res[0].get("search_count", 0)
        except Exception as err:
            raise err

    def _srch_qry_dta(self, sub_qry, sort_by, order_by, offset, limit, filter_query, values):
        try:
            if filter_query != "":
                filter_query = " AND " + filter_query
            srch_qry = "SELECT * FROM service A, (SELECT M.org_id, M.service_id, group_concat(T.tag_name) AS tags FROM " \
                       "service_metadata M LEFT JOIN service_tags T ON M.service_row_id = T.service_row_id WHERE " \
                       + sub_qry.replace('%', '%%') + filter_query + " GROUP BY M.org_id, M.service_id ORDER BY %s %s ) B WHERE " \
                                                      "A.service_id = B.service_id AND A.org_id=B.org_id AND A.is_curated= 1 LIMIT %s , %s"

            qry_dta = self.repo.execute(srch_qry, values + [sort_by, order_by, int(offset), int(limit)])
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
                    rslt[org_id][service_id] = {}
                rslt[org_id][service_id]["tags"] = tags
            qry_part = " AND (S.org_id, S.service_id) IN " + str(org_srvc_tuple).replace(',)', ')')
            services = self.repo.execute("SELECT M.* FROM service_metadata M, service S WHERE "
                                         "S.row_id = M.service_row_id " + qry_part)
            obj_utils = Utils()
            obj_utils.clean(services)
            service_rating = self.fetch_total_count()
            available_srvc = self._get_available_srvc()
            service_assets_map = {}
            for rec in services:
                org_id = rec["org_id"]
                service_id = rec["service_id"]
                tags = []
                is_available = 0
                if rslt.get(org_id, {}).get(service_id, {}).get("tags", None) is not None:
                    tags = rslt[org_id][service_id]["tags"].split(",")
                if (org_id,service_id) in available_srvc:
                    is_available = 1
                rec.update({"service_rating": service_rating.get(org_id, {}).get(service_id, {}).get("service_rating", None)})
                rec.update({"total_users_rated": service_rating.get(org_id, {}).get(service_id, {}).get("total_users_rated", None)})
                rec.update({"tags": tags})
                rec.update({"is_available": is_available})
                rec.update({"hero_image": service_assets_map.get(org_id, {}).get(service_id, {})})


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
            print("get_all_srvcs::sub_qry: ", sub_qry)

            filter_qry = ""
            if qry_param.get("filters", None) is not None:
                filter_query, values = self.filters_to_query(qry_param.get("filters"))
                print("get_all_srvcs::filter_query: ", filter_query, "|values: ", values)
            total_count = self._get_total_count(sub_qry=sub_qry, filter_query=filter_query, values=values)
            if total_count == 0:
                return self._srch_resp_format(total_count, offset, limit, [])
            q_dta = self._srch_qry_dta(sub_qry=sub_qry, sort_by=sort_by, order_by=order_by,
                                       offset=offset, limit=limit, filter_query=filter_query, values=values)
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
                "SELECT org_id, service_id, AVG(rating) AS service_rating, count(*) AS total_users_rated FROM "
                "user_service_vote WHERE rating is NOT NULL GROUP BY service_id, org_id")
            for rec in count_details:
                org_id = rec.get('org_id', '')
                service_id = rec.get('service_id', '')
                if not org_id in user_vote_count_dict.keys():
                    user_vote_count_dict[org_id] = {}
                user_vote_count_dict[org_id][service_id] = {"service_rating": rec.get('service_rating'),
                                                            "total_users_rated": rec.get('total_users_rated') }
            return user_vote_count_dict
        except Exception as e:
            print(repr(e))
            raise e

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
                                                      'service_id': service_id,
                                                      'user_rating': rec['rating']
                                                      }
            for rec in feedbk:
                org_id = rec['org_id']
                service_id = rec['service_id']
                user_vote_dict[org_id][service_id]['comment'] = rec['comment']

            return user_vote_dict
        except Exception as e:
            print(repr(e))
            raise e

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
                        'service_rating': srvcs_data.get(service_id, {}).get("service_rating", None),
                        "user_rating": votes.get(org_id, {}).get(service_id, {}).get("user_rating", None),
                        "comment": votes.get(org_id, {}).get(service_id, {}).get('comment', None)
                    }
                    vote_list.append(rec)
            return vote_list
        except Exception as e:
            print(repr(e))
            raise e

    def set_usr_feedbk(self, feedbk_info, net_id):
        try:
            user_rating = feedbk_info['user_rating']
            curr_dt = datetime.datetime.utcnow()
            usr_addr = feedbk_info['user_address']
            org_id = feedbk_info['org_id']
            srvc_id = feedbk_info['service_id']
            comment = feedbk_info['comment']
            self.repo.begin_transaction()
            set_rating = "INSERT INTO user_service_vote (user_address, org_id, service_id, rating, row_updated, row_created) " \
                         "VALUES (%s, %s, %s, %s, %s, %s) " \
                         "ON DUPLICATE KEY UPDATE rating = %s, row_updated = %s"
            set_rating_params = [usr_addr, org_id, srvc_id, user_rating, curr_dt, curr_dt, user_rating, curr_dt]
            self.repo.execute(set_rating, set_rating_params)
            set_feedback = "INSERT INTO user_service_feedback (user_address, org_id, service_id, comment, row_updated, row_created)" \
                           "VALUES (%s, %s, %s, %s, %s, %s)"
            set_feedback_params = [usr_addr, org_id, srvc_id, comment, curr_dt, curr_dt]
            self.repo.execute(set_feedback, set_feedback_params)
            self.repo.commit_transaction()
            return True
        except MySQLError as e:
            self.repo.rollback_transaction()
            raise e
        except Exception as err:
            print(repr(err))
            raise err

    def _get_available_srvc(self):
        try:
            available_srvc = []
            srvc_st_dta = self.repo.execute(
                "SELECT DISTINCT org_id, service_id  FROM service_endpoint WHERE is_available = 1")
            for rec in srvc_st_dta:
                available_srvc.append((rec['org_id'], rec['service_id']), )
            return available_srvc
        except Exception as err:
            print(repr(err))

    def filter_condition_to__query(self, filter_condition):
        value = []
        if filter_condition.attr in ["org_id", "service_id"]:
            filter_condition.attr = "M." + filter_condition.attr
        if filter_condition.operator == "=":
            value = filter_condition.value
            return '%s %s"%s"'%(filter_condition.attr, filter_condition.operator, "%s"), value
        if filter_condition.operator == "IN":
            value = filter_condition.value
            return '%s %s %s'%(filter_condition.attr, filter_condition.operator, "(" + (("%s,")*len(value))[:-1] +")"), value
        if filter_condition.operator == "BETWEEN":
            value = filter_condition.value
            return '%s %s %s AND %s'%(filter_condition.attr, filter_condition.operator, "%s", "%s"), value

    def filters_to_query(self, filter_json):
        query = ""
        filters = []
        values = []
        for filter in filter_json:
            filters.append(Filter(filter))
        for filter in filters:
            query += "("
            for filter_condition in filter.get_filter().get("filter"):
                sub_query , value = self.filter_condition_to__query(filter_condition)
                values +=  value
                query = query + "(" + sub_query + ") AND "
            if query.endswith(" AND "):
                query = query[:-5]
            query += ") OR "
        if query.endswith(" OR "):
            query = query[:-4]
        return query, values

    def get_filter_attribute(self, attribute):
        try:
            filter_attribute = {"attribute": attribute , "values": []}
            if attribute == "tag_name":
                filter_data = self.repo.execute("SELECT DISTINCT tag_name AS ATTR_VALUE FROM service_tags T, service S "
                                                "WHERE S.row_id = T.service_row_id AND S.is_curated = 1")
            elif attribute == "display_name":
                filter_data = self.repo.execute("SELECT DISTINCT display_name AS ATTR_VALUE FROM service_metadata M, service S "
                                                "WHERE S.row_id = M.service_row_id AND S.is_curated = 1")
            elif attribute == "org_id":
                filter_data = self.repo.execute("SELECT DISTINCT organization_name AS ATTR_VALUE from organization O, service S "
                                                "WHERE S.org_id = O.org_id AND S.is_curated = 1")
            else:
                return filter_attribute
            for rec in filter_data:
                filter_attribute["values"].append(rec.get("ATTR_VALUE", None))

            return filter_attribute
        except Exception as e:
            print(repr(e))
            raise e

    def update_service_rating(self, org_id, service_id):
        try:
            rating_data = self.repo.execute()
        except Exception as e:
            print(repr(e))
            raise e