from contract_api.infrastructure.repositories.ui_content_repository import UIContentRepository
from contract_api.domain.factory.ui_content_factory import UIContentFactory

class BannerService:
    def get_banners(self):
        banners_db = UIContentRepository().get_banners()
        response = UIContentFactory.carousel_from_banner_cta_list(banners_db)
        return response
