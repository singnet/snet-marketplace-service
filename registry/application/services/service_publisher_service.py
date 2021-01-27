import json
from uuid import uuid4

from aws_xray_sdk.core import patch_all

from common import utils
from common.boto_utils import BotoUtils
from common.constant import StatusCode
from common.ipfs_util import IPFSUtil
from common.logger import get_logger
from common.utils import download_file_from_url, json_to_file, publish_zip_file_in_ipfs, send_email_notification, Utils
from registry.config import ASSET_DIR, BLOCKCHAIN_TEST_ENV, EMAILS, IPFS_URL, METADATA_FILE_PATH, NETWORKS, NETWORK_ID, \
    NOTIFICATION_ARN, REGION_NAME, APPROVAL_SLACK_HOOK
from registry.constants import EnvironmentType, OrganizationStatus, ServiceAvailabilityStatus, ServiceStatus, \
    ServiceSupportType, UserType
from registry.domain.factory.service_factory import ServiceFactory
from registry.domain.models.service_comment import ServiceComment
from registry.domain.services.service_publisher_domain_service import ServicePublisherDomainService
from registry.exceptions import EnvironmentNotFoundException, InvalidOrganizationStateException, \
    InvalidServiceStateException, OrganizationNotFoundException, OrganizationNotPublishedException, \
    ServiceNotFoundException, ServiceProtoNotFoundException
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
from registry.mail_templates import get_service_approval_mail_template

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

    def save_service(self, payload):
        service = ServiceFactory().create_service_entity_model(self._org_uuid, self._service_uuid, payload,
                                                               ServiceStatus.DRAFT.value)
        service = ServicePublisherRepository().save_service(self._username, service, ServiceStatus.DRAFT.value)
        comments = payload.get("comments", {}).get(UserType.SERVICE_PROVIDER.value, "")
        if bool(comments):
            service_provider_comment = service_factory. \
                create_service_comment_entity_model(org_uuid=self._org_uuid,
                                                    service_uuid=self._service_uuid,
                                                    support_type="SERVICE_APPROVAL",
                                                    user_type="SERVICE_PROVIDER",
                                                    commented_by=self._username,
                                                    comment=comments)
            ServicePublisherRepository().save_service_comments(service_provider_comment)
            service.comments = self.get_service_comments()
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
        search_result = ServicePublisherRepository().get_services_for_organization(self._org_uuid, filter_parameters)
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

    def get_service_for_given_service_uuid(self):
        service = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        if not service:
            return None
        service.comments = self.get_service_comments()
        return service.to_dict()

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

    def approve_service(self):
        pass

    @staticmethod
    def get_list_of_orgs_with_services_submitted_for_approval():
        list_of_orgs_with_services = []
        services_review = ServicePublisherRepository().get_all_services_review_data()
        for service_review in services_review:
            list_of_orgs_with_services.append({
                "org_uuid": service_review.org_uuid,
                "services": [
                    {
                        "service_uuid": service_review.service_uuid
                    }
                ],
            })
        return list_of_orgs_with_services

    @staticmethod
    def organization_exist_in_blockchain(org_id):
        # get list of organization from blockchain
        return True
        orgs = []
        if org_id in orgs:
            return True
        return False

    @staticmethod
    def service_exist_in_blockchain(org_id, service_id):
        # get list of services
        services = []
        if service_id in services:
            return True
        return False

    @staticmethod
    def unregister_service_in_blockchain(org_id, service_id):
        return ""
        # blockchain_util = BlockChainUtil(provider=NETWORKS[NETWORK_ID]["http_provider"], provider_type="http_provider")
        # method_name = "deleteServiceRegistration"
        # positional_inputs = (org_id, service_id)
        # transaction_object = blockchain_util.create_transaction_object(*positional_inputs, method_name=method_name,
        #                                                                address=EXECUTOR_ADDRESS,
        #                                                                contract_path=REG_CNTRCT_PATH,
        #                                                                contract_address_path=REG_ADDR_PATH,
        #                                                                net_id=NETWORK_ID)
        # raw_transaction = blockchain_util.sign_transaction_with_private_key(transaction_object=transaction_object,
        #                                                                     private_key=EXECUTOR_KEY)
        # transaction_hash = blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)
        # return transaction_hash

    @staticmethod
    def unregister_service_in_blockchain_after_service_is_approved(org_id, service_id):
        transaction_hash = ServicePublisherService.unregister_service_in_blockchain(
            org_id=org_id, service_id=service_id)
        logger.info(
            f"Transaction hash {transaction_hash} generated while unregistering service_id {service_id} in blockchain")

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

    def notify_approval_team(self, service_id, service_name, org_id, org_name):
        slack_msg = f"Service {service_id} under org_id {org_id} is submitted for approval"
        Utils().report_slack(slack_msg, APPROVAL_SLACK_HOOK)
        mail = get_service_approval_mail_template(service_id, service_name, org_id, org_name)
        send_email_notification([EMAILS["SERVICE_APPROVERS_DLIST"]], mail["subject"],
                                mail["body"], NOTIFICATION_ARN, boto_util)

    def send_email(self, mail, recipient):
        send_notification_payload = {"body": json.dumps({
            "message": mail["body"],
            "subject": mail["subject"],
            "notification_type": "support",
            "recipient": recipient})}
        boto_util.invoke_lambda(lambda_function_arn=NOTIFICATION_ARN, invocation_type="RequestResponse",
                                payload=json.dumps(send_notification_payload))

    def submit_service_for_approval(self, payload):

        user_as_contributor = [{"email_id": self._username, "name": ""}]
        payload["contributors"] = payload.get("contributors", user_as_contributor) + user_as_contributor

        organization = OrganizationPublisherRepository().get_org_for_org_uuid(self._org_uuid)
        if not organization:
            raise OrganizationNotFoundException()
        if not organization.org_state:
            raise InvalidOrganizationStateException()
        if not organization.org_state.state == OrganizationStatus.PUBLISHED.value:
            raise OrganizationNotPublishedException()

        service = service_factory.create_service_entity_model(
            self._org_uuid, self._service_uuid, payload, ServiceStatus.APPROVAL_PENDING.value)

        # publish service data with test config on ipfs
        service = self.obj_service_publisher_domain_service.publish_service_data_to_ipfs(service,
                                                                                         EnvironmentType.TEST.value)

        comments = payload.get("comments", {}).get(UserType.SERVICE_PROVIDER.value, "")
        if bool(comments):
            service_provider_comment = service_factory. \
                create_service_comment_entity_model(org_uuid=self._org_uuid,
                                                    service_uuid=self._service_uuid,
                                                    support_type="SERVICE_APPROVAL",
                                                    user_type="SERVICE_PROVIDER",
                                                    commented_by=self._username,
                                                    comment=comments)
            ServicePublisherRepository().save_service_comments(service_provider_comment)
        service = ServicePublisherRepository().save_service(self._username, service, service.service_state.state)

        # publish service on test network
        response = self.obj_service_publisher_domain_service.publish_service_on_blockchain(
            org_id=organization.id, service=service, environment=EnvironmentType.TEST.value)

        # notify service contributors via email
        self.notify_service_contributor_when_user_submit_for_approval(organization.id, service.service_id,
                                                                      service.contributors)

        # notify approval team via slack
        self.notify_approval_team(service.service_id, service.display_name, organization.id, organization.name)
        return response

    @staticmethod
    def publish_to_ipfs(filename, data):
        json_to_file(data, filename)
        service_metadata_ipfs_hash = IPFSUtil(
            IPFS_URL['url'], IPFS_URL['port']).write_file_in_ipfs(filename, wrap_with_directory=False)
        return service_metadata_ipfs_hash

    def daemon_config(self, environment):
        organization = OrganizationPublisherRepository().get_org_for_org_uuid(self._org_uuid)
        if not organization:
            raise OrganizationNotFoundException()
        service = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        if not service:
            raise ServiceNotFoundException()
        organization_members = OrganizationPublisherRepository().get_org_member(org_uuid=self._org_uuid)
        network_name = NETWORKS[NETWORK_ID]["name"].lower()
        # this is how network name is set in daemon for mainnet
        network_name = "main" if network_name == "mainnet" else network_name
        if environment is EnvironmentType.TEST.value:
            daemon_config = {
                "allowed_user_flag": True,
                "allowed_user_addresses": [member.address for member in organization_members] + [
                    BLOCKCHAIN_TEST_ENV["publisher_address"]],
                "authentication_addresses": [member.address for member in organization_members],
                "blockchain_enabled": False,
                "passthrough_enabled": True,
                "organization_id": organization.id,
                "service_id": service.service_id
            }
        elif environment is EnvironmentType.MAIN.value:
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

    @staticmethod
    def get_list_of_service_pending_for_approval(limit):
        list_of_services = []
        services = ServicePublisherRepository().get_list_of_service_pending_for_approval(limit)
        for service in services:
            org = OrganizationPublisherRepository().get_org_for_org_uuid(org_uuid=service.org_uuid)
            list_of_services.append({
                "org_uuid": service.org_uuid,
                "org_id": org.id,
                "service_uuid": service.uuid,
                "service_id": service.service_id,
                "display_name": service.display_name,
                "requested_at": None
            })

        return list_of_services
