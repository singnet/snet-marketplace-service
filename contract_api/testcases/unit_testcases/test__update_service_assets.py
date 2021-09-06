import json
from unittest import TestCase
from unittest.mock import patch

from contract_api.handlers.service_handlers import trigger_demo_component_build


class TestServiceAssets(TestCase):

    @patch("common.boto_utils.BotoUtils.trigger_code_build")
    def test_trigger_demo_component_build(self, mock_code_build_trigger):
        key = 'assets/test_org_id/test_service_id/component.tar.gz'
        event = {
            'Records': [
                {'s3': {'bucket': {'name': 'ropsten-service-components'},
                        'object': {'key': key}
                        }
                 }
            ]
        }
        mock_code_build_trigger.return_value = {'build': {'id': "dummy_build_id"}}
        response = trigger_demo_component_build(event=event, context=None)
        assert response["statusCode"] == 201
        assert json.loads(response["body"])["data"] == "dummy_build_id"

        key = 'asset/test_org_id/test_service_id/component.tar.gz'
        event = {
            'Records': [
                {'s3': {'bucket': {'name': 'ropsten-service-components'},
                        'object': {'key': key}
                        }
                 }
            ]
        }
        response = trigger_demo_component_build(event=event, context=None)
        assert response["statusCode"] == 500

        key = 'assets/test_org_id/test_service_id/component.ar.gz'
        event = {
            'Records': [
                {'s3': {'bucket': {'name': 'ropsten-service-components'},
                        'object': {'key': key}
                        }
                 }
            ]
        }
        response = trigger_demo_component_build(event=event, context=None)
        assert response["statusCode"] == 500

        key = 'assets//test_service_id/component.ar.gz'
        event = {
            'Records': [
                {'s3': {'bucket': {'name': 'ropsten-service-components'},
                        'object': {'key': key}
                        }
                 }
            ]
        }
        response = trigger_demo_component_build(event=event, context=None)
        assert response["statusCode"] == 500