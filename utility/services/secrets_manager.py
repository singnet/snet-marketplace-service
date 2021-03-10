import boto3
import base64
from botocore.exceptions import ClientError
import json
from common.logger import get_logger

logger = get_logger(__name__)

def get_cmc_secret():
    secret_name = "COIN_MARKETPLACE_API_TOKEN"
    region_name = "us-east-1"
    
    # TODO: Remove profile name
    session = boto3.session.Session(profile_name="SINGNET")
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )['SecretString']

        response = json.loads(get_secret_value_response)

        return response[secret_name]
    except ClientError as e:
        logger.error(f"Failed to fetch credentials {e}")
        raise e
