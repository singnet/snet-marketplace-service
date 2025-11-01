import io
import tarfile
from typing import List

from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.storage_provider import StorageProvider
from common.utils import generate_uuid
from deployer.application.schemas.deployments_schemas import (
    InitiateDeploymentRequest,
    SearchDeploymentsRequest,
    RegistryEventConsumerRequest,
)
from deployer.config import DEFAULT_DAEMON_STORAGE_TYPE, REGION_NAME, DEPLOY_SERVICE_TOPIC_ARN
from deployer.constant import AllowedRegistryEventNames
from deployer.domain.models.daemon import NewDaemonDomain, DaemonDomain
from deployer.domain.models.hosted_service import NewHostedServiceDomain, HostedServiceDomain
from deployer.exceptions import DaemonAlreadyExistsException
from deployer.infrastructure.clients.deployer_client import DeployerClient
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import DeploymentStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.hosted_service_repository import HostedServiceRepository
from deployer.utils import get_daemon_endpoint


logger = get_logger(__name__)


class DeploymentsService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._haas_client = HaaSClient()
        self._storage_provider = StorageProvider()
        self._deployer_client = DeployerClient()
        self._boto_utils = BotoUtils(REGION_NAME)

    def initiate_deployment(self, request: InitiateDeploymentRequest, account_id: str) -> dict:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(session, request.org_id, request.service_id)

            if daemon is not None:
                raise DaemonAlreadyExistsException(request.org_id, request.service_id)

            daemon_id = generate_uuid()

            daemon_config = {"payment_channel_storage_type": DEFAULT_DAEMON_STORAGE_TYPE.value}
            if request.only_daemon:
                daemon_config["is_service_hosted"] = False
                daemon_config["service_endpoint"] = request.service_endpoint
                if request.service_credentials is not None:
                    daemon_config["service_credentials"] = request.service_credentials
            else:
                daemon_config["is_service_hosted"] = True
                daemon_config["service_endpoint"] = ""

            DaemonRepository.create_daemon(
                session,
                NewDaemonDomain(
                    id=daemon_id,
                    account_id=account_id,
                    org_id=request.org_id,
                    service_id=request.service_id,
                    status=DeploymentStatus.INIT,
                    daemon_config=daemon_config,
                    daemon_endpoint=get_daemon_endpoint(request.org_id, request.service_id),
                ),
            )

            if not request.only_daemon:
                HostedServiceRepository.create_hosted_service(
                    session,
                    NewHostedServiceDomain(
                        id=generate_uuid(),
                        daemon_id=daemon_id,
                        status=DeploymentStatus.INIT,
                        github_url=request.github_url,
                        last_commit_url="",
                    ),
                )

        return {}

    def get_user_deployments(self, account_id: str) -> List[dict]:
        with session_scope(self.session_factory) as session:
            daemons = DaemonRepository.get_user_daemons(session, account_id)
        return [daemon.to_short_response() for daemon in daemons]

    def search_deployments(self, request: SearchDeploymentsRequest):
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(session, request.org_id, request.service_id)
        if daemon is None:
            return {"daemon": {}, "hostedService": {}}
        return daemon.to_response()

    def get_public_key(self) -> dict:
        public_key = self._haas_client.get_public_key()
        return {"publicKey": public_key}

    def process_registry_event(self, request: RegistryEventConsumerRequest) -> None:
        event_name = request.event_name
        org_id = request.org_id
        service_id = request.service_id

        if event_name not in AllowedRegistryEventNames:
            logger.info(f"Event {event_name} doesn't need to be processed")
            return

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(session, org_id, service_id)
            if daemon is None:
                logger.info(f"Service (org_id {org_id}, service_id {service_id}) doesn't use HaaS")
                return
            daemon_id = daemon.id

            if event_name == AllowedRegistryEventNames.SERVICE_DELETED:
                self._delete_deployments(daemon, session)
                return

            metadata: dict = self._storage_provider.get(request.metadata_uri)
            try:
                daemon_group = metadata["groups"][0]
                group_name = daemon_group["group_name"]
                service_api_source = metadata["service_api_source"]
            except KeyError or IndexError as e:
                logger.exception(
                    f"Failed to get daemon group, endpoint or service api source from metadata: {metadata}. Exception: {e}",
                    exc_info=True,
                )
                raise Exception()

            service_class = self._get_service_class(service_api_source)

            new_config = daemon.daemon_config
            new_config["daemon_group"] = group_name
            new_config["service_class"] = service_class

            DaemonRepository.update_daemon_config(session, daemon_id, new_config)

            self._deployer_client.deploy_daemon(daemon_id, asynchronous=True)

            if (
                event_name == AllowedRegistryEventNames.SERVICE_CREATED
                and daemon.hosted_service is not None
            ):
                self._push_deploy_service_event(org_id, service_id, daemon.hosted_service)

    def _get_service_class(self, service_api_source: str) -> str:
        tar_bytes = self._storage_provider.get(service_api_source, to_decode=False)
        tar_stream = io.BytesIO(tar_bytes)

        try:
            with tarfile.open(fileobj=tar_stream, mode="r:*") as tar:
                members = [m for m in tar.getmembers() if m.isfile()]

                if not members:
                    raise Exception("No files found in tar archive")

                first_member = members[0]
                file_content = tar.extractfile(first_member)

                if file_content is None:
                    raise Exception("Failed to extract file from tar archive")

                content_text = file_content.read().decode("utf-8")

                for line in content_text.splitlines():
                    line = line.strip()
                    if line.startswith("package ") and line.endswith(";"):
                        package_line = line
                        package_name = package_line.replace("package ", "").replace(";", "").strip()
                        return package_name

        except (tarfile.TarError, IOError, UnicodeDecodeError, Exception) as e:
            raise Exception(f"Error processing tar file: {e}")

    def _delete_deployments(self, daemon: DaemonDomain, session) -> None:
        if daemon.status == DeploymentStatus.UP:
            self._haas_client.delete_daemon(daemon.org_id, daemon.service_id)
            DaemonRepository.update_daemon_status(session, daemon.id, DeploymentStatus.DOWN)
        if (
            daemon.hosted_service is not None
            and daemon.hosted_service.status == DeploymentStatus.UP
        ):
            self._haas_client.delete_hosted_service(daemon.org_id, daemon.service_id)
            HostedServiceRepository.update_hosted_service_status(
                session, daemon.hosted_service.id, DeploymentStatus.DOWN
            )

    def _push_deploy_service_event(
        self, org_id: str, service_id: str, hosted_service: HostedServiceDomain
    ) -> None:
        # TODO: rewrite payload if needed
        self._boto_utils.publish_data_to_sns_topic(
            topic_arn=DEPLOY_SERVICE_TOPIC_ARN,
            payload={
                "org_id": org_id,
                "service_id": service_id,
                "github_url": hosted_service.github_url,
                "last_commit_url": hosted_service.last_commit_url,
            },
        )
