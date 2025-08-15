import boto3

from deployer.config import REGION_NAME


class DeployerClientError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Deployer Client response error: {message}")


class DeployerClient:
    def __init__(self):
        self.lambda_client = boto3.client("lambda", region_name=REGION_NAME)

    def start_daemon(self, daemon_id: str):
        pass

    def stop_daemon(self, daemon_id: str):
        pass

