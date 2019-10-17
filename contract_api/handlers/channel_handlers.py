import json

from aws_xray_sdk.core import patch_all

from common.constant import StatusCode
from common.logger import get_logger
from common.repository import Repository
from common.utils import generate_lambda_response
from common.utils import Utils
from common.utils import validate_dict
from contract_api.config import NETWORK_ID
from contract_api.config import NETWORKS
from contract_api.config import SLACK_HOOK
from contract_api.mpe import MPE

patch_all()
logger = get_logger(__name__)

NETWORKS_NAME = dict(
    (NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS))
          for netId in NETWORKS.keys())
utils = Utils()


def get_channels(event, context):
    logger.info("Received request to get channel details from user address")
    try:
        query_string_parameters = event["queryStringParameters"]
        if validate_dict(query_string_parameters, ["wallet_address"]):
            wallet_address = query_string_parameters["wallet_address"]
            logger.info(
                f"Fetched values from request wallet_address: {wallet_address}"
            )
            response = MPE(
                net_id=NETWORK_ID,
                obj_repo=db[NETWORK_ID]).get_channels_by_user_address_v2(
                    wallet_address)
            status_code = StatusCode.OK
        else:
            status_code = StatusCode.BAD_REQUEST
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
    except Exception as e:
        logger.info(event)
        response = repr(e)
        utils.report_slack(1, str(response), SLACK_HOOK)
        logger.error(e)
        status_code = StatusCode.INTERNAL_SERVER_ERROR
    return generate_lambda_response(status_code=status_code,
                                    message=response,
                                    cors_enabled=True)
