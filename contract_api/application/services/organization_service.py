from common.logger import get_logger
from common.utils import Utils
from infrastructure.repositories.organization_repository import OrganizationRepository

logger = get_logger(__name__)


class OrganizationService:

    def __init__(self):
        self.repo = OrganizationRepository
        self.obj_utils = Utils()