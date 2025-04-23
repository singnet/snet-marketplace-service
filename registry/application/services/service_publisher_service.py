import os
import json
import tempfile
from datetime import datetime as dt
from typing import Dict, Union
from urllib.request import urlretrieve
from uuid import uuid4

from deepdiff import DeepDiff
from aws_xray_sdk.core import patch_all
from cerberus import Validator

from common import utils
from common.boto_utils import BotoUtils
from common.blockchain_util import BlockChainUtil
from common.constant import StatusCode
from common.logger import get_logger
from common.utils import send_email_notification
from registry.config import (
    IPFS_URL,
    METADATA_FILE_PATH,
    NETWORKS,
    NETWORK_ID,
    NOTIFICATION_ARN,
    REGION_NAME,
    PUBLISH_OFFCHAIN_ATTRIBUTES_ARN,
    GET_SERVICE_FOR_GIVEN_ORG_ARN,
    STAGE
)
from registry.constants import (
    EnvironmentType,
    ServiceAvailabilityStatus,
    ServiceStatus,
    ServiceSupportType,
    UserType,
    ServiceType,
    REG_ADDR_PATH
)
from registry.domain.factory.service_factory import ServiceFactory
from registry.domain.models.demo_component import DemoComponent
from registry.domain.models.offchain_service_config import OffchainServiceConfig
from registry.domain.models.service import Service
from registry.domain.models.organization import Organization
from registry.domain.models.service_comment import ServiceComment
from registry.exceptions import (
    EnvironmentNotFoundException,
    InvalidServiceStateException,
    OrganizationNotFoundException,
    ServiceNotFoundException,
    ServiceProtoNotFoundException,
    InvalidMetadataException
)
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
from registry.infrastructure.storage_provider import validate_storage_provider, StorageProvider, StorageProviderType, \
    FileUtils

patch_all()
ALLOWED_ATTRIBUTES_FOR_SERVICE_SEARCH = ["display_name"]
DEFAULT_ATTRIBUTE_FOR_SERVICE_SEARCH = "display_name"
ALLOWED_ATTRIBUTES_FOR_SERVICE_SORT_BY = ["ranking", "service_id"]
DEFAULT_ATTRIBUTES_FOR_SERVICE_SORT_BY = "ranking"
ALLOWED_ATTRIBUTES_FOR_SERVICE_ORDER_BY = ["asc", "desc"]
DEFAULT_ATTRIBUTES_FOR_SERVICE_ORDER_BY = "desc"
DEFAULT_OFFSET = 0
DEFAULT_LIMIT = 0
BUILD_FAILURE_CODE = 0

logger = get_logger(__name__)
service_factory = ServiceFactory()
boto_util = BotoUtils(region_name=REGION_NAME)
validator = Validator()


class ServicePublisherService:
    def __init__(self, username: str, org_uuid: str, service_uuid: str, lighthouse_token: Union[str, None] = None):
        self._username = username
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid
        self._storage_provider = StorageProvider(lighthouse_token)

    def service_build_status_notifier(self, org_id, service_id, build_status):
        if build_status == BUILD_FAILURE_CODE:
            BUILD_FAIL_MESSAGE = "Build failed please check your components"
            org_uuid, service = ServicePublisherRepository() \
                .get_service_for_given_service_id_and_org_id(org_id, service_id)

            contacts = [contributor.get("email_id", "") for contributor in service.contributors]

            service_comment = ServiceComment(org_uuid, service.uuid, "SERVICE_APPROVAL", "SERVICE_APPROVER",
                                             self._username, BUILD_FAIL_MESSAGE)
            ServicePublisherRepository().save_service_comments(service_comment)
            ServicePublisherRepository().save_service(self._username, service, ServiceStatus.CHANGE_REQUESTED.value)
            logger.info(f"Build failed for org_id {org_id}  and service_id {service_id}")
            try:
                BUILD_STATUS_SUBJECT = "Build failed for your service {}"
                BUILD_STATUS_MESSAGE = "Build failed for your org_id {} and service_id {}"
                send_email_notification(
                    contacts, BUILD_STATUS_SUBJECT.format(service_id),
                    BUILD_STATUS_MESSAGE.format(org_id, service_id), NOTIFICATION_ARN, boto_util
                )
            except Exception:
                logger.info(f"Error happened while sending build_status mail for {org_id} and contacts {contacts}")

    def get_service_id_availability_status(self, service_id):
        record_exist = ServicePublisherRepository().check_service_id_within_organization(self._org_uuid, service_id)
        if record_exist:
            return ServiceAvailabilityStatus.UNAVAILABLE.value
        return ServiceAvailabilityStatus.AVAILABLE.value

    @staticmethod
    def get_service_for_org_id_and_service_id(org_id, service_id):
        _, service = ServicePublisherRepository().get_service_for_given_service_id_and_org_id(org_id, service_id)
        if not service:
            return {}
        return service.to_dict()

    @staticmethod
    def _get_valid_service_contributors(contributors):
        for contributor in contributors:
            email_id = contributor.get("email_id", None)
            name = contributor.get("name", None)
            if (email_id is None or len(email_id) == 0) and (name is None or len(name) == 0):
                contributors.remove(contributor)
        return contributors

    def _save_service_comment(self, support_type, user_type, comment):
        service_provider_comment = ServiceFactory. \
            create_service_comment_entity_model(org_uuid=self._org_uuid,
                                                service_uuid=self._service_uuid,
                                                support_type=support_type,
                                                user_type=user_type,
                                                commented_by=self._username,
                                                comment=comment)
        ServicePublisherRepository().save_service_comments(service_provider_comment)

    def save_offline_service_configs(self, payload):
        demo_component_required = payload.get("assets", {}).get("demo_files", {}).get("required", -1)
        if demo_component_required == -1:
            return
        offchain_service_config = OffchainServiceConfig(
            org_uuid=self._org_uuid,
            service_uuid=self._service_uuid,
            configs={
                "demo_component_required": str(demo_component_required)
            }
        )
        ServicePublisherRepository().add_or_update_offline_service_config(offchain_service_config)
        return

    def save_service(self, payload):
        logger.info(f"Save service with payload :: {payload}")
        service = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        service.service_id = payload["service_id"]
        service.proto = payload.get("proto", {})
        service.storage_provider = payload.get("storage_provider", "")
        service.display_name = payload.get("display_name", "")
        service.short_description = payload.get("short_description", "")
        service.description = payload.get("description", "")
        service.project_url = payload.get("project_url", "")
        service.service_type = payload.get("service_type", ServiceType.GRPC.value)
        service.contributors = ServicePublisherService. \
            _get_valid_service_contributors(contributors=payload.get("contributors", []))
        service.tags = payload.get("tags", [])
        service.mpe_address = payload.get("mpe_address", "")
        groups = []
        for group in payload["groups"]:
            service_group = ServiceFactory.create_service_group_entity_model(self._org_uuid, self._service_uuid, group)
            groups.append(service_group)
        service.groups = groups
        service.service_state.transaction_hash = payload.get("transaction_hash", None)
        logger.info(f"Save service data with proto: {service.proto} and assets: {service.assets}")
        ServicePublisherRepository().save_service(self._username, service, ServiceStatus.APPROVED.value)
        comment = payload.get("comments", {}).get(UserType.SERVICE_PROVIDER.value, "")
        if len(comment) > 0:
            self._save_service_comment(support_type="SERVICE_APPROVAL", user_type="SERVICE_PROVIDER", comment=comment)
        self.save_offline_service_configs(payload=payload)
        service = self.get_service_for_given_service_uuid()
        return service

    def save_service_attributes(self, payload):
        VALID_PATCH_ATTRIBUTE = ["groups"]
        service_db = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid,
                                                                                     self._service_uuid)
        service = ServiceFactory.convert_service_db_model_to_entity_model(service_db)

        for attribute, value in payload.items():
            if attribute in VALID_PATCH_ATTRIBUTE:
                if attribute == "groups":
                    service.groups = [
                        ServiceFactory.create_service_group_entity_model(self._org_uuid, self._service_uuid, group) for
                        group in payload.get("groups", [])]
            else:
                raise Exception("Patching of other attributes not allowed as of now")

        saved_service = ServicePublisherRepository().save_service(self._username, service, service.service_state.state)

        return saved_service.to_dict()

    def save_transaction_hash_for_published_service(self, payload):
        service = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        if service.service_state.state == ServiceStatus.APPROVED.value:
            service.service_state = \
                ServiceFactory().create_service_state_entity_model(
                    self._org_uuid, self._service_uuid, ServiceStatus.PUBLISH_IN_PROGRESS.value,
                    payload.get("transaction_hash", ""))
            ServicePublisherRepository().save_service(self._username, service, ServiceStatus.PUBLISH_IN_PROGRESS.value)
        return StatusCode.OK

    def create_service(self, payload):
        service_uuid = uuid4().hex
        service = ServiceFactory().create_service_entity_model(self._org_uuid, service_uuid, payload,
                                                               ServiceStatus.DRAFT.value)
        logger.info(f"Creating service :: {service.to_dict()}")
        ServicePublisherRepository().add_service(service, self._username)
        return {"org_uuid": self._org_uuid, "service_uuid": service_uuid}

    def get_services_for_organization(self, payload):
        offset = payload.get("offset", DEFAULT_OFFSET)
        limit = payload.get("limit", DEFAULT_LIMIT)
        search_string = payload["q"]
        search_attribute = payload["s"]
        sort_by = payload["sort_by"].lower()
        order_by = payload["order_by"].lower()
        filter_parameters = {
            "offset": offset,
            "limit": limit,
            "search_string": search_string,
            "search_attribute": search_attribute if search_attribute in ALLOWED_ATTRIBUTES_FOR_SERVICE_SEARCH else DEFAULT_ATTRIBUTE_FOR_SERVICE_SEARCH,
            "sort_by": sort_by if sort_by in ALLOWED_ATTRIBUTES_FOR_SERVICE_SORT_BY else DEFAULT_ATTRIBUTES_FOR_SERVICE_SORT_BY,
            "order_by": order_by if order_by in ALLOWED_ATTRIBUTES_FOR_SERVICE_SORT_BY else DEFAULT_ATTRIBUTES_FOR_SERVICE_ORDER_BY
        }
        services = ServicePublisherRepository().get_services_for_organization(self._org_uuid, filter_parameters)
        search_result = [service.to_dict() for service in services]
        search_count = ServicePublisherRepository().get_total_count_of_services_for_organization(self._org_uuid,
                                                                                                 filter_parameters)
        return {"total_count": search_count, "offset": offset, "limit": limit, "result": search_result}

    def get_service_comments(self):
        service_provider_comment = ServicePublisherRepository().get_last_service_comment(
            org_uuid=self._org_uuid, service_uuid=self._service_uuid,
            support_type=ServiceSupportType.SERVICE_APPROVAL.value, user_type=UserType.SERVICE_PROVIDER.value)
        approver_comment = ServicePublisherRepository().get_last_service_comment(
            org_uuid=self._org_uuid, service_uuid=self._service_uuid,
            support_type=ServiceSupportType.SERVICE_APPROVAL.value, user_type=UserType.SERVICE_APPROVER.value)
        return {
            UserType.SERVICE_PROVIDER.value: None if not service_provider_comment else f"{service_provider_comment.comment}",
            UserType.SERVICE_APPROVER.value: "<div></div>" if not approver_comment else f"<div>{approver_comment.comment}</div>"
        }

    def map_offchain_service_config(self, offchain_service_config, service):
        # update demo component flag in service assets
        if "demo_files" not in service["media"]:
            service["media"]["demo_files"] = {}
        service["media"]["demo_files"].update({"required": offchain_service_config.configs["demo_component_required"]})
        return service

    def get_service_for_given_service_uuid(self):
        service = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        if not service:
            return None
        service.comments = self.get_service_comments()
        offchain_service_config = ServicePublisherRepository().get_offchain_service_config(
            org_uuid=self._org_uuid,
            service_uuid=self._service_uuid
        )
        service_data = service.to_dict()
        if offchain_service_config.configs:
            service_data = self.map_offchain_service_config(offchain_service_config, service_data)
        return service_data

    def publish_assets(self, service: Service, storage_provider_enum: StorageProviderType):
        """
        Publishes supported service assets to the specified storage provider.

        :param service: Service object containing assets.
        :param storage_provider_enum: Enum value for the storage provider.
        """
        ASSETS_SUPPORTED = ["hero_image", "demo_files"]
        supported_assets = {k: v for k, v in service.assets.items() if k in ASSETS_SUPPORTED}

        for asset_name, asset_data in supported_assets.items():
            try:
                asset_url = asset_data.get("url")
                if not asset_url:
                    logger.warning(f"Asset URL for '{asset_name}' is missing. Skipping...")
                    continue

                logger.info(f"Downloading asset '{asset_name}' from: {asset_url}")

                source_path = self._download_file(asset_url)
                logger.info(f"Downloaded asset '{asset_name}' to: {source_path}")

                asset_hash = self._storage_provider.publish(source_path, storage_provider_enum)
                logger.info(f"Published asset '{asset_name}'. Hash: {asset_hash}")

                service.assets[asset_name]["hash"] = asset_hash

            except Exception as e:
                logger.error(f"Failed to process asset '{asset_name}': {str(e)}")

    def publish_service_data_to_storage_provider(self, storage_provider_enum: StorageProviderType) -> Service:
        """
        Publishes the service's assets and protos to storage provider and updates the service's metadata.

        :param storage_provider_enum: Enum value for the storage provider (e.g., IPFS, Filecoin).
        :return: Updated Service object.
        :raises ServiceProtoNotFoundException: If the proto files are not found in the service assets.
        :raises InvalidServiceStateException: If the service is not in the APPROVED state.
        """
        service = self._get_approved_service()

        proto_url = service.assets.get("proto_files", {}).get("url")
        if not proto_url:
            raise ServiceProtoNotFoundException("Proto file URL not found in service assets.")

        proto_file_path = self._download_file(proto_url)
        logger.info(f"Proto file downloaded to: {proto_file_path}")

        asset_hash = self._storage_provider.publish(proto_file_path, storage_provider_enum, zip_archive=True)
        logger.info(f"Published proto files. Hash: {asset_hash}")

        return self._update_service_metadata(service, asset_hash, storage_provider_enum)

    def _get_approved_service(self) -> Service:
        """
        Fetches the service from the repository and validates its state.

        :return: Service object if it is in the APPROVED state.
        :raises InvalidServiceStateException: If the service is not in the APPROVED state.
        """
        service_repo = ServicePublisherRepository()
        service = service_repo.get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        if service.service_state.state != ServiceStatus.APPROVED.value:
            logger.error(f"Service status must be {ServiceStatus.APPROVED.value} to publish.")
            raise InvalidServiceStateException()
        return service

    def _download_file(self, url: str) -> str:
        """
        Downloads a file from the given URL to a temporary location.

        :param url: URL of the file.
        :return: Path to the downloaded temporary file.
        """
        try:
            # Create a temporary file with a proper suffix based on the URL's file extension
            file_suffix = os.path.splitext(url)[-1]  # Extract the file extension from the URL
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
                temp_file_path = temp_file.name

            # Download the file to the temporary file location
            urlretrieve(url, temp_file_path)  # Replace this with your download function if needed
            logger.info(f"File downloaded to temporary location: {temp_file_path}")
            return temp_file_path

        except Exception as e:
            logger.error(f"Failed to download file from URL '{url}': {str(e)}")
            raise

    def _update_service_metadata(self, service: Service, asset_hash: str, storage_provider_enum: StorageProviderType) -> Service:
        """
        Updates the service metadata and persists it in the repository.

        :param service: Service object to update.
        :param asset_hash: Hash of the published proto file.
        :param storage_provider_enum: Enum value for the storage provider.
        """
        service.proto = {
            "model_hash": asset_hash,
            "encoding": "proto",
            "service_type": service.service_type,
        }
        service.assets["proto_files"]["hash"] = asset_hash
        self.publish_assets(service, storage_provider_enum)

        service_repo = ServicePublisherRepository()
        return service_repo.save_service(self._username, service, service.service_state.state)

    @staticmethod
    def notify_service_contributor_when_user_submit_for_approval(org_id, service_id, contributors):
        # notify service contributor for submission via email
        recipients = [contributor.get("email_id", "") for contributor in contributors]
        if not recipients:
            logger.info(f"Unable to find service contributors for service {service_id} under {org_id}")
            return
        notification_subject = f"Your service {service_id} has successfully submitted for approval"
        notification_message = f"Your service {service_id} under organization {org_id} has successfully been submitted " \
                               f"for approval. We will notify you once it is reviewed by our approval team. It usually " \
                               f"takes around five to ten business days for approval."
        utils.send_email_notification(recipients, notification_subject, notification_message, NOTIFICATION_ARN, boto_util)

    def daemon_config(self, environment):
        organization = OrganizationPublisherRepository().get_organization(org_uuid=self._org_uuid)
        if not organization:
            raise OrganizationNotFoundException()
        service = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        if not service:
            raise ServiceNotFoundException()
        organization_members = OrganizationPublisherRepository().get_org_member(org_uuid=self._org_uuid)
        network_name = NETWORKS[NETWORK_ID]["name"].lower()
        # this is how network name is set in daemon for mainnet
        network_name = "main" if network_name == "mainnet" else network_name
        if environment is EnvironmentType.MAIN.value:
            daemon_config = {
                "ipfs_end_point": f"{IPFS_URL['url']}:{IPFS_URL['port']}",
                "blockchain_network_selected": network_name,
                "organization_id": organization.id,
                "service_id": service.service_id,
                "metering_end_point": f"https://{network_name}-marketplace.singularitynet.io",
                "authentication_addresses": [member.address for member in organization_members],
                "blockchain_enabled": True,
                "passthrough_enabled": True
            }
        else:
            raise EnvironmentNotFoundException()
        return daemon_config

    def get_service_demo_component_build_status(self):
        try:
            service = self.get_service_for_given_service_uuid()
            if service:
                build_id = service["media"]["demo_files"]["build_id"]
                build_response = boto_util.get_code_build_details(build_ids=[build_id])
                build_data = [data for data in build_response['builds'] if data['id'] == build_id]
                status = build_data[0]['buildStatus']
            else:
                raise Exception(f"service for org {self._org_uuid} and service {service} is not found")
            return {"build_status": status}
        except Exception as e:
            logger.info(
                f"error in triggering build_id {build_id} for service {self._service_uuid} and org {self._org_uuid} :: error {repr(e)}")
            raise e

    def get_existing_offchain_configs(self, existing_service_data):
        existing_offchain_configs = {}
        if "demo_component" in existing_service_data:
            existing_offchain_configs.update(
                {"demo_component": existing_service_data["demo_component"]})
        return existing_offchain_configs

    def are_blockchain_attributes_got_updated(self, existing_metadata, current_service_metadata):
        change = DeepDiff(current_service_metadata, existing_metadata)
        logger.info(f"Change in blockchain attributes::{change}")
        if change:
            return True
        return False

    def get_offchain_changes(self, current_offchain_config, existing_offchain_config, current_service):
        changes = {}
        existing_demo = existing_offchain_config.get("demo_component", {})
        new_demo = DemoComponent(
            demo_component_required=current_offchain_config["demo_component_required"],
            demo_component_url=current_service.assets.get("demo_files", {}).get("url", ""),
            demo_component_status=current_service.assets.get("demo_files", {}).get("status", "")
        )
        demo_changes = new_demo.to_dict()
        demo_last_modified = existing_demo.get("demo_component_last_modified", "")
        # if last_modified not there publish if it there and is greater than current last modifed publish
        demo_changes.update({"change_in_demo_component": 1})
        current_demo_last_modified = current_service.assets.get("demo_files", {}).get("last_modified")
        if demo_last_modified and \
            (current_demo_last_modified is None or
             dt.fromisoformat(demo_last_modified) > dt.fromisoformat(current_demo_last_modified)):
            demo_changes.update({"change_in_demo_component": 0})
        changes.update({"demo_component": demo_changes})
        return changes

    def publish_offchain_service_configs(self, org_id, service_id, payload, token_name):
        publish_offchain_attributes_arn = PUBLISH_OFFCHAIN_ATTRIBUTES_ARN[token_name]
        # response = requests.post(PUBLISH_OFFCHAIN_ATTRIBUTES_ENDPOINT.format(org_id, service_id), data=payload)
        payload = {
            "httpMethod": "POST",
            "pathParameters": {
                "orgId": org_id,
                "serviceId": service_id
            },
            "body": payload
        }
        response = boto_util.invoke_lambda(
            publish_offchain_attributes_arn,
            "RequestResponse",
            json.dumps(payload)
        )

        result = json.loads(response.get('Payload').read())
        response = json.loads(result['body'])

        if response["status"] != 200:
            raise Exception(f"Error in publishing offchain service attributes for org_id :: {org_id} service_id :: {service_id}")


    def get_existing_service_details_from_contract_api(self, service_id, org_id, token_name):
        get_service_arn = GET_SERVICE_FOR_GIVEN_ORG_ARN[token_name]
        payload = {
            "httpMethod": "GET",
            "pathParameters": {
                "orgId": org_id,
                "serviceId": service_id
            }
        }
        response = boto_util.invoke_lambda(
            get_service_arn,
            "RequestResponse",
            json.dumps(payload)
        )

        result = json.loads(response.get('Payload').read())
        response = json.loads(result['body'])

        if response["status"] != 200:
            raise Exception(f"Error getting service details for org_id :: {org_id} service_id :: {service_id}")
        logger.debug(f"Get service by org_id from contract_api :: {response}")

        return response["data"]

    def publish_new_offchain_configs(self, current_service: Service, storage_provider: StorageProviderType) -> Dict[str, Union[bool, str]]:
        organization = OrganizationPublisherRepository().get_organization(org_uuid=self._org_uuid)
        logger.debug(f"Current organization :: {organization.to_response()}")

        service_mpe_address = current_service.mpe_address
        token_name = self.__get_token_name(service_mpe_address)

        existing_service_data = self.get_existing_service_details_from_contract_api(
            current_service.service_id, organization.id, token_name
        )
        logger.debug(f"Existing service data :: {existing_service_data}")

        existing_metadata = (
            self._storage_provider.get(existing_service_data["hash_uri"])
            if existing_service_data else {}
        )
        publish_to_blockchain = self.are_blockchain_attributes_got_updated(
            existing_metadata, current_service.to_metadata()
        )
        logger.debug(f"Publish to blockchain :: {publish_to_blockchain}")

        existing_offchain_configs = self.get_existing_offchain_configs(existing_service_data)
        current_offchain_configs = ServicePublisherRepository().get_offchain_service_config(
            org_uuid=self._org_uuid, service_uuid=self._service_uuid
        )

        logger.debug(f"Current offchain configs :: {current_offchain_configs}")
        logger.debug(f"Existing offchain configs :: {existing_offchain_configs}")

        new_offchain_configs = self.get_offchain_changes(
            current_offchain_config=current_offchain_configs.configs,
            existing_offchain_config=existing_offchain_configs,
            current_service=current_service
        )
        logger.debug(f"New offchain configs :: {new_offchain_configs}")

        status = self._prepare_publish_status(
            organization,
            current_service,
            storage_provider,
            publish_to_blockchain,
            new_offchain_configs,
            token_name
        )
        logger.debug(f"Prepare publish status result :: {status}")

        return status

    def _prepare_publish_status(self, organization: Organization, current_service: Service,
                                storage_provider: StorageProviderType, publish_to_blockchain: bool,
                                new_offchain_configs: Dict[str, any], token_name: str):
        status = {"publish_to_blockchain": publish_to_blockchain}

        if publish_to_blockchain:
            filepath = FileUtils.create_temp_json_file(current_service.to_metadata())
            # filename = f"{METADATA_FILE_PATH}/{current_service.uuid}_service_metadata.json"
            status["service_metadata_uri"] = self._storage_provider.publish(filepath, storage_provider)
            current_service.metadata_uri = status["service_metadata_uri"]

        logger.info("Publish offchain service configs to contract_api")
        self.publish_offchain_service_configs(
            org_id=organization.id,
            service_id=current_service.service_id,
            payload=json.dumps(new_offchain_configs),
            token_name=token_name
        )

        if not publish_to_blockchain:
            ServicePublisherRepository().save_service(
                username=self._username,
                service=current_service,
                state=ServiceStatus.PUBLISHED.value
            )

        return status

    def publish_service(self, storage_provider: str):
        storage_provider_enum = validate_storage_provider(storage_provider)
        current_service = self.publish_service_data_to_storage_provider(storage_provider_enum=storage_provider_enum)
        logger.debug(f"Current service :: {current_service.to_dict()}")

        if not Service.is_metadata_valid(service_metadata=current_service.to_metadata()):
            raise InvalidMetadataException()

        return self.publish_new_offchain_configs(current_service, storage_provider_enum)

    @staticmethod
    def __get_token_name(mpe_address):
        mpe_contract = BlockChainUtil.load_contract(REG_ADDR_PATH)
        network_data = mpe_contract[NETWORK_ID]
        for token, data in network_data.items():
            if data[STAGE]["address"] == mpe_address:
                return token
