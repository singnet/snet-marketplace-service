import unittest

from contract_api.infrastructure.models import Banner, CTA
from contract_api.infrastructure.repositories.ui_content_repository import UIContentRepository
from contract_api.services.banner_service import BannerService


class MyTestCase(unittest.TestCase):
    def setUp(self):
        repo = UIContentRepository()
        repo.delete_banners()
        banner_list = [
            Banner(id=1, image="dummy_image"
                   , image_alignment="LEFT", alt_text="minecraft",
                   title="Song/Splitter.", rank=1, description="dflkajflajsdflkj"),
            Banner(id=2, image="dummy_image"
                   , image_alignment="LEFT", alt_text="minecraft",
                   title="Song/Splitter.", rank=1, description="dflkajflajsdflkj"),
            Banner(id=3, image="dummy_image"
                   , image_alignment="LEFT", alt_text="minecraft",
                   title="Song/Splitter.", rank=1, description="dflkajflajsdflkj")
        ]
        cta_list = [
            CTA(id=1, banner_id=1, text="abc", url="www.google.com", type="primary", variant="contained", rank=1),
            CTA(id=2, banner_id=1, text="abc", url="www.google.com", type="primary", variant="contained", rank=2),
            CTA(id=3, banner_id=2, text="abc", url="www.google.com", type="primary", variant="text", rank=1),
            CTA(id=4, banner_id=2, text="abc", url="www.google.com", type="primary", variant="contained", rank=2),
            CTA(id=5, banner_id=3, text="abc", url="www.google.com", type="primary", variant="outlined", rank=1),
            CTA(id=6, banner_id=3, text="abc", url="www.google.com", type="primary", variant="contained", rank=2)]
        repo.add_all_items(banner_list)
        repo.add_all_items(cta_list)

    def test_get_banners(self):
        banner_service = BannerService()
        response = banner_service.get_banners()
        expected_response = [{'id': 1, 'image': 'dummy_image', 'alt_text': 'minecraft', 'image_alignment': 'LEFT',
                              'title': 'Song/Splitter.', 'description': 'dflkajflajsdflkj', 'cta': [
                {'id': 1, 'text': 'abc', 'url': 'www.google.com', 'type': 'primary', 'variant': 'contained'},
                {'id': 2, 'text': 'abc', 'url': 'www.google.com', 'type': 'primary', 'variant': 'contained'}]},
                             {'id': 2, 'image': 'dummy_image', 'alt_text': 'minecraft', 'image_alignment': 'LEFT',
                              'title': 'Song/Splitter.', 'description': 'dflkajflajsdflkj', 'cta': [
                                 {'id': 3, 'text': 'abc', 'url': 'www.google.com', 'type': 'primary',
                                  'variant': 'text'},
                                 {'id': 4, 'text': 'abc', 'url': 'www.google.com', 'type': 'primary',
                                  'variant': 'contained'}]},
                             {'id': 3, 'image': 'dummy_image', 'alt_text': 'minecraft', 'image_alignment': 'LEFT',
                              'title': 'Song/Splitter.', 'description': 'dflkajflajsdflkj', 'cta': [
                                 {'id': 5, 'text': 'abc', 'url': 'www.google.com', 'type': 'primary',
                                  'variant': 'outlined'},
                                 {'id': 6, 'text': 'abc', 'url': 'www.google.com', 'type': 'primary',
                                  'variant': 'contained'}]}]
        self.assertListEqual(expected_response, response)


    def tearDown(self):
        repo = UIContentRepository()
        repo.delete_banners()