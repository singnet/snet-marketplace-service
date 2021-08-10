import json
from unittest import TestCase
from unittest.mock import patch

from contract_api.handlers.service_handlers import trigger_demo_component_build


class TestServiceAssets(TestCase):
    pass

    @patch("common.boto_utils.BotoUtils.trigger_code_build")
    def test_trigger_demo_component_build(self, mock_code_build_trigger):
        event = {'Records': [
            {'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1',
             'eventTime': '2021-08-10T12:53:45.057Z',
             'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AIDAXYSEM4MOPXXLSNUMO'},
             'requestParameters': {'sourceIPAddress': '59.93.253.191'}, 'responseElements':
                 {'x-amz-request-id': '57RZPRGWHTJTZ5RY',
                  'x-amz-id-2': 'wxDXbsTrg5LfGk13y30FNYWLfJ5WDNOW5aD+ZfkgP/2d5xTL3TZK7Nf8WSuLL/X1EFLDSbA+N0Nm1UCxZRQ/fKzd2nC6tipW'},
             's3': {'s3SchemaVersion': '1.0', 'configurationId': '8fc3c6dd-818b-4b4c-b980-fe0dcd4bb90a',
                    'bucket': {'name': 'ropsten-service-components', 'ownerIdentity': {'principalId': 'A1AEOFBS4PX33'},
                               'arn': 'arn:aws:s3:::ropsten-service-components'},
                    'object': {'key': 'assets/test_org_id/test_service_id/proto.tar.gz',
                               'size': 328, 'eTag': '3178507eb519d4b5dd8185786dc2b94d',
                               'sequencer': '00611276DF6ED36860'}}}]}
        mock_code_build_trigger.return_value = {'build': {'id': "dummy_build_id"}}
        response = trigger_demo_component_build(event=event, context=None)
        assert response["statusCode"] == 201
        assert json.loads(response["body"])["data"] == "dummy_build_id"
