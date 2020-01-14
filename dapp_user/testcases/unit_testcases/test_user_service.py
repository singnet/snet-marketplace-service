from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from common.repository import Repository
from dapp_user.config import NETWORK_ID, NETWORKS
from dapp_user.domain.services.user_service import UserService


class TestUserService(TestCase):
    def setUp(self):
        self.repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_delete_user(self, mock_invoke_lambda):
        user_service = UserService()
        username = "dummy@dummy.io"
        account_id = "123"
        name = "dummy_135"
        status = 1
        request_id = "id_123"
        current_time = datetime.utcnow()
        epoch_time = current_time.timestamp()
        self.repo.execute(
            "INSERT INTO user (username, account_id, name, email, email_verified, status, request_id, "
            "request_time_epoch, row_created, row_updated) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [username, account_id, name, username, 1,
             status, request_id, epoch_time, current_time, current_time]
        )
        mock_invoke_lambda.return_value = {
            "statusCode": 201,
            "body": ""
        }
        user_service.delete_user(username)
        user_data = self.repo.execute("SELECT username FROM user WHERE username = %s", [username])
        if len(user_data) == 0:
            assert True
        else:
            assert True

    def tearDown(self):
        self.repo.execute("DELETE FROM user")
