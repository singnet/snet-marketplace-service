import json
from datetime import datetime

from contract_api.dao.common_repository import CommonRepository
from common.logger import get_logger

logger = get_logger(__name__)


class ServiceRepository(CommonRepository):

    def __init__(self, connection):
        super().__init__(connection)

    def create_or_update_service(self, org_id, service_id, hash_uri):
        upsrt_service = "INSERT INTO service (org_id, service_id, is_curated, hash_uri, row_created, row_updated) " \
                        "VALUES (%s, %s, %s, %s, %s, %s) " \
                        "ON DUPLICATE KEY UPDATE hash_uri = %s, row_updated = %s "
        upsrt_service_params = [org_id, service_id, 0, hash_uri,
                                datetime.utcnow(), datetime.utcnow(), hash_uri, datetime.utcnow()]
        query_response = self.connection.execute(upsrt_service, upsrt_service_params)
        return query_response[len(query_response) - 1]

    def create_or_update_service_metadata(self, service_row_id, org_id, service_id, service_metadata, assets_url):
        upsrt_servicec_metadata = "INSERT INTO service_metadata (service_row_id, org_id, service_id, " \
                                  "display_name, model_hash, description,short_description, url, json, encoding, type, " \
                                  "mpe_address, assets_hash , assets_url, service_rating,contributors, row_updated, row_created) " \
                                  "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s ) " \
                                  "ON DUPLICATE KEY UPDATE service_row_id = %s, " \
                                  "display_name = %s, model_hash = %s, description = %s,short_description =%s, url = %s, json = %s, " \
                                  "encoding = %s, type = %s, mpe_address = %s, row_updated = %s ,assets_hash = %s ,assets_url = %s , contributors =%s "

        service_desc = service_metadata.get('service_description', {})
        desc = service_desc.get('description', '')
        short_desc = service_desc.get('short_description', '')
        url = service_desc.get('url', '')
        json_str = service_metadata.get('json', '')
        assets_hash = json.dumps(service_metadata.get('assets', {}))
        assets_url_str = json.dumps(assets_url)
        contributors = json.dumps(service_metadata.get('contributors', {}))
        model_hash = service_metadata.get('service_api_source', '')
        upsrt_service_metadata_params = [service_row_id, org_id, service_id, service_metadata['display_name'],
                                         model_hash, desc, short_desc, url, json_str,
                                         service_metadata['encoding'], service_metadata['service_type'],
                                         service_metadata['mpe_address'], assets_hash, assets_url_str,
                                         '{"rating": 0.0 , "total_users_rated": 0 }', contributors,
                                         datetime.utcnow(), datetime.utcnow(),service_row_id,
                                         service_metadata['display_name'], model_hash,
                                         desc, short_desc, url, json_str, service_metadata['encoding'],
                                         service_metadata['service_type'], service_metadata['mpe_address'],
                                         datetime.utcnow(), assets_hash, assets_url_str, contributors]

        self.connection.execute(upsrt_servicec_metadata, upsrt_service_metadata_params)

    def create_endpoints(self, service_row_id, org_id, service_id, endpt_data):
        insert_endpoints = "INSERT INTO service_endpoint (service_row_id, org_id, service_id, group_id, endpoint, " \
                           "is_available, row_created, row_updated) " \
                           "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        is_available = 1
        insert_endpoint_paramteres = [service_row_id, org_id, service_id, endpt_data['group_id'],
                                      endpt_data['endpoint'], is_available, datetime.utcnow(), datetime.utcnow()]
        return self.connection.execute(insert_endpoints, insert_endpoint_paramteres)

    def create_tags(self, service_row_id, org_id, service_id, tag_name):
        insrt_tag = "INSERT INTO service_tags (service_row_id, org_id, service_id, tag_name, row_created, row_updated) " \
                    "VALUES(%s, %s, %s, %s, %s, %s) " \
                    "ON DUPLICATE KEY UPDATE tag_name = %s, row_updated = %s "
        insrt_tag_params = [service_row_id, org_id, service_id,
                            tag_name, datetime.utcnow(), datetime.utcnow(), tag_name, datetime.utcnow()]
        # logger.info(f'insrt_tag_params: {" ".join(insrt_tag_params)}')
        qry_res = self.connection.execute(insrt_tag, insrt_tag_params)
        logger.info(f'_create_tags::qry_res: {qry_res}')

    def delete_tags(self, org_id, service_id):
        delete_service_tags = 'DELETE FROM service_tags WHERE service_id = %s AND org_id = %s '
        self.connection.execute(delete_service_tags, [service_id, org_id])

    def delete_service_dependents(self, org_id, service_id):
        self.delete_service_group(org_id, service_id)
        self.delete_tags(org_id=org_id, service_id=service_id)
        self.delete_service_group(org_id=org_id, service_id=service_id)
        self.delete_service_endpoint(org_id=org_id, service_id=service_id)

    def delete_service_endpoint(self, org_id, service_id):

        delete_service_endpoint = 'DELETE FROM service_endpoint WHERE service_id = %s AND org_id = %s '
        self.connection.execute(
            delete_service_endpoint, [service_id, org_id])

    def delete_service_group(self, org_id, service_id):
        delete_service_groups = 'DELETE FROM service_group WHERE service_id = %s AND org_id = %s '
        self.connection.execute(delete_service_groups, [service_id, org_id])

    def delete_service(self, org_id, service_id):
        delete_service = 'DELETE FROM service WHERE service_id = %s AND org_id = %s '
        self.connection.execute(delete_service, [service_id, org_id])

    def get_service_row_id(self, org_id, service_id):
        query = 'SELECT row_id FROM service WHERE service_id = %s AND org_id = %s '
        service_data = self.connection.execute(query, [service_id, org_id])
        return service_data

    def get_service(self,org_id,service_id):
        query = 'SELECT org_id, service_id, service_path, hash_uri, is_curated FROM service WHERE service_id = %s AND org_id = %s '
        query_response = self.connection.execute(query, [service_id, org_id])

        return query_response[0]

    def get_services(self, org_id):
        query = 'SELECT * FROM service WHERE org_id = %s '
        service_data = self.connection.execute(query, (org_id))

        return service_data

    def get_service_metadata(self, service_id, org_id):
        query = ("select org_id, service_id, display_name, description, short_description,url, json, model_hash, "
                 "encoding, `type`, mpe_address, assets_url, assets_hash, service_rating, ranking, contributors from "
                 "service_metadata where service_id = %s and org_id = %s ")
        service_metadata = self.connection.execute(query, (service_id, org_id))

        if len(service_metadata) > 0:
            return service_metadata[0]
        return None

    def get_service_endpoints(self, service_id, org_id):
        query = "Select  org_id, service_id, group_id, endpoint from service_endpoint where service_id = %s and org_id = %s "
        service_endpoints = self.connection.execute(query, (service_id, org_id))

        return service_endpoints

    def get_service_tags(self, service_id, org_id):
        query = "Select   org_id, service_id, tag_name from service_tags where service_id = %s and org_id = %s "
        service_tags = self.connection.execute(query, (service_id, org_id))

        return service_tags

    def create_group(self, service_row_id, org_id, service_id, grp_data):
        insert_group = "INSERT INTO service_group (service_row_id, org_id, service_id, group_id, group_name," \
                       "pricing,free_call_signer_address,free_calls,row_updated, row_created)" \
                       "VALUES(%s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s)"
        insert_group_param = [service_row_id, org_id, service_id, grp_data['group_id'], grp_data['group_name'],
                              grp_data['pricing'],grp_data.get("free_call_signer_address","") ,grp_data.get("free_calls",0),datetime.utcnow(), datetime.utcnow()]

        return self.connection.execute(insert_group, insert_group_param)

    def get_service_group(self, org_id, service_id):
        select_group_query = """
        SELECT  org_id, service_id, group_id, group_name, pricing,free_call_signer_address,free_calls
            FROM service_group WHERE service_id = %s AND org_id = %s;
        """

        query_response = self.connection.execute(select_group_query, [service_id, org_id])

        return query_response[0]

    def curate_service(self, org_id, service_id, curate):
        update_curation_query = "UPDATE service SET is_curated = %s where org_id = %s and service_id = %s"
        try:
            self.connection.execute(update_curation_query, [curate, org_id, service_id])
            self.commit_transaction()
        except:
            self.rollback_transaction()
            raise

    def get_service_media(self,service_id, org_id):
        query = ("SELECT `row_id`, org_id, service_id, url, `order`, file_type, asset_type, alt_text, hash_uri "
                 "FROM service_media where service_id = %s and org_id = %s order by `order` ")
        service_media = self.connection.execute(query, (service_id, org_id))

        if len(service_media) > 0:
            return service_media
        return None

    def insert_service_media(self,org_id, service_id, service_row_id, media_data):
        url = media_data.get('url',"")
        hash_uri = media_data.get('hash_uri',"")
        order = media_data.get('order',0)
        file_type = media_data.get('file_type',"")
        asset_type = media_data.get('asset_type',"")
        alt_text = media_data.get('alt_text',"")

        query = ("INSERT INTO service_media (org_id, service_id, url, `order`, file_type, asset_type, alt_text, hash_uri, "
                 "service_row_id ,created_on, updated_on) VALUES(%s, %s, %s, %s, %s, %s, %s, %s,%s, %s,%s)")
        insert_media_parameters = (org_id,service_id,url,order,file_type,asset_type,alt_text,
                                   hash_uri,service_row_id,datetime.now(),datetime.now())

        self.connection.execute(query,insert_media_parameters)

    def delete_service_media(self, org_id, service_id, file_types=None):
        delete_service_media = 'DELETE FROM service_media WHERE service_id = %s AND org_id = %s '
        parameters = (service_id, org_id)
        if file_types:
            delete_service_media = delete_service_media +  " AND file_type IN %s"
            parameters = (service_id, org_id, file_types)
        self.connection.execute(delete_service_media, parameters)

