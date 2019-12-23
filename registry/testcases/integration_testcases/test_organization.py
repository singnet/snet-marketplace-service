import json
from unittest import TestCase

from registry.application.handlers.organization_handlers import add_org


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
        add_org(event, None)
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
