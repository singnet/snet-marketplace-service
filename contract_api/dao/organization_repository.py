from datetime import datetime
import json

from contract_api.dao.common_repository import CommonRepository


class OrganizationRepository(CommonRepository):

    def __init__(self, connection):

        super().__init__(connection)

    def get_organization(self, org_id):
        query = "select  org_id, organization_name, owner_address,org_metadata_uri, description, org_assets_url, assets_hash ,contacts from organization where org_id = %s"
        query_param = [org_id]
        reposne = self.connection.execute(query, query_param)
        if reposne:
            return reposne[0]
        return None

    def get_organization_group(self, org_id):
        query = "select org_id, group_id, group_name, payment from org_group where org_id = %s"
        query_param = [org_id]
        response = self.connection.execute(query, query_param)
        return response

    def create_or_updatet_organization(self, org_id, org_name, owner_address, org_metadata_uri, description,
                                       is_curated, assets_hash, assets_url, contacts):
        upsert_query = "Insert into organization (org_id, organization_name, owner_address, org_metadata_uri, is_curated, description, assets_hash,org_assets_url, contacts, row_updated, row_created) " \
                       "VALUES ( %s, %s, %s, %s, %s , %s ,%s ,%s, %s ,%s, %s) " \
                       "ON DUPLICATE KEY UPDATE organization_name = %s, owner_address = %s, org_metadata_uri = %s, row_updated = %s, is_curated=%s, description = %s ,assets_hash =%s , org_assets_url = %s , contacts = %s"
        upsert_params = [org_id, org_name, owner_address, org_metadata_uri, is_curated, description, assets_hash,
                         assets_url, contacts,
                         datetime.utcnow(), datetime.utcnow(),
                         org_name, owner_address, org_metadata_uri,
                         datetime.utcnow(), is_curated, description, assets_hash, assets_url, contacts]

        reposne = self.connection.execute(upsert_query, upsert_params)

    def delete_organization(self, org_id):
        del_org = 'DELETE FROM organization WHERE org_id = %s '
        qry_res = self.connection.execute(del_org, [org_id])

    def create_organization_groups(self, org_id, groups):
        insert_qry = "Insert into org_group (org_id, group_id, group_name, payment, row_updated, row_created) " \
                     "VALUES ( %s, %s, %s, %s, %s, %s ) "
        count = 0
        for group in groups:
            insert_params = [org_id, group['group_id'], group['group_name'], json.dumps(
                group['payment']), datetime.utcnow(), datetime.utcnow()]
            query_response = self.connection.execute(insert_qry, insert_params)
            count = count + query_response[0]

    def delete_organization_groups(self, org_id):
        delete_query = self.connection.execute(
            "DELETE FROM org_group WHERE org_id = %s ", [org_id])

    def create_or_update_members(self, org_id, members):
        upsrt_members = "INSERT INTO members ( org_id, member, row_created, row_updated ) " \
                        "VALUES ( %s, %s, %s, %s ) " \
                        "ON DUPLICATE KEY UPDATE row_updated = %s "
        count = 0
        for member in members:
            upsrt_members_params = [org_id, member,
                                    datetime.utcnow(), datetime.utcnow(), datetime.utcnow()]
            query_response = self.connection.execute(upsrt_members, upsrt_members_params)
            count = count + query_response[0]

    def del_members(self, org_id):
        del_org = 'DELETE FROM members WHERE org_id = %s '
        qry_res = self.connection.execute(del_org, org_id)

    def read_registry_events(self):
        query = 'select * from registry_events_raw where processed = 0 order by block_no asc '
        events = self.connection.execute(query)
        print('read_registry_events::read_count: ', len(events))
        return events
