from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from contract_api.application.schemas.channel_schemas import GetChannelsRequest, UpdateConsumedBalanceRequest, \
    GetGroupChannelsRequest
from contract_api.application.services.channel_service import ChannelService

logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_channels(event, context):
    request = GetChannelsRequest.validate_event(event)

    response = ChannelService().get_channels(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def get_group_channels(event, context):
    request = GetGroupChannelsRequest.validate_event(event)

    response = ChannelService().get_group_channels(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def update_consumed_balance(event, context):
    request = UpdateConsumedBalanceRequest.validate_event(event)

    response = ChannelService().update_consumed_balance(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )
