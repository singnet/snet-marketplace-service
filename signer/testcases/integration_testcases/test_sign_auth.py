import unittest
from unittest.mock import patch

from signer.infrastructure.authenticators.signature_authenticator import main


class TestSignAuth(unittest.TestCase):
    @patch("boto3.client")
    def test_generate_sign(self,mock_boto_client):
        mock_boto_client.return_value=None
        username = 'test-user'
        org_id = 'snet'
        group_id = 'cOyJHJdvvig73r+o8pijgMDcXOX+bt8LkvIeQbufP7g='
        service_id = 'example-service'
        block_number = 1234
        signature = 'h9Ssz1bi+aT4NKERkGqJOfx2E9/4Y9czj+YNr4XzXDcnlay37v9Jfown278MFF+VrKsz1r1Ip/CeppwtjhiBtAA='
        headers = {
            'x-username': username,
            'x-organizationid': org_id,
            'x-groupid': group_id,
            'x-serviceid': service_id,
            'x-currentblocknumber': block_number,
            'x-signature': signature
        }
        event = dict()
        event['headers'] = headers
        event['methodArn'] = 'abc'
        response = main(event, None)
        # assert response['policyDocument']['Statement'][0]['Effect'] == 'Allow'


if __name__ == '__main__':
    unittest.main()
