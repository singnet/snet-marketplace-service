import json
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
    REGION_NAME, PUBLISH_OFFCHAIN_ATTRIBUTES_ENDPOINT, GET_SERVICE_FOR_GIVEN_ORG_LAMBDA_ARN
from registry.constants import EnvironmentType, ServiceAvailabilityStatus, ServiceStatus, \
    ServiceSupportType, UserType
from registry.domain.factory.service_factory import ServiceFactory
from registry.domain.models.service import SERVICE_METADATA_SCHEMA, Service
from registry.domain.models.service_comment import ServiceComment
from registry.domain.services.service_publisher_domain_service import ServicePublisherDomainService
from registry.exceptions import EnvironmentNotFoundException, InvalidServiceStateException, \
    OrganizationNotFoundException, ServiceNotFoundException, ServiceProtoNotFoundException
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
            ServicePublisherRepository().save_service(self._username, service, ServiceStatus.CHANGE_REQUESTED.value)
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
        org_uuid, service = ServicePublisherRepository().get_service_for_given_service_id_and_org_id(org_id, service_id)
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

    def save_service(self, payload):
        service = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        service.service_id = payload["service_id"]
        service.proto = payload.get("proto", {})
        service.short_description = payload.get("short_description", "")
        service.description = payload.get("description", "")
        service.project_url = payload.get("project_url", "")
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
        service = ServicePublisherRepository().save_service(self._username, service, ServiceStatus.APPROVED.value)
        comment = payload.get("comments", {}).get(UserType.SERVICE_PROVIDER.value, "")
        if len(comment) > 0:
            self._save_service_comment(support_type="SERVICE_APPROVAL", user_type="SERVICE_PROVIDER", comment=comment)
        return service.to_dict()

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
        service["media"]["demo_files"].update({"required": offchain_service_config.configs.get("demo_component_required", 0)})
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
        service_response = self.map_offchain_service_config(offchain_service_config, service.to_dict())
        return service_response

    def publish_service_data_to_ipfs(self):
        service = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        if service.service_state.state == ServiceStatus.APPROVED.value:
            proto_url = service.assets.get("proto_files", {}).get("url", None)
            if proto_url is None:
                raise ServiceProtoNotFoundException
            filename = download_file_from_url(file_url=proto_url,
                                              file_dir=f"{ASSET_DIR}/{service.org_uuid}/{service.uuid}")
            asset_ipfs_hash = publish_zip_file_in_ipfs(filename=filename,
                                                       file_dir=f"{ASSET_DIR}/{service.org_uuid}/{service.uuid}",
                                                       ipfs_client=IPFSUtil(IPFS_URL['url'], IPFS_URL['port']))
            service.proto = {
                "model_ipfs_hash": asset_ipfs_hash,
                "encoding": "proto",
                "service_type": "grpc"
            }
            service.assets["proto_files"]["ipfs_hash"] = asset_ipfs_hash
            ServicePublisherDomainService.publish_assets(service)
            service = ServicePublisherRepository().save_service(self._username, service, service.service_state.state)
            service_metadata = service.to_metadata()
            filename = f"{METADATA_FILE_PATH}/{service.uuid}_service_metadata.json"
            service.metadata_ipfs_hash = ServicePublisherService.publish_to_ipfs(filename, service_metadata)
            return {"service_metadata": service.to_metadata(),
                    "metadata_ipfs_hash": "ipfs://" + service.metadata_ipfs_hash}
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

    def publish_offchain_service_configs(self, org_id, service_id):
        response = requests.post(
            PUBLISH_OFFCHAIN_ATTRIBUTES_ENDPOINT.format(org_id.id, service_id))
        if response.get["statusCode"] != 200:
            raise Exception(f"Error in updating offchain service attributes")

    def get_existing_service_details_from_contract_api(self, service_id, org_id):
        payload = json.dumps({
            "pathParameters": {
                "serviceId": service_id,
                "orgId": org_id
            }
        })
        response = boto_util.invoke_lambda(
            lambda_function_arn=GET_SERVICE_FOR_GIVEN_ORG_LAMBDA_ARN,
            invocation_type="RequestResponse",
            payload=payload
        )
        logger.info(f"get existing service response :: {response}")
        if response["statusCode"] == 200:
            response = json.loads(response["body"])["data"]
            return response
        raise Exception(
            f"Error getting service details from lambda for org_id :: {self._org_uuid} and service_id :: {self._service_uuid}")

    def validate_service_metadata(self, current_organization_data, current_service_data, existing_service_data):
        # VALIDATE METADATA
        is_valid = Service.is_metadata_valid(service_metadata=current_service_data.to_metadata())
        if not is_valid:
            raise Exception("Service data is not valid!. Please make all valid data are present before publishing")
        if not existing_service_data:
            return {"publish_to_blockchain": True, "publish_offchain_attributes": True}
        publish_onchain = publish_offchain = False
        # ONCHAIN DIFF
        existing_metadata = ipfs_util.read_file_from_ipfs(existing_service_data["ipfs_hash"])
        onchain_diff = DeepDiff(current_service_data.to_metadata(), existing_metadata)
        if onchain_diff:
            publish_onchain = True
            logger.info(f"changes in onchain_data :: f{onchain_diff}")
        # OFFCHAIN DIFF
        current_offchain_attributes = ServicePublisherRepository().get_offchain_service_config(
            org_uuid=self._org_uuid,
            service_uuid=self._service_uuid
        )
        offchain_diff = DeepDiff(current_offchain_attributes.configs,
                                 existing_service_data["offchain_service_config"]["configs"])
        if offchain_diff:
            publish_offchain = True
            logger.info(f"changes in onchain_data :: f{offchain_diff}")
        return {"publish_to_blockchain": publish_onchain, "publish_offchain_attributes": publish_offchain}

    def publish_service_data(self):
        # Get required details for validation
        current_organization_data = OrganizationPublisherRepository().get_organization(org_uuid=self._org_uuid)
        current_service_data = ServicePublisherRepository() \
            .get_service_for_given_service_uuid(org_uuid=self._org_uuid, service_uuid=self._service_uuid)
        existing_service_data = self.get_existing_service_details_from_contract_api(current_service_data.service_id,
                                                                                    current_organization_data.id)
        # Validate metadata
        service_validation = self.validate_service_metadata(current_organization_data, current_service_data,
                                                            existing_service_data)
        # Publish service data
        if service_validation["publish_to_blockchain"]:
            ipfs_data = self.publish_service_data_to_ipfs()
            service_validation.update({"service_metadata_ipfs_hash": ipfs_data["service_metadata_ipfs_hash"]})
        if service_validation["publish_offchain_attributes"]:
            self.publish_offchain_service_configs(
                org_id=current_organization_data.id,
                service_id=current_service_data.service_id
            )
        return service_validation