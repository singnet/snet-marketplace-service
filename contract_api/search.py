from contract_api.service import Service
from operator import itemgetter

class Search:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_srvc = Service(obj_repo=obj_repo)

    def get_all_org(self):
        try:
            all_orgs_data = self.repo.execute("SELECT org_id, organization_name, owner_address FROM organization ")
            return all_orgs_data
        except Exception as e:
            print(repr(e))
            raise e

    def get_org(self, org_id):
        try:
            org_data = self.repo.execute(
                "SELECT org_id, organization_name, owner_address FROM organization WHERE org_id = %s ", org_id)
            return org_data
        except Exception as e:
            print(repr(e))
            raise e

    def get_all_srvc(self, org_id):
        try:
            srvcs_data = self.obj_srvc.get_group_info(org_id=org_id)
            return srvcs_data
        except Exception as e:
            print(repr(e))
            raise e

    def get_all_srvc_by_tag(self, tag_name):
        try:
            result = []
            tags_data = self.repo.execute("SELECT * FROM service_tags WHERE tag_name = %s ", tag_name)
            for srvc in tags_data:
                org_id = srvc['org_id']
                srvc_id = srvc['service_id']
                srvc_data = self.obj_srvc.get_group_info(org_id=org_id, srvc_id=srvc_id)
                result += srvc_data
            return result
        except Exception as e:
            print(repr(e))
            raise e

    def _get_total_count(self, sub_qry):
        try:
            count_qry = "SELECT COUNT(*) OVER() AS total_count FROM service_metadata M LEFT JOIN service_tags T ON " \
                        "M.service_row_id = T.service_row_id WHERE  (" + sub_qry + ") GROUP BY M.org_id, M.service_id LIMIT 1";
            res = self.repo.execute(count_qry)
            if len(res) == 0:
                return 0
            return res[0].get("total_count", 0)
        except Exception as err:
            raise err

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

    def _srch_qry_dta(self, sub_qry, sort_by, order_by, offset, limit):
        try:
            srch_qry = "SELECT M.org_id, M.service_id, group_concat(T.tag_name) AS tags FROM service_metadata M " \
                       "LEFT JOIN service_tags T ON M.service_row_id = T.service_row_id WHERE (" \
                       + sub_qry.replace('%', '%%') + ") GROUP BY T.org_id, M.service_id ORDER BY %s %s LIMIT %s , %s"
            return self.repo.execute(srch_qry,[sort_by, order_by, int(offset), int(limit)])

        except Exception as err:
            raise err

    def _format_srch_dta(self, rw_dta):
        try:
            org_srvc_tuple = ()
            for rec in rw_dta:
                org_srvc_tuple = org_srvc_tuple + ((rec['org_id'], rec['service_id']),)
            return org_srvc_tuple
        except Exception as err:
            raise err

    def _get_srvc_data(self, org_srvc_tuple, sort_by, rev):
        try:
            qry_part = " AND (S.org_id, S.service_id) IN " + str(org_srvc_tuple).replace(',)', ')')
            services = self.repo.execute(
                "SELECT * FROM service_metadata M, service S WHERE S.row_id = M.service_row_id "
                + qry_part)
            groups = self.repo.execute("SELECT G.*, E.* FROM service S, service_group G, service_endpoint E WHERE " \
                                       "G.group_id = E.group_id AND G.service_row_id = S.row_id AND " \
                                       "E.service_row_id = S.row_id " + qry_part)
            tags = self.repo.execute(
                "SELECT T.* FROM service S, service_tags T WHERE T.service_row_id = S.row_id " + qry_part)
            obj_srvc = Service(obj_repo=self.repo)
            grpd_srvcs = obj_srvc.merge_service_data(services, groups, tags)
            return sorted(grpd_srvcs, key=lambda i: i[sort_by], reverse=rev)
        except Exception as e:
            print(repr(e))
            raise e

    def _srch_resp_format(self, tc, offset, limit, rslt):
        try:
            return {"total_count": tc, "offset": offset, "limit": limit, "result": rslt}
        except Exception as err:
            raise err

    def get_srch_rslt(self, srch_dta):
        try:
            fields_mapping = {"dn": "display_name", "tg": "tag_name", "org": "org_id"}
            s = srch_dta['s']
            q = srch_dta['q']
            offset = srch_dta['offset']
            limit = srch_dta['limit']
            sort_by = fields_mapping.get(srch_dta['sort_by'], "display_name")
            order_by = srch_dta['order_by']
            reverse = False
            sub_qry = self._prepare_subquery(s=s, q=q, fm=fields_mapping)
            total_count = self._get_total_count(sub_qry=sub_qry)
            if total_count == 0:
                return self._srch_resp_format(total_count, offset, limit, [])
            q_dta = self._srch_qry_dta(sub_qry=sub_qry, sort_by=sort_by, order_by=order_by, offset=offset, limit=limit)
            org_srvc_tuple = self._format_srch_dta(rw_dta=q_dta)
            if str(order_by).lower() == 'desc':
                reverse = True
            result = self._get_srvc_data(org_srvc_tuple=org_srvc_tuple, sort_by=sort_by, rev=reverse)
            return self._srch_resp_format(tc=total_count, offset=offset, limit=limit, rslt=result)
        except Exception as err:
            raise err
