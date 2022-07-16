from datetime import datetime
from unittest import TestCase

from registry.domain.services.service_publisher_domain_service import ServicePublisherDomainService
from registry.infrastructure.models import Service


class TestServicePublisherDomainService(TestCase):
    def setUp(self):
        pass

    def test_publish_service_assets(self):
        org_uuid: str = "ec4e8b021def46ae94d47b99ac86d750"
        service_uuid: str = "3b79b09df4a74d5bace7dedc36061b24"
        current_time = datetime.now()
        assets = {"hero_image": {
            "url": "https://ropsten-marketplace-service-assets.s3.us-east-1.amazonaws.com/ec4e8b021def46ae94d47b99ac86d750/services/3b79b09df4a74d5bace7dedc36061b24/assets/20220606085939_asset.png",
            "ipfs_hash": "QmRJxPxYUedFxe5zUfd7mBMUKwHjkMEwXD3G8AiEFvf7q3/20220606085939_asset.png"}, "proto_files": {
            "url": "https://ropsten-marketplace-service-assets.s3.us-east-1.amazonaws.com/ec4e8b021def46ae94d47b99ac86d750/services/3b79b09df4a74d5bace7dedc36061b24/proto/20220606090033_proto_files.zip",
            "status": "SUCCEEDED", "ipfs_hash": "QmYiR3qEwnwKMvFMaJhVhErweWmD2AWBuEHh62RhygT9RZ"}}
        test_service = Service(org_uuid=org_uuid, uuid=service_uuid, display_name="123", service_id="test_service",
                               created_on=current_time, assets=assets)
        service = ServicePublisherDomainService("test", "ec4e8b021def46ae94d47b99ac86d750",
                                                "3b79b09df4a74d5bace7dedc36061b24")
        assets_details = service.publish_service_proto_to_ipfs(test_service)
        self.assertEqual(assets_details.assets["proto_files"]["ipfs_hash"],
                         "QmZviR51vuwf6Fgju31VjMKaBKgyNrjHnFcVLDHGMv5nH1")
