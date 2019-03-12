from contract_api.service import Service


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