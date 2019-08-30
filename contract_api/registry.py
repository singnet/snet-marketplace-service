import json
from collections import defaultdict
from common.utils import Utils
from contract_api.filter import Filter
from contract_api.constant import GET_ALL_SERVICE_OFFSET_LIMIT, GET_ALL_SERVICE_LIMIT


class Registry:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_utils = Utils()

    def _get_all_service(self):
        """ Method to generate org_id and service mapping."""
        try:
            all_orgs_srvcs_raw = self.repo.execute("SELECT O.org_id, O.organization_name, O.owner_address, S.service_id  FROM service S, "
                                                   "organization O WHERE S.org_id = O.org_id AND S.is_curated = 1")
            all_orgs_srvcs = {}
            for rec in all_orgs_srvcs_raw:
                if rec['org_id'] not in all_orgs_srvcs.keys():
                    all_orgs_srvcs[rec['org_id']] = {'service_id': [],
                                                     'owner_address': rec['owner_address']}
                all_orgs_srvcs[rec['org_id']]['service_id'].append(
                    rec['service_id'])
            return all_orgs_srvcs
        except Exception as e:
            print(repr(e))
            raise e

    def _get_all_members(self, org_id=None):
        """ Method to generate org_id and members mapping."""
        try:
            query = "SELECT org_id, member FROM members M"
            params = None
            if org_id is not None:
                query += " where M.org_id = %s"
                params = [org_id]

            all_orgs_members_raw = self.repo.execute(query, params)
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
                                 + sub_qry.replace('%', '%%') + ")" + filter_query + ") B WHERE A.service_id = B.service_id " \
                                 "AND A.org_id = B.org_id AND A.is_curated = 1 "

            res = self.repo.execute(search_count_query, values)
            return res[0].get("search_count", 0)
        except Exception as err:
            raise err

    def _convert_service_metadata_str_to_json(self, record):
        record["service_rating"] = json.loads(record["service_rating"])
        record["assets_url"] = json.loads(record["assets_url"])
        record["assets_hash"] = json.loads(record["assets_hash"])

    def _search_query_data(self, sub_qry, sort_by, order_by, offset, limit, filter_query, values):
        try:
            if filter_query != "":
                filter_query = " AND " + filter_query
            srch_qry = "SELECT * FROM service A, (SELECT M.org_id, M.service_id, group_concat(T.tag_name) AS tags FROM " \
                       "service_metadata M LEFT JOIN service_tags T ON M.service_row_id = T.service_row_id WHERE (" \
                       + sub_qry.replace('%', '%%') + ")" + filter_query + " GROUP BY M.org_id, M.service_id ORDER BY %s %s ) B WHERE " \
                                                      "A.service_id = B.service_id AND A.org_id=B.org_id AND A.is_curated= 1 LIMIT %s , %s"

            qry_dta = self.repo.execute(
                srch_qry, values + [sort_by, order_by, int(offset), int(limit)])
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
            qry_part = " AND (S.org_id, S.service_id) IN " + \
                str(org_srvc_tuple).replace(',)', ')')
            services = self.repo.execute("SELECT M.* FROM service_metadata M, service S WHERE "
                                         "S.row_id = M.service_row_id " + qry_part)
            obj_utils = Utils()
            obj_utils.clean(services)
            available_service = self._get_is_available_service()
            for rec in services:
                self._convert_service_metadata_str_to_json(rec)

                org_id = rec["org_id"]
                service_id = rec["service_id"]
                tags = []
                is_available = 0
                if rslt.get(org_id, {}).get(service_id, {}).get("tags", None) is not None:
                    tags = rslt[org_id][service_id]["tags"].split(",")
                if (org_id, service_id) in available_service:
                    is_available = 1
                rec.update({"tags": tags})
                rec.update({"is_available": is_available})

            return services
        except Exception as err:
            raise err

    def _search_response_format(self, tc, offset, limit, rslt):
        try:
            return {"total_count": tc, "offset": offset, "limit": limit, "result": rslt}
        except Exception as err:
            raise err

    def get_all_srvcs(self, qry_param):
        try:
            fields_mapping = {"dn": "display_name",
                              "tg": "tag_name", "org": "org_id"}
            s = qry_param.get('s', 'all')
            q = qry_param.get('q', '')
            offset = qry_param.get('offset', GET_ALL_SERVICE_OFFSET_LIMIT)
            limit = qry_param.get('limit', GET_ALL_SERVICE_LIMIT)
            sort_by = fields_mapping.get(
                qry_param.get('sort_by', None), "ranking")
            order_by = qry_param.get('order_by', 'desc')

            sub_qry = self._prepare_subquery(s=s, q=q, fm=fields_mapping)
            print("get_all_srvcs::sub_qry: ", sub_qry)

            filter_qry = ""
            if qry_param.get("filters", None) is not None:
                filter_query, values = self._filters_to_query(
                    qry_param.get("filters"))
                print("get_all_srvcs::filter_query: ",
                      filter_query, "|values: ", values)
            total_count = self._get_total_count(
                sub_qry=sub_qry, filter_query=filter_query, values=values)
            if total_count == 0:
                return self._search_response_format(total_count, offset, limit, [])
            q_dta = self._search_query_data(sub_qry=sub_qry, sort_by=sort_by, order_by=order_by,
                                            offset=offset, limit=limit, filter_query=filter_query, values=values)
            return self._search_response_format(total_count, offset, limit, q_dta)
        except Exception as e:
            print(repr(e))
            raise e

    def get_group_info(self, org_id, service_id):
        try:
            group_data = self.repo.execute(
                "SELECT G.*, E.* FROM service_group G INNER JOIN service_endpoint E ON G.group_id = E.group_id AND G.service_row_id = E.service_row_id WHERE "
                "G.org_id = %s AND G.service_id = %s ", [org_id, service_id])
            self.obj_utils.clean(group_data)
            groups = {}
            for rec in group_data:
                group_id = rec['group_id']
                if group_id not in groups.keys():
                    groups = {group_id: {"group_id": rec['group_id'],
                                         "group_name": rec['group_name'],
                                         "pricing": json.loads(rec['pricing']),
                                         "endpoints": []
                                         }
                              }
                    groups[group_id]['endpoints'].append({"endpoint": rec['endpoint'], "is_available":
                                                          rec['is_available'], "last_check_timestamp": rec["last_check_timestamp"]})
            return list(groups.values())
        except Exception as e:
            print(repr(e))
            raise e

    def _get_is_available_service(self):
        try:
            available_service = []
            srvc_st_dta = self.repo.execute(
                "SELECT DISTINCT org_id, service_id  FROM service_endpoint WHERE is_available = 1")
            for rec in srvc_st_dta:
                available_service.append((rec['org_id'], rec['service_id']), )
            return available_service
        except Exception as err:
            print(repr(err))
            raise err

    def _filter_condition_to_query(self, filter_condition):
        value = []
        if filter_condition.attr in ["org_id", "service_id"]:
            filter_condition.attr = "M." + filter_condition.attr
        if filter_condition.operator == "=":
            value = filter_condition.value
            return '%s %s"%s"' % (filter_condition.attr, filter_condition.operator, "%s"), value
        if filter_condition.operator == "IN":
            value = filter_condition.value
            return '%s %s %s' % (filter_condition.attr, filter_condition.operator, "(" + (("%s,")*len(value))[:-1] + ")"), value
        if filter_condition.operator == "BETWEEN":
            value = filter_condition.value
            return '%s %s %s AND %s' % (filter_condition.attr, filter_condition.operator, "%s", "%s"), value

    def _filters_to_query(self, filter_json):
        query = ""
        filters = []
        values = []
        for filter in filter_json:
            filters.append(Filter(filter))
        for filter in filters:
            query += "("
            for filter_condition in filter.get_filter().get("filter"):
                sub_query, value = self._filter_condition_to_query(
                    filter_condition)
                values += value
                query = query + "(" + sub_query + ") AND "
            if query.endswith(" AND "):
                query = query[:-5]
            query += ") OR "
        if query.endswith(" OR "):
            query = query[:-4]
        return query, values

    def get_filter_attribute(self, attribute):
        """ Method to fetch filter metadata based on attribute."""
        try:
            filter_attribute = {"attribute": attribute, "values": []}
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

    def get_all_group_for_org_id(self, org_id):
        """ Method to get all group data for given org_id. This includes group data at org level"""
        try:
            groups_data = self.repo.execute(
                "SELECT group_id, group_name, payment FROM org_group WHERE org_id = %s", [org_id])
            [rec.update({'payment': json.loads(rec['payment'])})
             for rec in groups_data]
            groups = {"org_id": org_id,
                      "groups": groups_data}
            return groups
        except Exception as e:
            print(repr(e))
            raise e

    def get_service_data_by_org_id_and_service_id(self, org_id, service_id):
        try:
            """ Method to get all service data for given org_id and service_id"""
            tags = []
            org_groups_dict = {}
            basic_service_data = self.repo.execute(
                "SELECT * FROM service S, service_metadata M WHERE S.row_id = M.service_row_id AND S.org_id = %s "
                "AND S.service_id = %s AND S.is_curated = 1", [org_id, service_id])
            if len(basic_service_data) == 0:
                return []
            self.obj_utils.clean(basic_service_data)

            org_group_data = self.repo.execute(
                "SELECT * FROM org_group WHERE org_id = %s", [org_id])
            self.obj_utils.clean(org_group_data)

            service_group_data = self.get_group_info(
                org_id=org_id, service_id=service_id)

            tags = self.repo.execute("SELECT tag_name FROM service_tags WHERE org_id = %s AND service_id = %s",
                                     [org_id, service_id])

            result = basic_service_data[0]
            self._convert_service_metadata_str_to_json(result)

            for rec in org_group_data:
                org_groups_dict[rec['group_id']] = {
                    "payment": json.loads(rec["payment"])}

            is_available = 0
            for rec in service_group_data:
                if is_available == 0:
                    endpoints = rec['endpoints']
                    for endpoint in endpoints:
                        is_available = endpoint['is_available']
                        if is_available == 1:
                            break
                rec.update(org_groups_dict.get(rec['group_id'], {}))

            result.update({"is_available": is_available})
            result.update({"groups": service_group_data})
            result.update({"tags": tags})
            return result
        except Exception as e:
            print(repr(e))
            raise e

    def get_org_details(self, org_id):
        """ Method to get org details for given org_id. """
        try:
            org_details = self.repo.execute(
                "SELECT * from organization o, (select org_id, count(*) as service_count "
                "from service where org_id = %s) s where o.org_id = %s and o.org_id = s.org_id", [org_id, org_id])

            obj_utils = Utils()
            obj_utils.clean(org_details)
            if len(org_details) > 0:
                members = self._get_all_members(org_id)
                org_details[0]["members"] = members
            return org_details
        except Exception as e:
            print(repr(e))
            raise e
