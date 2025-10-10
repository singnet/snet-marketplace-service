from common.lambda_client import LambdaClient
from common.logger import get_logger
from deployer.config import (
    REGION_NAME,
    START_DAEMON_ARN,
)


logger = get_logger(__name__)


class DeployerClient(LambdaClient):
    def __init__(self):
        super().__init__(REGION_NAME)

    def deploy_daemon(self, daemon_id: str, asynchronous=False):
        return self._invoke_lambda(
            lambda_function_arn=START_DAEMON_ARN,
            path_parameters={"daemonId": daemon_id},
            asynchronous=asynchronous,
        )
