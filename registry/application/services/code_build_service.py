import boto3

from common.logger import get_logger
from registry.application.services.service_publisher_service import ServicePublisherService

logger = get_logger(__name__)
client = boto3.client('codebuild')


class CodeBuild:
    def __init__(self):
        self.build_client = boto3.client('codebuild')

    def get_build_results(self, ids):
        return self.build_client.batch_get_builds(ids=ids)

    def get_code_build_status(self, org_uuid, service_uuid):
        try:
            service_repository = ServicePublisherService(org_uuid=org_uuid, service_uuid=service_uuid, username=None)
            service = service_repository.get_service_for_given_service_uuid()
            if service:
                build_id = service["media"]["demo_files"]["build_id"]
                build_response = self.get_build_results(ids=[build_id])
                build_data = [data for data in build_response['builds'] if data['id'] == build_id]
                status = build_data[0]['buildStatus']
            else:
                raise Exception(f"service for org {org_uuid} and service {service} is not found")
            return {"build_status": status}
        except self.build_client.exceptions.InvalidInputException as e:
            raise Exception(f"build_id {build_id} is not found for service {service_uuid} and org {org_uuid}")
        except client.exceptions.InvalidInputException as e:
            logger.info(f"error in triggering build_id {build_id} for service {service_uuid} and org {org_uuid}")
            raise e
