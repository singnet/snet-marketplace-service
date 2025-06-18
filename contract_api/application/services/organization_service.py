


class OrganizationService:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_utils = Utils()

    # is used in handler
    def get_all_organizations(self):
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
            logger.exception(repr(e))
            raise e

    # is used in handler
    def get_group(self, org_id, group_id):
        """ Method to get group data for given org_id and group_id. This includes group data at org level"""
        group_data = self.repo.execute(
            "SELECT group_id, group_name, payment , org_id FROM org_group WHERE org_id = %s and group_id = %s",
            [org_id, group_id]
        )
        [group_record.update({'payment': json.loads(group_record['payment'])})
         for group_record in group_data]
        return {"groups": group_data}

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
            logger.exception(repr(e))
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
            logger.exception(repr(e))
            raise e