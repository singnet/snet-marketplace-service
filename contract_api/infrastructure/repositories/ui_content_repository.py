from contract_api.infrastructure.models import Banner
from contract_api.infrastructure.repositories.base_repository import BaseRepository


class UIContentRepository(BaseRepository):
    def get_banners(self):
        try:
            result = self.session.query(Banner) \
                .order_by(Banner.rank.asc()).all()
            self.session.commit()
            return result
        except Exception as e:
            self.session.rollback()
            raise e

    def delete_banners(self):
        try:
            result = self.session.query(Banner).delete()
            self.session.commit()
            return result
        except Exception as e:
            self.session.rollback()
            raise e
