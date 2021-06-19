import json
import os

import boto3
from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.boto_utils import BotoUtils
from common.ipfs_util import IPFSUtil
from common.logger import get_logger
from common.repository import Repository
from common.s3_util import S3Util
from common.utils import download_file_from_url, extract_zip_file, make_tarfile
from contract_api.config import ASSETS_BUCKET_NAME, ASSETS_PREFIX, GET_SERVICE_FROM_ORGID_SERVICE_ID_REGISTRY_ARN, \
    MARKETPLACE_DAPP_BUILD, NETWORKS, NETWORK_ID, REGION_NAME, S3_BUCKET_ACCESS_KEY, S3_BUCKET_SECRET_KEY, \
    ASSET_TEMP_EXTRACT_DIRECTORY, ASSETS_COMPONENT_BUCKET_NAME, MANAGE_PROTO_COMPILATION
from contract_api.consumers.event_consumer import EventConsumer
from contract_api.dao.service_repository import ServiceRepository

logger = get_logger(__name__)


class ServiceEventConsumer(EventConsumer):
    _connection = Repository(NETWORK_ID, NETWORKS=NETWORKS)
    _service_repository = ServiceRepository(_connection)

    def __init__(self, ws_provider, ipfs_url, ipfs_port):
        self._blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)
        self._s3_util = S3Util(S3_BUCKET_ACCESS_KEY, S3_BUCKET_SECRET_KEY)
        self._ipfs_util = IPFSUtil(ipfs_url, ipfs_port)

    def on_event(self, event):
        pass

    def _get_org_id_from_event(self, event):
        event_data = event['data']
        service_data = eval(event_data['json_str'])
        org_id_bytes = service_data['orgId']
        org_id = Web3.toText(org_id_bytes).rstrip("\x00")
        return org_id

    def _get_service_id_from_event(self, event):
        event_data = event['data']
        service_data = eval(event_data['json_str'])
        service_id_bytes = service_data['serviceId']
        service_id = Web3.toText(service_id_bytes).rstrip("\x00")
        return service_id

    def _get_metadata_uri_from_event(self, event):
        event_data = event['data']
        service_data = eval(event_data['json_str'])
        metadata_uri = Web3.toText(service_data['metadataURI'])[7:].rstrip("\u0000")
        return metadata_uri

    def _get_registry_contract(self):
        net_id = NETWORK_ID
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'node_modules', 'singularitynet-platform-contracts'))
        registry_contract = self._blockchain_util.get_contract_instance(base_contract_path, "REGISTRY", net_id)
        return registry_contract

    def _get_service_details_from_blockchain(self, event):
        logger.info(f"processing service event {event}")
        org_id = self._get_org_id_from_event(event)
        service_id = self._get_service_id_from_event(event)
        return org_id, service_id


class ServiceCreatedEventConsumer(ServiceEventConsumer):

    def on_event(self, event):
        org_id, service_id = self._get_service_details_from_blockchain(event)
        metadata_uri = self._get_metadata_uri_from_event(event)
        service_ipfs_data = self._ipfs_util.read_file_from_ipfs(metadata_uri)
        self._process_service_data(org_id=org_id, service_id=service_id, new_ipfs_hash=metadata_uri,
                                   new_ipfs_data=service_ipfs_data)

    def _push_asset_to_s3_using_hash(self, hash, org_id, service_id):
        io_bytes = self._ipfs_util.read_bytesio_from_ipfs(hash)
        filename = hash.split("/")[1]
        if service_id:
            s3_filename = ASSETS_PREFIX + "/" + org_id + "/" + service_id + "/" + filename
        else:
            s3_filename = ASSETS_PREFIX + "/" + org_id + "/" + filename

        new_url = self._s3_util.push_io_bytes_to_s3(s3_filename,
                                                    ASSETS_BUCKET_NAME, io_bytes)
        return new_url

    def _get_new_assets_url(self, org_id, service_id, new_ipfs_data, existing_service_metadata):
        new_assets_hash = new_ipfs_data.get('assets', {})
        existing_assets_hash = {}
        existing_assets_url = {}

        if existing_service_metadata:
            existing_assets_hash = json.loads(existing_service_metadata["assets_hash"])
            existing_assets_url = json.loads(existing_service_metadata["assets_url"])
        assets_url_mapping = self._comapre_assets_and_push_to_s3(existing_assets_hash, new_assets_hash,
                                                                 existing_assets_url, org_id,
                                                                 service_id)
        return assets_url_mapping

    def insert_proto_stubs(self, org_id, service_id, proto_stubs, service_row_id):
        if proto_stubs:
            self._service_repository.delete_service_media(org_id=org_id, service_id=service_id, file_types = ['grpc_stub'])
        for stub in proto_stubs:
            stub_item = {
                "url": stub,
                "file_type": "grpc_stub",
                "asset_type": "stub",
            }
            self._service_repository.insert_service_media(org_id=org_id, service_id=service_id,
                                                          service_row_id=service_row_id,
                                                          media_data=stub_item)


    def create_service_media(self,org_id,service_id,service_media,service_row_id):
        count = 0;
        if len(service_media)>0:
            #clear the existing values from db
            self._service_repository.delete_service_media(org_id=org_id,service_id=service_id, file_types=['image','video'])
            #fif ipfs_url store in s3 and update url else store url
            for service_media_item in service_media:
                url = service_media_item.get("url",{})
                if "http" in url or "https" in url:
                    updated_url = url
                    ipfs_url = ''
                else:
                    updated_url = self._push_asset_to_s3_using_hash(org_id=org_id,service_id=service_id,hash=url)
                    ipfs_url = service_media_item.get("url","")
                #insert service media data
                service_media_data = {
                    "url":updated_url,
                    "file_type":service_media_item['file_type'],
                    "order":service_media_item['order'],
                    "asset_type":service_media_item.get('asset_type',""),
                    "alt_text":service_media_item.get('alt_text',""),
                    "ipfs_url":ipfs_url
                }
                self._service_repository.insert_service_media(org_id=org_id,service_id=service_id,service_row_id=service_row_id,media_data=service_media_data)
                if service_media_item.get('order',0) > count:
                    count = service_media_item.get('order',0)

    def _compile_proto_stubs(self, org_id, service_id):
        boto_utils = BotoUtils(region_name=REGION_NAME)
        base_url = f"s3://{ASSETS_COMPONENT_BUCKET_NAME}/assets/{org_id}/{service_id}/proto.tar.gz"
        output_url = f"s3://{ASSETS_COMPONENT_BUCKET_NAME}/assets/{org_id}/{service_id}/stubs/"
        lambda_payload = {
            "input_s3_path": base_url,
            "output_s3_path": output_url
        }
        response = boto_utils.invoke_lambda(
            invocation_type="RequestResponse",
            lambda_function_arn=MANAGE_PROTO_COMPILATION,
            payload=json.dumps(lambda_payload)
        )
        generated_stubs_url = []
        if response['statusCode'] == 200:
            output_bucket, output_key = boto_utils.get_bucket_and_key_from_url(url=output_url)
            stub_objects = boto_utils.get_objects_from_s3(bucket=output_bucket, key=output_key)
            for object in stub_objects:
                generated_stubs_url.append(f"https://{output_bucket}.s3.{REGION_NAME}.amazonaws.com/{object['Key']}")
            return generated_stubs_url
        else:
            msg = f"Error generating stubs :: {response}"
            logger.info(msg)
            raise Exception(msg)

    def _process_service_data(self, org_id, service_id, new_ipfs_hash, new_ipfs_data):
        try:

            self._connection.begin_transaction()

            existing_service_metadata = self._service_repository.get_service_metadata(org_id=org_id,
                                                                                      service_id=service_id)

            assets_url = self._get_new_assets_url(
                org_id, service_id, new_ipfs_data, existing_service_metadata)

            self._service_repository.delete_service_dependents(
                org_id=org_id, service_id=service_id)
            service_data = self._service_repository.create_or_update_service(
                org_id=org_id, service_id=service_id, ipfs_hash=new_ipfs_hash)
            service_row_id = service_data['last_row_id']
            logger.debug(f"Created service with service {service_row_id}")
            self._service_repository.create_or_update_service_metadata(service_row_id=service_row_id, org_id=org_id,
                                                                       service_id=service_id,
                                                                       ipfs_data=new_ipfs_data, assets_url=assets_url)


            groups = new_ipfs_data.get('groups', [])
            group_insert_count = 0
            for group in groups:
                service_group_data = self._service_repository.create_group(service_row_id=service_row_id, org_id=org_id,
                                                                           service_id=service_id,
                                                                           grp_data={
                                                                               'free_calls': group.get("free_calls", 0),
                                                                               'free_call_signer_address': group.get(
                                                                                   "free_call_signer_address", ""),
                                                                               'group_id': group['group_id'],
                                                                               'group_name': group['group_name'],
                                                                               'pricing': json.dumps(group['pricing'])
                                                                           })
                group_insert_count = group_insert_count + service_group_data[0]
                endpoints = group.get('endpoints', [])
                endpoint_insert_count = 0
                for endpoint in endpoints:
                    service_data = self._service_repository.create_endpoints(service_row_id=service_row_id,
                                                                             org_id=org_id,
                                                                             service_id=service_id,
                                                                             endpt_data={
                                                                                 'endpoint': endpoint,
                                                                                 'group_id': group['group_id'],
                                                                             })
                    endpoint_insert_count = endpoint_insert_count + service_data[0]

            tags_data = new_ipfs_data.get("tags", [])
            for tag in tags_data:
                self._service_repository.create_tags(service_row_id=service_row_id, org_id=org_id,
                                                     service_id=service_id,
                                                     tag_name=tag,
                                                     )

            service_media = new_ipfs_data.get('media', [])
            self.create_service_media(org_id=org_id, service_id=service_id,
                                      service_media=service_media, service_row_id=service_row_id)
            proto_stubs = []
            if not existing_service_metadata or (
                    existing_service_metadata["model_ipfs_hash"] != new_ipfs_data["model_ipfs_hash"]):
                proto_stubs = self._compile_proto_stubs(org_id=org_id, service_id=service_id)
            self.insert_proto_stubs(org_id=org_id, service_id=service_id, proto_stubs=proto_stubs,
                                    service_row_id=service_row_id)

            self._connection.commit_transaction()

        except Exception as e:
            self._connection.rollback_transaction()
            raise e


class ServiceMetadataModifiedConsumer(ServiceCreatedEventConsumer):
    pass


class SeviceDeletedEventConsumer(ServiceEventConsumer):

    def on_event(self, event):
        org_id, service_id = self._get_service_details_from_blockchain(event)
        self._service_repository.delete_service_dependents(org_id, service_id)
        self._service_repository.delete_service(
            org_id=org_id, service_id=service_id)


class ServiceCreatedDeploymentEventHandler(ServiceEventConsumer):

    def __init__(self, ws_provider, ipfs_url, ipfs_port):
        super().__init__(ws_provider, ipfs_url, ipfs_port)
        self.lambda_client = boto3.client("lambda", region_name=REGION_NAME)

    def on_event(self, event):
        org_id, service_id = self._get_service_details_from_blockchain(event)
        self._process_service_deployment(org_id=org_id, service_id=service_id)

    def _extract_zip_and_and_tar(self, org_id, service_id, s3_url):
        root_directory = ASSET_TEMP_EXTRACT_DIRECTORY
        zip_directory = root_directory + org_id + "/" + service_id
        extracted_zip_directory = root_directory + "extracted/" + org_id + "/" + service_id

        zip_file_name = download_file_from_url(s3_url, zip_directory)
        zip_file_path = zip_directory + "/" + zip_file_name
        extracted_file_path = extracted_zip_directory + "/" + zip_file_name.split(".")[0].split("_")[1]
        extract_zip_file(zip_file_path, extracted_file_path)

        tar_file_path = extracted_file_path + ".tar.gz"
        make_tarfile(tar_file_path, extracted_file_path)

        return tar_file_path

    def _get_s3_path_url_for_proto_and_component(self, org_id, service_id):
        proto_file_s3_path = ""
        component_files_s3_path = ""
        lambda_payload = {
            "httpMethod": "GET",
            "queryStringParameters": {
                "org_id": org_id,
                "service_id": service_id
            },
        }
        response = self.lambda_client.invoke(
            FunctionName=GET_SERVICE_FROM_ORGID_SERVICE_ID_REGISTRY_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(lambda_payload),
        )

        result = json.loads(response.get('Payload').read())

        response = json.loads(result['body'])

        if response["status"] == "success":
            media = response["data"].get("media", {})
            proto_file_s3_path = media.get("proto_files", {}).get("url", None)
            component_files_s3_path = media.get("demo_files", {}).get("url", None)

        return proto_file_s3_path, component_files_s3_path

    def _trigger_code_build_for_marketplace_dapp(self, org_id, service_id):
        cb = boto3.client('codebuild')
        build = {
            'projectName': MARKETPLACE_DAPP_BUILD,
            'environmentVariablesOverride': [
                {
                    'name': 'org_id',
                    'value': f"{org_id}",
                    'type': 'PLAINTEXT'
                },
                {
                    'name': 'service_id',
                    'value': f"{service_id}",
                    'type': 'PLAINTEXT'
                },
            ]
        }

        try:
            build = cb.start_build(**build)

            logger.info('Codebuild returned: {}'.format(build))
        except Exception as e:
            logger.error(f"Failed BUild for {org_id} {service_id}")
            raise e

    def _process_service_deployment(self, org_id, service_id):
        logger.info(f"Processing Service deployment for {org_id} {service_id}")
        proto_file_s3_path, component_files_s3_path = self._get_s3_path_url_for_proto_and_component(org_id, service_id)

        if proto_file_s3_path:
            proto_file_tar_path = self._extract_zip_and_and_tar(org_id, service_id, proto_file_s3_path)
            self._s3_util.push_file_to_s3(proto_file_tar_path, ASSETS_COMPONENT_BUCKET_NAME,
                                          f"assets/{org_id}/{service_id}/{proto_file_tar_path.split('/')[-1]}")
        if component_files_s3_path:
            component_files_tar_path = self._extract_zip_and_and_tar(org_id, service_id, component_files_s3_path)
            self._s3_util.push_file_to_s3(component_files_tar_path, ASSETS_COMPONENT_BUCKET_NAME,
                                          f"assets/{org_id}/{service_id}/{component_files_tar_path.split('/')[-1]}")

        self._trigger_code_build_for_marketplace_dapp(org_id, service_id)
