import json
import os
import tempfile
import uuid
import boto3

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.repository import Repository
from common.utils import download_file_from_url, extract_zip_file, make_tarfile
from contract_api.application.schemas.consumer_schemas import RegistryEventConsumerRequest
from contract_api.config import (
    GET_SERVICE_FROM_ORGID_SERVICE_ID_REGISTRY_ARN,
    NETWORKS,
    NETWORK_ID,
    REGION_NAME,
    ASSET_TEMP_EXTRACT_DIRECTORY,
    ASSETS_COMPONENT_BUCKET_NAME,
    MANAGE_PROTO_COMPILATION,
    CONTRACT_BASE_PATH,
    TOKEN_NAME,
    STAGE
)
from contract_api.application.consumers.event_consumer import EventConsumer
from contract_api.application.consumers.organization_event_consumer import (
    OrganizationDeletedEventConsumer,
    OrganizationCreatedEventConsumer
)
from contract_api.dao.organization_repository import OrganizationRepository
from contract_api.dao.service_repository import ServiceRepository
from contract_api.domain.models.service_media import ServiceMedia
from contract_api.infrastructure.repositories.service_media_repository import ServiceMediaRepository
from contract_api.infrastructure.repositories.service_repository import ServiceRepository as NewServiceRepository


logger = get_logger(__name__)
new_service_repo = NewServiceRepository()
service_media_repo = ServiceMediaRepository()


class ServiceEventConsumer(EventConsumer):
    def __init__(self):
        super().__init__()
        self._connection = Repository(NETWORK_ID, NETWORKS = NETWORKS)
        self._service_repository = ServiceRepository(self._connection)
        self._organization_repository = OrganizationRepository(self._connection)

class ServiceCreatedEventConsumer(ServiceEventConsumer):

    def __init__(self):
        super().__init__()

    def on_event(self, request: RegistryEventConsumerRequest):
        org_id = request.org_id
        service_id = request.service_id
        metadata_uri = request.metadata_uri
        service_metadata = self._storage_provider.get(metadata_uri)
        service_mpe_address = service_metadata.get("mpe_address")

        mpe_contract_path = os.path.abspath(f"{CONTRACT_BASE_PATH}/node_modules/singularitynet-platform-contracts/networks/MultiPartyEscrow.json")
        current_mpe_address = self._blockchain_util.read_contract_address(
            net_id=NETWORK_ID,
            path = mpe_contract_path,
            token_name=TOKEN_NAME,
            stage=STAGE,
            key="address"
        )

        if service_mpe_address != current_mpe_address:
            logger.info("Service's MPE address is not the same as the current MPE address.")
            try:
                service_data = self._service_repository.get_service(org_id, service_id)
                logger.info(f"Deleting service {service_id} from org {org_id}")
                ServiceDeletedEventConsumer().on_event(
                    request = None,
                    org_id = service_data['org_id'],
                    service_id = service_data['service_id']
                )
            except Exception:
                logger.info(f"No service found with org_id {org_id} and service_id {service_id}")

            org_data = self._organization_repository.get_organization(org_id)
            if org_data is None:
                logger.info(f"No organization found with org_id {org_id}")
                return
            org_services = self._service_repository.get_services(org_id)
            if len(org_services) == 0:
                logger.info(f"Deleting organization {org_id} because of the lack of services.")
                OrganizationDeletedEventConsumer().on_event(request = None, org_id = org_id)
            else:
                logger.info(f"Organization {org_id} still has services. Skipping deletion.")
            return
        else:
            logger.info(f"Service's MPE address is the same as the current MPE address. Checking organization {org_id}.")
            org_data = self._organization_repository.get_organization(org_id)
            if org_data is None:
                logger.info(f"No organization found with org_id {org_id}. Creating it.")
                OrganizationCreatedEventConsumer().on_event(request = None, org_id = org_id)
            else:
                logger.info(f"Organization {org_id} already exists. Skipping addition.")

        self._process_service_data(org_id, service_id, metadata_uri, service_metadata)

    def _get_new_assets_url(self, org_id, service_id, new_ipfs_data, existing_service_metadata):
        new_assets_hash = new_ipfs_data.get("assets", {})
        existing_assets_hash = {}
        existing_assets_url = {}

        if existing_service_metadata:
            existing_assets_hash = json.loads(existing_service_metadata["assets_hash"])
            existing_assets_url = json.loads(existing_service_metadata["assets_url"])
        assets_url_mapping = self._compare_assets_and_push_to_s3(
            existing_assets_hash, new_assets_hash, existing_assets_url, org_id, service_id
        )

        return assets_url_mapping

    def create_service_media(self, org_id, service_id, service_media):
        count = 0
        if len(service_media) > 0:
            service = new_service_repo.get_service(org_id=org_id, service_id=service_id)
            if not service:
                raise Exception(f"Unable to find service for given org_id {org_id} and service_id {service_id}")
            service_media_list = []
            for service_media_item in service_media:
                if service_media_item.get('file_type') in ['image', 'video']:
                    url = service_media_item.get("url", {})
                    if utils.if_external_link(link=url):
                        updated_url = url
                        hash_uri = ''
                    else:
                        updated_url = self._push_asset_to_s3_using_hash(org_id=org_id, service_id=service_id, hash_uri=url)
                        hash_uri = service_media_item.get("url", "")
                    # insert service media data
                    asset_type = 'media_gallery' if service_media_item.get('asset_type', {}) != 'hero_image' else service_media_item.get('asset_type')
                    media_item = ServiceMedia(
                        service_row_id=service.row_id,
                        org_id=org_id,
                        service_id=service_id,
                        url=updated_url,
                        file_type=service_media_item['file_type'],
                        order=service_media_item['order'],
                        asset_type=asset_type,
                        alt_text=service_media_item.get('alt_text', ""),
                        hash_uri=hash_uri
                    )
                    service_media_list.append(media_item)
                    if service_media_item.get('order', 0) > count:
                        count = service_media_item.get('order', 0)
            service_media_repo.update_service_media(org_id=org_id, service_id=service_id,
                                                    service_media_list=service_media_list,
                                                    asset_types=['hero_image', 'media_gallery']
                                                    )

    def _process_service_data(self, org_id, service_id, new_hash, new_data):
        try:
            self._connection.begin_transaction()
            existing_service_metadata = self._service_repository.get_service_metadata(org_id, service_id)
            logger.info(f"Existing service metadata :: {existing_service_metadata}")

            assets_url = self._get_new_assets_url(org_id, service_id, new_data, existing_service_metadata)    
            logger.info(f"Get new assets url :: {assets_url}")

            self._service_repository.delete_service_dependents(org_id=org_id, service_id=service_id)
        
            service_data = self._service_repository.create_or_update_service(org_id, service_id, new_hash)
            service_row_id = service_data['last_row_id']
            logger.info(f"Created service with service :: {service_row_id}")

            self._service_repository.curate_service(org_id, service_id, 1)
            logger.info(f"Curated service with service :: {service_row_id}")

            self._service_repository.create_or_update_service_metadata(
                service_row_id=service_row_id,
                org_id=org_id,
                service_id=service_id,
                service_metadata=new_data,
                assets_url=assets_url
            )

            groups = new_data.get("groups", [])
            group_insert_count = 0
            for group in groups:
                service_group_data = self._service_repository.create_group(
                    service_row_id=service_row_id, org_id=org_id,
                    service_id=service_id,
                    grp_data = {
                        "free_calls": group.get("free_calls", 0),
                        "free_call_signer_address": group.get("free_call_signer_address", ""),
                        "group_id": group["group_id"],
                        "group_name": group["group_name"],
                        "pricing": json.dumps(group["pricing"])
                    }
                )
                group_insert_count = group_insert_count + service_group_data[0]
                endpoints = group.get("endpoints", [])
                endpoint_insert_count = 0
                for endpoint in endpoints:
                    service_data = self._service_repository.create_endpoints(
                        service_row_id=service_row_id,
                        org_id=org_id,
                        service_id=service_id,
                        endpt_data={
                            "endpoint": endpoint,
                            "group_id": group["group_id"],
                        }
                    )
                    endpoint_insert_count = endpoint_insert_count + service_data[0]

            tags_data = new_data.get("tags", [])
            # logger.info(f"Tags data: {' '.join(tags_data)}")
            for tag in tags_data:
                self._service_repository.create_tags(service_row_id=service_row_id, org_id=org_id,
                                                     service_id=service_id,
                                                     tag_name=tag,
                                                     )

            service_media = new_data.get("media", [])
            self.create_service_media(org_id=org_id, service_id=service_id,
                                      service_media=service_media)

            update_proto_stubs = False
            if not existing_service_metadata or (
                    existing_service_metadata["model_hash"] != new_data["service_api_source"]):
                update_proto_stubs = True

            self._connection.commit_transaction()

        except Exception as e:
            self._connection.rollback_transaction()
            raise e

        ServiceCreatedDeploymentEventHandler().process_service_deployment(
            org_id=org_id,
            service_id=service_id,
            proto_hash=new_data["service_api_source"],
            update_proto_stubs=update_proto_stubs
        )


class ServiceMetadataModifiedConsumer(ServiceCreatedEventConsumer):
    pass


class ServiceDeletedEventConsumer(ServiceEventConsumer):
    def __init__(self):
        super().__init__()

    def on_event(self, request: RegistryEventConsumerRequest, org_id=None, service_id=None):
        if org_id is None or service_id is None:
            org_id = request.org_id
            service_id = request.service_id
        self._service_repository.delete_service_dependents(org_id, service_id)
        self._service_repository.delete_service(org_id, service_id)


class ServiceCreatedDeploymentEventHandler(ServiceEventConsumer):

    def __init__(self):
        super().__init__()
        self.lambda_client = boto3.client("lambda", region_name=REGION_NAME)

    def on_event(self, request: RegistryEventConsumerRequest):
        org_id = request.org_id
        service_id = request.service_id
        self.process_service_deployment(org_id=org_id, service_id=service_id, update_proto_stubs=None, proto_hash=None)

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

    @staticmethod
    def compile_proto_stubs(org_id, service_id):
        boto_utils = BotoUtils(region_name=REGION_NAME)
        base_url = f"s3://{ASSETS_COMPONENT_BUCKET_NAME}/assets/{org_id}/{service_id}/proto.tar.gz"
        output_url = f"s3://{ASSETS_COMPONENT_BUCKET_NAME}/assets/{org_id}/{service_id}/"
        lambda_payload = {
            "input_s3_path": base_url,
            "output_s3_path": output_url,
            "org_id": org_id,
            "service_id": service_id
        }
        response = boto_utils.invoke_lambda(
            invocation_type="RequestResponse",
            lambda_function_arn=MANAGE_PROTO_COMPILATION,
            payload=json.dumps(lambda_payload)
        )
        generated_stubs_url = []
        if response['statusCode'] == 200:
            output_bucket, output_key = boto_utils.get_bucket_and_key_from_url(url=f"{output_url}stubs")
            stub_objects = boto_utils.get_objects_from_s3(bucket=output_bucket, key=output_key)
            for object in stub_objects:
                generated_stubs_url.append(f"https://{output_bucket}.s3.{REGION_NAME}.amazonaws.com/{object['Key']}")
            return generated_stubs_url
        else:
            msg = f"Error generating stubs :: {response}"
            logger.info(msg)
            raise Exception(msg)

    @staticmethod
    def update_proto_stubs(org_id, service_id, proto_stubs):
        service = new_service_repo.get_service(org_id=org_id, service_id=service_id)
        if not service:
            raise Exception(f"Unable to find service for given org_id {org_id} and service_id {service_id}")
        proto_media_list = []
        for stub in proto_stubs:
            filename, extension = utils.get_file_name_and_extension_from_path(path=stub)
            media_item = ServiceMedia(
                service_row_id=service.row_id,
                org_id=org_id,
                service_id=service_id,
                url=stub,
                file_type="grpc-stub",
                order=0,
                asset_type=f"grpc-stub/{filename}",
                alt_text="",
                hash_uri=""
            )
            proto_media_list.append(media_item)
        service_media_repo.update_service_media(org_id=org_id, service_id=service_id,
                                                service_media_list=proto_media_list,
                                                asset_types=['grpc-stub/nodejs', 'grpc-stub/python']
                                                )

    def upload_proto_file_from_hash_to_bucket(self, org_id, service_id, asset_hash):
        temp_dir = tempfile.gettempdir()

        base_path = os.path.join(temp_dir, str(uuid.uuid1()))
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        temp_output_path = os.path.join(base_path, 'proto.tar.gz')

        io_bytes = self._storage_provider.get(asset_hash, to_decode = False)
        with open(temp_output_path, 'wb') as outfile:
            outfile.write(io_bytes)

        self._s3_util.push_file_to_s3(temp_output_path, ASSETS_COMPONENT_BUCKET_NAME,
                                      f"assets/{org_id}/{service_id}/proto.tar.gz")

    def process_service_deployment(self, org_id, service_id, update_proto_stubs, proto_hash):
        logger.info(f"Processing Service deployment for {org_id} {service_id}")
        if update_proto_stubs:
            self.upload_proto_file_from_hash_to_bucket(org_id=org_id, service_id=service_id, asset_hash=proto_hash)
            proto_stubs = self.compile_proto_stubs(org_id=org_id, service_id=service_id)
            self.update_proto_stubs(org_id=org_id, service_id=service_id, proto_stubs=proto_stubs)
