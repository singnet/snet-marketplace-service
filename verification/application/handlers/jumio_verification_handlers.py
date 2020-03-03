from common.constant import ResponseStatus, StatusCode
from common.utils import generate_lambda_response
from verification.application.services.verification_manager import VerificationManager
from verification.exceptions import BadRequestException


def submit(event, context):
    query_parameters = event["queryStringParameters"]
    path_parameters = event["pathParameters"]
    if "transactionStatus" not in query_parameters:
        raise BadRequestException()
    status = query_parameters["transactionStatus"]
    verification_id = path_parameters["verification_id"]
    redirect_url = VerificationManager().submit(verification_id, status)

    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": {}},
                                    cors_enabled=True, headers={"location": redirect_url})
