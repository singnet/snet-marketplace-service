from contract_api.domain.models.ui_content_banner import Banner
from contract_api.domain.models.ui_content_cta import CTA


class UIContentFactory:
    @staticmethod
    def banner_domain_entity_from_repo_model(banner_db):
        return Banner(banner_db.id, banner_db.image, banner_db.image_alignment,
                      banner_db.alt_text,
                      banner_db.title, banner_db.rank,
                      banner_db.description)

    @staticmethod
    def cta_domain_entity_from_repo_model(cta_db):
        return CTA(cta_db.id, cta_db.text, cta_db.url, cta_db.type,
                   cta_db.variant, cta_db.rank)

    @staticmethod
    def carousel_from_banner_cta_list(repo_model):
        carousel = []
        for (index,model) in enumerate(repo_model):
            banner = UIContentFactory.banner_domain_entity_from_repo_model(model)
            carousel.append({"id": banner.id, "image": banner.image,
                                 "alt_text": banner.alt_text, "image_alignment": banner.image_alignment,
                                 "title": banner.title, "description": banner.description,"cta":[]})
            for data in model.cta_order_rank:
                cta = UIContentFactory.cta_domain_entity_from_repo_model(data)
                carousel[index]["cta"].append({
                    "id": cta.id,
                    "text": cta.text, "url": cta.url,
                    "type":cta.type, "variant": cta.variant
                })
        return carousel
