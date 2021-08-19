import json
from collections import defaultdict

from common.constant import BuildStatus
from common.logger import get_logger
from common.utils import Utils
from contract_api.constant import GET_ALL_SERVICE_LIMIT, GET_ALL_SERVICE_OFFSET_LIMIT
from contract_api.dao.service_repository import ServiceRepository
from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.domain.models.demo_component import DemoComponent
from contract_api.domain.models.offchain_service_attribute import OffchainServiceAttribute
from contract_api.infrastructure.repositories.service_media_repository import ServiceMediaRepository
from contract_api.infrastructure.repositories.service_repository import ServiceRepository as NewServiceRepository, \
    OffchainServiceConfigRepository
from contract_api.filter import Filter

logger = get_logger(__name__)
BUILD_CODE = {"SUCCESS": 1, "FAILED": 0}
new_service_repo = NewServiceRepository()
service_media_repo = ServiceMediaRepository()
service_factory = ServiceFactory()


class Registry:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_utils = Utils()

    @staticmethod
    def service_build_status_notifier(org_id, service_id, build_status):
        is_curated = False
        if build_status == BUILD_CODE['SUCCESS']:
            is_curated = True
        service = new_service_repo.get_service(org_id=org_id, service_id=service_id)
        if service:
            service.is_curated = is_curated
            new_service_repo.create_or_update_service(service=service)
        else:
            raise Exception(f"Unable to find service for service_id {service_id} and org_id {org_id}")
        demo_build_status = BuildStatus.SUCCESS if build_status == BUILD_CODE['SUCCESS'] else BuildStatus.FAILED
        offchain_attributes = OffchainServiceAttribute(
            org_id, service_id, {"demo_component_status": demo_build_status}
        )
        OffchainServiceConfigRepository().save_offchain_service_attribute(offchain_attributes)

    def _get_all_service(self):
        """ Method to generate org_id and service mapping."""
        try:
            all_orgs_srvcs_raw = self.repo.execute(
                "SELECT O.org_id, O.organization_name,O.org_assets_url, O.owner_address, S.service_id  FROM service S, "
                "organization O WHERE S.org_id = O.org_id AND S.is_curated = 1")
            all_orgs_srvcs = {}
            for rec in all_orgs_srvcs_raw:
                if rec['org_id'] not in all_orgs_srvcs.keys():
                    all_orgs_srvcs[rec['org_id']] = {'service_id': [],
                                                     'organization_name': rec["organization_name"],
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
            query = "SELECT org_id, `member` FROM members M"
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
            for org_rec in all_orgs_srvcs:
                data = {"org_id": org_rec,
                        "org_name": all_orgs_srvcs[org_rec]["organization_name"],
                        "owner_address": all_orgs_srvcs[org_rec]['owner_address'],
                        "service_id": all_orgs_srvcs[org_rec]['service_id'],
                        "members": all_orgs_members.get(org_rec, [])}
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
                    sub_qry += fm[rec] + " LIKE '%" + str(q) + "%' OR "
                sub_qry = sub_qry[:-3] if sub_qry.endswith("OR ") else sub_qry
            else:
                sub_qry += fm[s] + " LIKE '%" + str(q) + "%' "
            return sub_qry.replace("org_id", "M.org_id")
        except Exception as err:
            raise err

    def _get_total_count(self, sub_qry, filter_query, values):
        try:
            if filter_query != "":
                filter_query = " AND " + filter_query
            search_count_query = "SELECT count(*) as search_count FROM service A, (SELECT DISTINCT M.org_id, M.service_id FROM " \
                                 "service_metadata M LEFT JOIN service_tags T ON M.service_row_id = T.service_row_id WHERE (" \
                                 + sub_qry.replace('%',
                                                   '%%') + ")" + filter_query + ") B WHERE A.service_id = B.service_id " \
                                                                                "AND A.org_id = B.org_id AND A.is_curated = 1 "

            res = self.repo.execute(search_count_query, values)
            return res[0].get("search_count", 0)
        except Exception as err:
            raise err

    def _convert_service_metadata_str_to_json(self, record):
        record["service_rating"] = json.loads(record["service_rating"])
        record["org_assets_url"] = json.loads(record["org_assets_url"])
        record["contributors"] = json.loads(record.get("contributors", "[]"))
        record["contacts"] = json.loads(record.get("contacts", "[]"))

        if record["contacts"] is None:
            record["contacts"] = []
        if record["contributors"] is None:
            record["contributors"] = []

    def _search_query_data(self, sub_qry, sort_by, order_by, offset, limit, filter_query, values):
        try:
            if filter_query != "":
                filter_query = " AND " + filter_query
            srch_qry = "SELECT * FROM service A, (SELECT M.org_id, M.service_id, group_concat(T.tag_name) AS tags FROM " \
                       "service_metadata M LEFT JOIN service_tags T ON M.service_row_id = T.service_row_id " \
                       "LEFT JOIN service_endpoint E ON M.service_row_id = E.service_row_id WHERE (" \
                       + sub_qry.replace('%', '%%') + ")" + filter_query + \
                       " GROUP BY M.org_id, M.service_id ORDER BY E.is_available DESC, " + sort_by + " " + order_by + \
                       " ) B WHERE A.service_id = B.service_id AND A.org_id=B.org_id AND A.is_curated= 1 LIMIT %s , %s"

            qry_dta = self.repo.execute(
                srch_qry, values + [int(offset), int(limit)])
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
            qry_part_where = " AND (org_id, service_id) IN " + \
                             str(org_srvc_tuple).replace(',)', ')')
            print("qry_part::", qry_part)
            sort_by = sort_by.replace("org_id", "M.org_id")
            if org_srvc_tuple:
                services = self.repo.execute(
                    "SELECT DISTINCT M.row_id, M.service_row_id, M.org_id, M.service_id, M.display_name, M.description, M.url, M.json, M.model_ipfs_hash, M.encoding, M.`type`,"
                    " M.mpe_address,M.service_rating, M.ranking, M.contributors, M.short_description,"
                    "O.organization_name,O.org_assets_url FROM service_endpoint E, service_metadata M, service S "
                    ", organization O WHERE O.org_id = S.org_id AND S.row_id = M.service_row_id AND "
                    "S.row_id = E.service_row_id " + qry_part + "ORDER BY E.is_available DESC, " + sort_by + " " + order_by)
                services_media = self.repo.execute(
                    "select org_id ,service_id,file_type ,asset_type,url,alt_text ,`order`,row_id from service_media where asset_type = 'hero_image' " + qry_part_where)
            else:
                services = []
                services_media = []
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
                asset_media = []
                if len(services_media) > 0:
                    asset_media = [x for x in services_media if x['service_id'] == service_id]
                    if len(asset_media) > 0:
                        asset_media = asset_media[0]
                rec.update({"tags": tags})
                rec.update({"is_available": is_available})
                rec.update({"media": asset_media})

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
            fields_mapping = {"display_name": "display_name",
                              "tag_name": "tag_name", "org_id": "org_id"}
            s = qry_param.get('s', 'all')
            q = qry_param.get('q', '')
            offset = qry_param.get('offset', GET_ALL_SERVICE_OFFSET_LIMIT)
            limit = qry_param.get('limit', GET_ALL_SERVICE_LIMIT)
            sort_by = fields_mapping.get(
                qry_param.get('sort_by', None), "ranking")
            order_by = qry_param.get('order_by', 'desc')
            if order_by.lower() != "desc":
                order_by = "asc"

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
                                         "endpoints": [],
                                         "free_calls": rec.get("free_calls", 0),
                                         "free_call_signer_address": rec.get("free_call_signer_address", "")
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
            return '%s %s %s' % (
                filter_condition.attr, filter_condition.operator, "(" + (("%s,") * len(value))[:-1] + ")"), value
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
                filter_data = self.repo.execute(
                    "SELECT DISTINCT tag_name AS 'key', tag_name AS 'value' FROM service_tags T, service S "
                    "WHERE S.row_id = T.service_row_id AND S.is_curated = 1")
            elif attribute == "display_name":
                filter_data = self.repo.execute(
                    "SELECT DISTINCT S.service_id AS 'key',display_name AS 'value' FROM service_metadata M, service S "
                    "WHERE S.row_id = M.service_row_id AND S.is_curated = 1")
            elif attribute == "org_id":
                filter_data = self.repo.execute(
                    "SELECT DISTINCT O.org_id AS 'key' ,O.organization_name AS 'value' from organization O, service S "
                    "WHERE S.org_id = O.org_id AND S.is_curated = 1")
            else:
                return filter_attribute
            for rec in filter_data:
                filter_attribute["values"].append(rec)

            return filter_attribute
        except Exception as e:
            print(repr(e))
            raise e

    def get_all_group_for_org_id(self, org_id):
        """ Method to get all group data for given org_id. This includes group data at org level"""
        try:
            groups_data = self.repo.execute(
                "SELECT group_id, group_name, payment FROM org_group WHERE org_id = %s", [org_id])
            [group_record.update({'payment': json.loads(group_record['payment'])})
             for group_record in groups_data]
            groups = {"org_id": org_id,
                      "groups": groups_data}
            return groups
        except Exception as e:
            print(repr(e))
            raise e

    def get_group_details_for_org_id(self, org_id, group_id):
        """ Method to get group data for given org_id and group_id. This includes group data at org level"""
        group_data = self.repo.execute(
            "SELECT group_id, group_name, payment , org_id FROM org_group WHERE org_id = %s and group_id = %s",
            [org_id, group_id]
        )
        [group_record.update({'payment': json.loads(group_record['payment'])})
         for group_record in group_data]
        return {"groups": group_data}

    def get_service_data_by_org_id_and_service_id(self, org_id, service_id):
        try:
            """ Method to get all service data for given org_id and service_id"""
            tags = []
            org_groups_dict = {}
            basic_service_data = self.repo.execute(
                "SELECT M.row_id, M.service_row_id, M.org_id, M.service_id, M.display_name, M.description, M.url, M.json, M.model_ipfs_hash, M.encoding, M.`type`,"
                " M.mpe_address,M.service_rating, M.ranking, M.contributors, M.short_description, M.demo_component_available,"
                " S.*, O.org_id, O.organization_name, O.owner_address, O.org_metadata_uri, O.org_email, "
                "O.org_assets_url, O.description as org_description, O.contacts "
                "FROM service_metadata M, service S, organization O "
                "WHERE O.org_id = S.org_id AND S.row_id = M.service_row_id AND S.org_id = %s "
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

            service_media = service_media_repo.get_service_media(org_id=org_id, service_id=service_id)
            media = [media_data.to_dict() for media_data in service_media]
            result = basic_service_data[0]

            self._convert_service_metadata_str_to_json(result)

            offchain_service_configs = Registry.prepare_offchain_service_attributes(org_id, service_id)

            for rec in org_group_data:
                org_groups_dict[rec['group_id']] = {
                    "payment": json.loads(rec["payment"])}

            is_available = 0
            # Hard Coded Free calls in group data
            for rec in service_group_data:
                rec["free_calls"] = rec.get("free_calls", 0)
                if is_available == 0:
                    endpoints = rec['endpoints']
                    for endpoint in endpoints:
                        is_available = endpoint['is_available']
                        if is_available == 1:
                            break
                rec.update(org_groups_dict.get(rec['group_id'], {}))

            result.update({"is_available": is_available, "groups": service_group_data, "tags": tags, "media": media})
            result.update(offchain_service_configs)
            return result
        except Exception as e:
            print(repr(e))
            raise e

    @staticmethod
    def prepare_offchain_service_attributes(org_id, service_id):
        offchain_attributes = {}
        offchain_service_config_repo = OffchainServiceConfigRepository()
        offchain_service_config = offchain_service_config_repo.get_offchain_service_config(
            org_id=org_id,
            service_id=service_id
        )
        offchain_attributes_db = offchain_service_config.attributes
        demo_component_required = offchain_attributes_db.get("demo_component_required", 0)
        demo_component = service_factory.create_demo_component_domain_model(offchain_service_config.attributes)
        offchain_attributes.update({"demo_component_required": demo_component_required})
        offchain_attributes.update({"demo_component": demo_component.to_dict(
                    last_modified=offchain_attributes_db.get("demo_component_last_modified", {}))
                if demo_component else demo_component})
        return offchain_attributes

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

    def update_service_rating(self, org_id, service_id):
        """
            Method updates service_rating and total_user_rated when user rating is changed for given service_id
            and org_id.
        """
        try:
            update_service_metadata = self.repo.execute(
                "UPDATE service_metadata A  INNER JOIN "
                "(SELECT U.org_id, U.service_id, AVG(U.rating) AS service_rating, count(*) AS total_users_rated "
                "FROM user_service_vote AS U WHERE U.rating IS NOT NULL GROUP BY U.service_id, U.org_id ) AS B "
                "ON A.org_id=B.org_id AND A.service_id=B.service_id SET A.service_rating "
                "= CONCAT('{\"rating\":', B.service_rating, ' , \"total_users_rated\":', B.total_users_rated, '}') "
                "WHERE A.org_id = %s AND A.service_id = %s ", [org_id, service_id])
            return "success"
        except Exception as e:
            print(repr(e))
            raise e

    def curate_service(self, org_id, service_id, curated):
        service_repo = ServiceRepository(self.repo)
        if str(curated).lower() == "true":
            service_repo.curate_service(org_id, service_id, 1)
        elif str(curated).lower() == "false":
            service_repo.curate_service(org_id, service_id, 0)
        else:
            Exception("Invalid curation flag")
