import json
import sqlite3
import unittest
import web3
from unittest.mock import Mock, patch

from nose.tools import assert_equal
from nose.tools import assert_dict_equal

from common.repository import Repository
from contract_api import lambda_handler
from contract_api.service import Service
from eth_account.messages import defunct_hash_message

class TestContractAPI(unittest.TestCase):
    def setUp(self):
        self.net_id = 42
        self.event = {'httpMethod': 'GET', 'requestContext': {'stage': 'kovan'}}
        self.conn = sqlite3.connect('test.db')
        self.obj_repo = Repository(net_id=self.net_id)
        self.obj_srvc = Service(obj_repo=self.obj_repo)


    def test_request_handler_without_path(self):
        response = lambda_handler.request_handler(self.event, context=None)
        assert_equal(response['statusCode'], '400')

    @patch('common.utils.Utils.report_slack')
    def test_request_handler_without_httpMethod(self, mock_get):
        self.event['path'] = '/service'
        self.event.pop('httpMethod')
        mock_get.return_value = Mock()
        response = lambda_handler.request_handler(self.event, context=None)
        self.event['httpMethod'] = 'GET'
        assert_equal(response['statusCode'], 500)

    @patch('common.utils.Utils.report_slack')
    def test_request_handler_without_requestContext(self, mock_get):
        self.event['path'] = '/service'
        self.event.pop('requestContext')
        mock_get.return_value = Mock()
        response = lambda_handler.request_handler(self.event, context=None)
        self.event['requestContext'] = {'stage': 'kovan'}
        assert_equal(response['statusCode'], 500)

    @patch('contract_api.service.Service.get_curated_services')
    def test_request_handler(self, mock_get, key="getCuratedSrvcData"):
        self.c = self.conn.cursor()
        self.c.execute("SELECT mock_data FROM mock_data WHERE mock_key = '{}' limit 1".format(key))
        mock_get.return_value = self.c.fetchone()[0]
        self.c.close()
        self.event['path'] = '/service'
        response = lambda_handler.request_handler(self.event, context=None)
        assert_equal(response['body'], json.dumps({"status": "success", "data": mock_get.return_value}))
        assert_equal(response['statusCode'], '200')

    @patch('common.repository.Repository.execute')
    def test_get_group_info(self, mock_get, key="getGrpInfoData"):
        self.c = self.conn.cursor()
        self.c.execute("SELECT mock_data FROM mock_data WHERE mock_key = '{}' limit 1".format(key))
        mock_get.return_value = json.loads(self.c.fetchone()[0])
        self.c.close()
        response = self.obj_srvc.get_group_info()
        assert_equal(response, [])


    @patch('common.repository.Repository.execute')
    def test_fetch_total_count(self, mock_get, key="fetchTotalCount"):
        self.c = self.conn.cursor()
        self.c.execute("SELECT mock_data FROM mock_data WHERE mock_key = '{}' limit 1".format(key))
        mock_get.return_value = json.loads(self.c.fetchone()[0])
        self.c.close()

    @patch('common.repository.Repository.execute')
    def test_get_profile_details(self, mock_get, key="getProfileDetailsData"):
        self.c = self.conn.cursor()
        self.c.execute("SELECT mock_data FROM mock_data WHERE mock_key = '{}' limit 1".format(key))
        mock_get.return_value = json.loads(self.c.fetchone()[0])
        self.c.close()

    def test_merge_service_data(self):
        pass


    @patch('web3.Web3')
    def test_is_valid_vote(self, mock_get):
        #     idValidVoteData = {
        #         "user_address": "0xDasddedeasdadaddaddaddad",
        #         "org_id": "test-snet",
        #         "service_id": "example-service",
        #         "up_vote": True,
        #         "down_vote": False,
        #     }
        #     mock_get.return_value = idValidVoteData['user_address'].lower()
        #     response = self.obj_srvc.is_valid_vote(net_id=self.net_id, vote_info_dict=idValidVoteData)
        #     print(response)
        pass

    @patch('contract_api.service.Service.is_valid_vote')
    def test_set_user_vote(self, mock_get):
        mock_get.return_value = True
        pass

    # def test_get_user_vote(self):
    #     pass

    def test_vote_mapping(self):
        response = self.obj_srvc.vote_mapping(vote=1)
        assert_dict_equal(response, {'up_vote': True, 'down_vote': False})


if __name__ == '__main__':
    unittest.main()
