# import json
# from unittest import TestCase
# from unittest.mock import patch
# from registry.application.handlers.service_handlers import verify_service_id, save_service, create_service, \
#     get_services_for_organization
#
#
# class TestService(TestCase):
#     def setUp(self):
#         pass
#
#     def test_verify_service_id(self):
#         event = {
#             "requestContext": {
#                 "authorizer": {
#                     "claims": {
#                         "email": "dummy_user1@dummy.io"
#                     }
#                 }
#             },
#             "httpMethod": "GET",
#             "pathParameters": {"org_uuid": "test_org_uuid"},
#             "queryStringParameters": {"service_id": "test_service_id"}
#         }
#         response = verify_service_id(event=event, context=None)
#         assert (response["statusCode"] == 200)
#         response_body = json.loads(response["body"])
#         assert(response_body["status"] == "success")
#
#     def test_create_service(self):
#         event = {
#             "requestContext": {
#                 "authorizer": {
#                     "claims": {
#                         "email": "dummy_user1@dummy.io"
#                     }
#                 }
#             },
#             "httpMethod": "POST",
#             "pathParameters": {"org_uuid": "test_org_uuid"},
#             "body": "{}"
#         }
#         response = create_service(event=event, context=None)
#         assert (response["statusCode"] == 200)
#         response_body = json.loads(response["body"])
#         assert(response_body["status"] == "success")
#
#     def test_get_services_for_organization(self):
#         event = {
#             "requestContext": {
#                 "authorizer": {
#                     "claims": {
#                         "email": "dummy_user1@dummy.io"
#                     }
#                 }
#             },
#             "httpMethod": "GET",
#             "pathParameters": {"org_uuid": "test_org_uuid"},
#             "body": "{}"
#         }
#         response = get_services_for_organization(event=event, context=None)
#         assert (response["statusCode"] == 200)
#         response_body = json.loads(response["body"])
#         assert(response_body["status"] == "success")
#
#     def test_save_service(self):
#         event = {
#             "path": "/org/test_org_uuid/service",
#             "requestContext": {
#                 "authorizer": {
#                     "claims": {
#                         "email": "dummy_user1@dummy.io"
#                     }
#                 }
#             },
#             "httpMethod": "PUT",
#             "pathParameters": {"org_uuid": "test_org_uuid"},
#             "body": "{}"
#         }
#         response = save_service(event=event, context=None)
#         assert (response["statusCode"] == 200)
#         response_body = json.loads(response["body"])
#         assert(response_body["status"] == "success")
#
#     def tearDown(self):
#         pass
