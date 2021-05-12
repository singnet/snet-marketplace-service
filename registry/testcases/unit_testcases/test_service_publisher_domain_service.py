from unittest import TestCase

from registry.constants import EnvironmentType
from registry.domain.models.service import Service
from registry.domain.models.service_group import ServiceGroup
from registry.domain.services.service_publisher_domain_service import ServicePublisherDomainService


class TestServicePublisherDomainService(TestCase):

    def test_get_service_metadata(self):
        service = Service(
            org_uuid="test_org_uuid", uuid="test_service_uuid", service_id="test_service_id",
            display_name="test_display_name", short_description="test_short_description",
            description="test_description", project_url="https://dummy.io",
            proto={"encoding": "proto", "service_type": "grpc", "model_ipfs_hash": "test_model_ipfs_hash"},
            media={
                "proto_files": {
                    "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/9887ec2e099e4afd92c4a052737eaa"
                           "97/services/7420bf47989e4afdb1797d1bba8090aa/proto/20200327130256_proto_files.zip",
                    "ipfs_hash": "QmUfDprFisFeaRnmLEqks1AFN6iam5MmTh49KcomXHEiQY"},
                "hero_image": {
                    "url": "QmUfDprFisFeaRnmLEqks1AFN6iam5MmTh49KcomXHEiQY/20200323130126_asset.png",
                    "ipfs_hash": "QmUfDprFisFeaRnmLEqks1AFN6iam5MmTh49KcomXHEiQY"},
                "demo_files": {
                    "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/9887ec2e099e4afd92c4a052737eaa"
                           "97/services/7420bf47989e4afdb1797d1bba8090aa/component/20200401121414_component.zip",
                    "ipfs_hash": "QmUfDprFisFeaRnmLEqks1AFN6iam5MmTh49KcomXHEiQY"
                }},
            ranking=1,
            rating={}, contributors=[{'name': 'df', 'email_id': '123@mail.io'}], tags=["1234"], mpe_address="0x123",
            metadata_uri="", groups=[
                ServiceGroup(
                    org_uuid="test_org_uuid", service_uuid="test_service_uuid",
                    group_id="test", group_name="test_name",
                    endpoints={"https://dummydaemonendpoint.io": {"verfied": True}},
                    test_endpoints=["https://dummydaemonendpoint.io"],
                    pricing=[{'default': True, 'price_model': 'fixed_price', 'price_in_cogs': 1}],
                    free_calls=10, daemon_address=["0xq2w3e4rr5t6y7u8i9"],
                    free_call_signer_address="0xq2s3e4r5t6y7u8i9o0")], service_state=None
        )
        service_metadata = ServicePublisherDomainService("", "", "").get_service_metadata(service,
                                                                                          EnvironmentType.TEST.value)
        self.assertDictEqual(
            {'version': 1, 'display_name': 'test_display_name', 'encoding': 'proto', 'service_type': 'grpc',
             'model_ipfs_hash': 'test_model_ipfs_hash', 'mpe_address': '0x123', 'groups': [
                {'free_calls': 100, 'free_call_signer_address': '0xq2s3e4r5t6y7u8i9o0',
                 'daemon_addresses': ['0xq2w3e4rr5t6y7u8i9'],
                 'pricing': [{'default': True, 'price_model': 'fixed_price', 'price_in_cogs': 1}],
                 'endpoints': ['https://dummydaemonendpoint.io'], 'group_id': 'test', 'group_name': 'test_name'}],
             'service_description': {'url': 'https://dummy.io', 'short_description': 'test_short_description',
                                     'description': 'test_description'},
             'media': [{"order": 1, "url": "QmUfDprFisFeaRnmLEqks1AFN6iam5MmTh49KcomXHEiQY/20200323130126_asset.png", "file_type": "hero_image", "alt_text": ""}],
             'contributors': [{'name': 'df', 'email_id': '123@mail.io'}]}, service_metadata)
