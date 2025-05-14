from pydantic import ValidationError

from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from registry.application.access_control.authorization import secured
from registry.application.handlers.common import RequestContext
from registry.application.schemas.organization import (
    GetGroupByOrganizationIdRequest,
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    PublishOrganizationRequest,
    SaveTransactionHashForOrganizationRequest,
    GetAllMembersRequest,
    GetMemberRequest,
    InviteMembersRequest,
    VerifyCodeRequest,
    PublishMembersRequest,
    DeleteMembersRequest,
    RegisterMemberRequest,
    VerifyOrgRequest,
    VerifyOrgIdRequest,
)
from registry.application.services.org_transaction_status import (
    OrganizationTransactionStatus,
)
from registry.application.services.organization_publisher_service import (
    OrganizationPublisherService,
)
from registry.config import NETWORK_ID, SLACK_HOOK
from registry.constants import Action
from registry.exceptions import BadRequestException, EXCEPTIONS

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_all_org(event, context):
    req_ctx = RequestContext(event)

    response = OrganizationPublisherService().get_all_org_for_user(username=req_ctx.username)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(
    action=Action.CREATE,
    org_uuid_path=("pathParameters", "org_uuid"),
    username_path=("requestContext", "authorizer", "claims", "email"),
)
def get_group_for_org(event, context):
    try:
        request = GetGroupByOrganizationIdRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().get_groups_for_org(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def create_organization(event, context):
    req_ctx = RequestContext(event)

    try:
        request = CreateOrganizationRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().create_organization(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(
    action=Action.UPDATE,
    org_uuid_path=("pathParameters", "org_uuid"),
    username_path=("requestContext", "authorizer", "claims", "email"),
)
def update_org(event, context):
    req_ctx = RequestContext(event)

    try:
        request = UpdateOrganizationRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().update_organization(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(
    action=Action.CREATE,
    org_uuid_path=("pathParameters", "org_uuid"),
    username_path=("requestContext", "authorizer", "claims", "email"),
)
def publish_organization(event, context):
    req_ctx = RequestContext(event)

    try:
        request = PublishOrganizationRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().publish_organization(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(
    action=Action.CREATE,
    org_uuid_path=("pathParameters", "org_uuid"),
    username_path=("requestContext", "authorizer", "claims", "email"),
)
def save_transaction_hash_for_publish_org(event, context):
    req_ctx = RequestContext(event)

    try:
        request = SaveTransactionHashForOrganizationRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().save_transaction_hash_for_publish_org(
        req_ctx.username, request
    )

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(
    action=Action.CREATE,
    org_uuid_path=("pathParameters", "org_uuid"),
    username_path=("requestContext", "authorizer", "claims", "email"),
)
def get_all_members(event, context):
    try:
        request = GetAllMembersRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().get_all_member(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(
    action=Action.CREATE,
    org_uuid_path=("pathParameters", "org_uuid"),
    username_path=("requestContext", "authorizer", "claims", "email"),
)
def get_member(event, context):
    req_ctx = RequestContext(event)

    try:
        request = GetMemberRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().get_member(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(
    action=Action.CREATE,
    org_uuid_path=("pathParameters", "org_uuid"),
    username_path=("requestContext", "authorizer", "claims", "email"),
)
def invite_members(event, context):
    try:
        request = InviteMembersRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException

    response = OrganizationPublisherService().invite_members(request)

    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def verify_code(event, context):
    req_ctx = RequestContext(event)

    try:
        request = VerifyCodeRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().verify_invite(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(
    action=Action.CREATE,
    org_uuid_path=("pathParameters", "org_uuid"),
    username_path=("requestContext", "authorizer", "claims", "email"),
)
def publish_members(event, context):
    req_ctx = RequestContext(event)

    try:
        request = PublishMembersRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().publish_members(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def delete_members(event, context):
    req_ctx = RequestContext(event)

    try:
        request = DeleteMembersRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().delete_members(req_ctx.username, request)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def register_member(event, context):
    req_ctx = RequestContext(event)

    try:
        request = RegisterMemberRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException()

    response = OrganizationPublisherService().register_member(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def org_verification(event, context):
    try:
        request = VerifyOrgRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException

    response = OrganizationPublisherService().update_verification(request)

    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=False,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def verify_org_id(event, context):
    try:
        request = VerifyOrgIdRequest.validate_event(event)
    except ValidationError:
        raise BadRequestException

    response = OrganizationPublisherService().get_org_id_availability_status(request)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}},
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def update_transaction(event, context):
    OrganizationTransactionStatus().update_transaction_status()
    return generate_lambda_response(StatusCode.OK, "OK")
