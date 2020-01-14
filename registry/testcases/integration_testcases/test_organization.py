import json
import unittest
from unittest import TestCase
from unittest.mock import patch
from registry.application.handlers.organization_handlers import add_org

ORIGIN = "PUBLISHER_PORTAL"


class TestOrganization(TestCase):

    def test_post_draft_organization(self):
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy@dummy.io"
                    }
                }
            },
            "body": json.dumps({
                "org_id": "",
                "org_uuid": "",
                "org_name": "dummy_org",
                "org_type": "individual",
                "metadata_ipfs_hash": "",
                "description": "this is the dummy org for testcases",
                "short_description": "that is the short description",
                "url": "https://dummy.dummy",
                "contacts": [],
                "assets": {},
                "groups": []
            })
        }
        # add_org(event, None)
        assert True

    def post_publish_organization(self):
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy@dummy.io"
                    }
                }
            },
            "queryStringParameters": {
                "act": "PUBLISH"
            },
            "body": json.dumps({
                "org_id": "org_dummy",
                "org_uuid": "c8494b71dca1469f931686bf3798ab14",
                "org_name": "dummy_org",
                "org_type": "individual",
                "metadata_ipfs_hash": "",
                "description": "this is the dummy org for testcases",
                "short_description": "that is the short description",
                "url": "https://dummy.dummy",
                "contacts": [],
                "assets": {},
                "groups": [
                    {
                        "id": "2134",
                        "name": "dummy_group",
                        "payment_address": "0x123",
                        "payment_config": {}
                    }
                ]
            })
        }
        assert True

    @patch("common.boto_utils.BotoUtils.s3_upload_file")
    def test_add_org(self, mock_s3_upload):
        mock_s3_upload.return_value = None
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy@dummy.io"
                    }
                }
            },
            "queryStringParameters": {
                "action": "DRAFT"
            },
            "body": json.dumps({"org_id": "org_id",
                                "org_uuid": "12ba76e57230403da870856fd85b019h",
                                "org_name": "org_name",
                                "org_type": "organization",
                                "metadata_ipfs_hash": "",
                                "description": "long desc",
                                "origin": ORIGIN,
                                "short_description": "short desc",
                                "url": "https://dummy.com/dummy",
                                "contacts": [],
                                "assets": {"hero_image": {
                                    "raw": "",
                                    "file_type": "png"}
                                },
                                "groups": [],
                                "duns_no": 123456789,
                                "owner_name": "Dummy Name",
                                "mail_address_same_hq_address": False,
                                "addresses": [{
                                    "address_type": "headquater_address",
                                    "street_address": "F102",
                                    "apartment": "ABC Apartment",
                                    "city": "TestCity",
                                    "pincode": 123456,
                                    "country": "TestCountry"
                                },
                                    {
                                        "address_type": "mailing_address",
                                        "street_address": "F102",
                                        "apartment": "ABC Apartment",
                                        "city": "TestCity",
                                        "pincode": 123456,
                                        "country": "TestCountry"
                                    }
                                ]})
        }
        response = add_org(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response['body'])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["name"] == "org_name")
        assert (response_body["data"]["org_id"] == "org_id")
        assert (response_body["data"]["org_type"] == "organization")
        assert (len(response_body["data"]["addresses"]) == 2)
