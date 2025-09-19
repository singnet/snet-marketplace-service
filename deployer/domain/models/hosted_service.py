from dataclasses import dataclass

from deployer.domain.models.base_domain import BaseDomain
from deployer.infrastructure.models import DeploymentStatus


@dataclass
class NewHostedServiceDomain:
    id: str
    daemon_id: str
    status: DeploymentStatus
    github_url: str
    last_commit_url: str


@dataclass
class HostedServiceDomain(NewHostedServiceDomain, BaseDomain):
    pass
