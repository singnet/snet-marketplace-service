from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
from registry.constants import ServiceAvailabilityStatus, ServiceStatus
from registry.config import IPFS_URL, METADATA_FILE_PATH, ASSET_DIR, ORG_ID_FOR_TESTING_AI_SERVICE, SLACK_HOOK
from uuid import uuid4
from registry.exceptions import InvalidServiceState, ServiceProtoNotFoundException, OrganizationNotFoundException
from registry.domain.factory.service_factory import ServiceFactory
from registry.domain.services.service_publisher_domain_service import ServicePublisherDomainService
from common.ipfs_util import IPFSUtil
from common.boto_utils import BotoUtils
from common import utils
from common.utils import json_to_file, hash_to_bytesuri, publish_zip_file_in_ipfs
from registry.constants import EnvironmentType
from common.constant import StatusCode
from registry.config import REGION_NAME, NOTIFICATION_ARN, SLACK_CHANNEL_FOR_APPROVAL_TEAM
from common.logger import get_logger

ALLOWED_ATTRIBUTES_FOR_SERVICE_SEARCH = ["display_name"]
DEFAULT_ATTRIBUTE_FOR_SERVICE_SEARCH = "display_name"
ALLOWED_ATTRIBUTES_FOR_SERVICE_SORT_BY = ["ranking", "service_id"]
DEFAULT_ATTRIBUTES_FOR_SERVICE_SORT_BY = "ranking"
ALLOWED_ATTRIBUTES_FOR_SERVICE_ORDER_BY = ["asc", "desc"]
DEFAULT_ATTRIBUTES_FOR_SERVICE_ORDER_BY = "desc"
DEFAULT_OFFSET = 0
DEFAULT_LIMIT = 0

logger = get_logger(__name__)
service_factory = ServiceFactory()
boto_util = BotoUtils(region_name=REGION_NAME)


class ServicePublisherService:
    def __init__(self, username, org_uuid, service_uuid):
        self._username = username
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid
        self.obj_service_publisher_domain_service = ServicePublisherDomainService(username, org_uuid, service_uuid)

    def get_service_id_availability_status(self, service_id):
        record_exist = ServicePublisherRepository().check_service_id_within_organization(self._org_uuid, service_id)
        if record_exist:
            return ServiceAvailabilityStatus.UNAVAILABLE.value
        return ServiceAvailabilityStatus.AVAILABLE.value

    def save_service(self, payload):
        service = ServiceFactory().create_service_entity_model(self._org_uuid, self._service_uuid, payload,
                                                               ServiceStatus.DRAFT.value)
        service = ServicePublisherRepository().save_service(self._username, service, ServiceStatus.DRAFT.value)
        return service.to_dict()

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

    def get_service_for_given_service_uuid(self):
        service = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        return service.to_dict()

    def publish_service_data_to_ipfs(self):
        service = ServicePublisherRepository().get_service_for_given_service_uuid(self._org_uuid, self._service_uuid)
        if service.service_state.state == ServiceStatus.APPROVED.value:
            proto_url = service.assets.get("proto_files", {}).get("url", None)
            if proto_url is None:
                raise ServiceProtoNotFoundException
            asset_ipfs_hash = publish_zip_file_in_ipfs(file_url=proto_url,
                                                       file_dir=f"{ASSET_DIR}/{service.org_uuid}/{service.uuid}",
                                                       ipfs_client=IPFSUtil(IPFS_URL['url'], IPFS_URL['port']))
            service.proto = {
                "model_ipfs_hash": asset_ipfs_hash,
                "encoding": "proto",
                "service_type": "grpc"
            }
            service.assets["proto_files"]["ipfs_hash"] = asset_ipfs_hash
            service = ServicePublisherRepository().save_service(self._username, service, service.service_state.state)
            service_metadata = service.to_metadata()
            filename = f"{METADATA_FILE_PATH}/{service.uuid}_service_metadata.json"
            service.metadata_ipfs_hash = ServicePublisherService.publish_to_ipfs(filename, service_metadata)
            return {"service_metadata": service.to_metadata(),
                    "metadata_ipfs_hash": "ipfs://" + service.metadata_ipfs_hash}
        logger.info(f"Service status needs to be {ServiceStatus.APPROVED.value} to be eligible for publishing.")
        raise InvalidServiceState()

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
    def unregister_service_in_blockchain_after_service_is_approved(service_id):
        transaction_hash = ServicePublisherService.unregister_service_in_blockchain(org_id=ORG_ID_FOR_TESTING_AI_SERVICE, service_id=service_id)
        logger.info(
            f"Transaction hash {transaction_hash} generated while unregistering service_id {service_id} in blockchain")

    @staticmethod
    def notify_service_contributor_when_user_submit_for_approval(org_id, service_id, contributors):
        # notify service contributor for submission via email
        recipients = [contributor["email_id"] for contributor in contributors]
        if not recipients:
            logger.info(f"Unable to find service contributors for service {service_id} under {org_id}")
            return
        notification_subject = f"Your service {service_id} has successfully submitted for approval"
        notification_message = f"Your service {service_id} under {org_id} has successfully submitted for approval. " \
                               f"We will notify you once it is approved/rejected from our approval team. Usually it " \
                               f"takes {5} - {10} days for approval."
        utils.send_email_notification(recipients, notification_subject, notification_message, NOTIFICATION_ARN, boto_util)

    @staticmethod
    def notify_approval_team_when_user_submit_for_approval(slack_msg):
        slack_url = SLACK_HOOK['hostname'] + SLACK_HOOK['path']
        utils.send_slack_notification(slack_msg=slack_msg, slack_url=slack_url, slack_channel=SLACK_CHANNEL_FOR_APPROVAL_TEAM)

    def submit_service_for_approval(self, payload):
        # we should get org_id from organization service for given org_uuid than from payload
        org_id = payload["org_id"]

        # service is submitted for approval. service state is APPROVAL PENDING.
        service = service_factory.create_service_entity_model(
            self._org_uuid, self._service_uuid, payload, ServiceStatus.APPROVAL_PENDING.value)

        # publish service test data on ipfs and save service submitted for approval
        service = self.obj_service_publisher_domain_service.publish_service_data_to_ipfs(
            service, EnvironmentType.TEST.value)
        service = ServicePublisherRepository().save_service(self._username, service, service.service_state.state)

        # publish service on test network
        # response = self.obj_service_publisher_domain_service.publish_service_on_blockchain(
        #     org_id=org_id, service=service, environment=EnvironmentType.TEST.value)

        # notify service contributors via email
        self.notify_service_contributor_when_user_submit_for_approval(org_id, service.service_id,
                                                                      service.contributors)

        # notify approval team via slack
        slack_msg = f"Service {service.service_id} under org_id {org_id} is submitted for approval"
        self.notify_approval_team_when_user_submit_for_approval(slack_msg=slack_msg)
        return service.to_dict()

    @staticmethod
    def publish_to_ipfs(filename, data):
        json_to_file(data, filename)
        service_metadata_ipfs_hash = IPFSUtil(
            IPFS_URL['url'], IPFS_URL['port']).write_file_in_ipfs(filename, wrap_with_directory=False)
        return service_metadata_ipfs_hash
