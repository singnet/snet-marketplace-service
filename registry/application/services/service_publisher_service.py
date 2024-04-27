import json
from datetime import datetime as dt
from uuid import uuid4
import requests

from aws_xray_sdk.core import patch_all
from cerberus import Validator

from common import utils
from common.boto_utils import BotoUtils
from common.constant import StatusCode
from common.ipfs_util import IPFSUtil
from common.logger import get_logger
from common.utils import download_file_from_url, json_to_file, publish_zip_file_in_ipfs, send_email_notification
from registry.config import ASSET_DIR, IPFS_URL, METADATA_FILE_PATH, NETWORKS, NETWORK_ID, NOTIFICATION_ARN, \
    REGION_NAME, PUBLISH_OFFCHAIN_ATTRIBUTES_ENDPOINT, GET_SERVICE_FOR_GIVEN_ORG_ENDPOINT
from registry.constants import EnvironmentType, ServiceAvailabilityStatus, ServiceStatus, \
    ServiceSupportType, UserType, ServiceType
from registry.domain.factory.service_factory import ServiceFactory
from registry.domain.models.demo_component import DemoComponent
from registry.domain.models.offchain_service_config import OffchainServiceConfig
from registry.domain.models.service import Service as ServiceEntityModel
from registry.domain.models.service_comment import ServiceComment
from registry.domain.services.service_publisher_domain_service import ServicePublisherDomainService
from registry.exceptions import EnvironmentNotFoundException, InvalidServiceStateException, \
    OrganizationNotFoundException, ServiceNotFoundException, ServiceProtoNotFoundException, InvalidMetadataException
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
from deepdiff import DeepDiff

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
ipfs_util = IPFSUtil(IPFS_URL["url"], IPFS_URL["port"])


class ServicePublisherService:
    def __init__(self, username, org_uuid, service_uuid):
        self._username = username
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid
        self.obj_service_publisher_domain_service = ServicePublisherDomainService(username, org_uuid, service_uuid)

    def service_build_status_notifier(self, org_id, service_id, build_status):

        if build_status == BUILD_FAILURE_CODE:
            BUILD_FAIL_MESSAGE = "Build failed please check your components"
            org_uuid, service = ServicePublisherRepository().get_service_for_given_service_id_and_org_id(org_id,
                                                                                                         service_id)

            contacts = [contributor.get("email_id", "") for contributor in service.contributors]

            service_comment = ServiceComment(org_uuid, service.uuid, "SERVICE_APPROVAL", "SERVICE_APPROVER",
                                             self._username, BUILD_FAIL_MESSAGE)
            ServicePublisherRepository().save_service_comments(service_comment)
            ServicePublisherRepository().save_service(self._username, service, ServiceStatus.CHANGE_REQUESTED)
            logger.info(f"Build failed for org_id {org_id}  and service_id {service_id}")
            try:
                BUILD_STATUS_SUBJECT = "Build failed for your service {}"
                BUILD_STATUS_MESSAGE = "Build failed for your org_id {} and service_id {}"
                send_email_notification(contacts,
                                        BUILD_STATUS_SUBJECT.format(service_id),
                                        BUILD_STATUS_MESSAGE.format(org_id, service_id), NOTIFICATION_ARN,
                                        boto_util)
            except:
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
        ServicePublisherRepository().save_service(self._username, service, ServiceStatus.APPROVED)
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
        if service.service_state.state == ServiceStatus.APPROVED:
            service.service_state = \
                ServiceFactory().create_service_state_entity_model(
                    self._org_uuid, self._service_uuid, ServiceStatus.PUBLISH_IN_PROGRESS,
                    payload.get("transaction_hash", ""))
            ServicePublisherRepository().save_service(self._username, service, ServiceStatus.PUBLISH_IN_PROGRESS)
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

    def publish_service_data_to_ipfs(self):
        service_publisher_repo = ServicePublisherRepository()
        service = service_publisher_repo.get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        if service.service_state.state == ServiceStatus.APPROVED:
            proto_url = service.assets.get("proto_files", {}).get("url", None)
            if proto_url is None:
                raise ServiceProtoNotFoundException
            filename = download_file_from_url(file_url=proto_url,
                                              file_dir=f"{ASSET_DIR}/{service.org_uuid}/{service.uuid}")
            logger.info(f"proto file Name Retrieved  = '{filename}` ")
            asset_ipfs_hash = publish_zip_file_in_ipfs(filename=filename,
                                                       file_dir=f"{ASSET_DIR}/{service.org_uuid}/{service.uuid}",
                                                       ipfs_client=IPFSUtil(IPFS_URL['url'], IPFS_URL['port']))
            service.proto = {
                "model_ipfs_hash": asset_ipfs_hash,
                "encoding": "proto",
                "service_type": service.service_type
            }
            service.assets["proto_files"]["ipfs_hash"] = asset_ipfs_hash
            ServicePublisherDomainService.publish_assets(service)
            service = service_publisher_repo.save_service(self._username, service, service.service_state.state)
            return service
        logger.info(f"Service status needs to be {ServiceStatus.APPROVED.value} to be eligible for publishing.")
        raise InvalidServiceStateException()

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
        utils.send_email_notification(recipients, notification_subject, notification_message, NOTIFICATION_ARN,
                                      boto_util)

    def send_email(self, mail, recipient):
        send_notification_payload = {"body": json.dumps({
            "message": mail["body"],
            "subject": mail["subject"],
            "notification_type": "support",
            "recipient": recipient})}
        boto_util.invoke_lambda(lambda_function_arn=NOTIFICATION_ARN, invocation_type="RequestResponse",
                                payload=json.dumps(send_notification_payload))

    @staticmethod
    def publish_to_ipfs(filename, data):
        json_to_file(data, filename)
        service_metadata_ipfs_hash = IPFSUtil(
            IPFS_URL['url'], IPFS_URL['port']).write_file_in_ipfs(filename, wrap_with_directory=False)
        return service_metadata_ipfs_hash

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
            (current_demo_last_modified is None or \
             dt.fromisoformat(demo_last_modified) > dt.fromisoformat(current_demo_last_modified)):
            demo_changes.update({"change_in_demo_component": 0})
        changes.update({"demo_component": demo_changes})
        return changes

    def publish_offchain_service_configs(self, org_id, service_id, payload):
        response = requests.post(
            PUBLISH_OFFCHAIN_ATTRIBUTES_ENDPOINT.format(org_id, service_id), data=payload)
        if response.status_code != 200:
            raise Exception("Error in updating offchain service attributes")

    def get_existing_service_details_from_contract_api(self, service_id, org_id):
        response = requests.get(
            GET_SERVICE_FOR_GIVEN_ORG_ENDPOINT.format(org_id, service_id))
        if response.status_code != 200:
            raise Exception(f"Error getting service details for org_id :: {org_id} service_id :: {service_id}")
        return json.loads(response.text)["data"]

    def publish_service_data(self):
        # Validate service metadata
        current_service = self.publish_service_data_to_ipfs()

        is_valid = ServiceEntityModel.is_metadata_valid(service_metadata=current_service.to_metadata())
        logger.info(f"is_valid :: {is_valid} :: validated current_metadata :: {current_service.to_metadata()}")
        if not is_valid:
            raise InvalidMetadataException()

        # Monitor blockchain and offchain changes
        current_org = OrganizationPublisherRepository().get_organization(org_uuid=self._org_uuid)
        existing_service_data = self.get_existing_service_details_from_contract_api(current_service.service_id, current_org.id)
        if existing_service_data:
            existing_metadata = ipfs_util.read_file_from_ipfs(existing_service_data["ipfs_hash"])
        else:
            existing_metadata = {}
        publish_to_blockchain = self.are_blockchain_attributes_got_updated(existing_metadata, current_service.to_metadata())
        existing_offchain_configs = self.get_existing_offchain_configs(existing_service_data)

        current_offchain_attributes = ServicePublisherRepository().get_offchain_service_config(org_uuid=self._org_uuid,
                                                                                               service_uuid=self._service_uuid)

        new_offchain_attributes = self.get_offchain_changes(
            current_offchain_config=current_offchain_attributes.configs,
            existing_offchain_config=existing_offchain_configs,
            current_service=current_service)

        status = {
            "publish_to_blockchain": publish_to_blockchain
        }
        if publish_to_blockchain:
            filename = f"{METADATA_FILE_PATH}/{current_service.uuid}_service_metadata.json"
            ipfs_hash = ServicePublisherService.publish_to_ipfs(filename, current_service.to_metadata())
            status["service_metadata_ipfs_hash"] = "ipfs://" + ipfs_hash
        self.publish_offchain_service_configs(
            org_id=current_org.id,
            service_id=current_service.service_id,
            payload=json.dumps(new_offchain_attributes)
        )
        # if there is no blockchain change update state as published
        # else status will be marked based event received from blockchain
        if not publish_to_blockchain:
            ServicePublisherRepository().save_service(
                username=self._username,
                service=current_service,
                state=ServiceStatus.PUBLISHED
            )
        return status
