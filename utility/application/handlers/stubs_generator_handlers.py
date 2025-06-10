from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.schemas import PayloadValidationError
from utility.application.schemas import ManageProtoCompilationRequest, GeneratePythonStubsRequest
from utility.application.services.stubs_generator_service import StubsGeneratorService
from utility.exceptions import EXCEPTIONS, BadRequestException

logger = get_logger(__name__)


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def manage_proto_compilation(event, context):
    try:
        request = ManageProtoCompilationRequest.validate_event(event)
    except PayloadValidationError:
        raise BadRequestException()

    response = StubsGeneratorService().manage_proto_compilation(request)
    return {"statusCode": StatusCode.OK, "data": response}

@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def generate_python_stubs(event, context):
    try:
        request = GeneratePythonStubsRequest.validate_event(event)
    except PayloadValidationError:
        raise BadRequestException()

    response = StubsGeneratorService().generate_python_stubs(request)
    return {"statusCode": StatusCode.OK, "data": response}
