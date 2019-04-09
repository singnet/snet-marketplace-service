import sys
print(sys.executable)
print("\n".join(sys.path))
import json
import sqlite3
import unittest
from unittest.mock import patch

from nose.tools import assert_equal

from contract_api import lambda_handler


class TestContractAPI(unittest.TestCase):
    def setUp(self):
        self.event = {'httpMethod': 'GET', 'requestContext': {'stage': 'kovan'}}
        self.conn = sqlite3.connect('test.db')

    @patch('contract_api.service.Service.get_curated_services')
    def test_request_handler(self, mock_get, key="getSrvcData"):
        self.c = self.conn.cursor()
        self.c.execute("SELECT mock_data FROM mock_data WHERE mock_key = '{}' limit 1".format(key))
        mock_get.return_value = self.c.fetchone()[0]
        self.c.close()
        self.event['path'] = '/service'
        response = lambda_handler.request_handler(self.event, context=None)
        assert_equal(response['body'], json.dumps({"status": "success", "data": mock_get.return_value}))


if __name__ == '__main__':
    unittest.main()
