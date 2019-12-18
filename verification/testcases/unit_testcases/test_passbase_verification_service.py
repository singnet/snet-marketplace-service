import unittest
import json

from requests import Response
from unittest.mock import patch
from verification.services.passbase_verification_service import PassbaseVerificationService


class PassbaseVerificationServiceTestCase(unittest.TestCase):

    @patch("requests.get")
    def test_get_all_authentications(self, mock_requests):
        mock_response_json = {"authentications": [{"key": "b007b547-8a2c-4e46-9fe0-514398d1be58", "reviewed_at": None, "review_status": None, "created_at": "2019-12-18T06:03:32.692Z", "additional_attributes": {"identifier": "vivek.n@singularitynet.io", "country_code": "in", "identifier_type": "email", "customer_user_id": "1234567"}, "authentication_assessments": {"facematch": {"value": "0.0"}, "id_authenticity": {"value": "0.0"}, "liveness": {"value": "0.9133184035386636"}, "overall": {"value": "0.2283296008846659"}}, "authentication_document": "NATIONAL_ID_CARD", "additional_document": None, "documents": [{"document_type": "NATIONAL_ID_CARD", "document_information": [{"key": "DATE_OF_EXPIRY", "value": None}, {"key": "DATE_OF_ISSUE", "value": None}, {"key": "DATE_OF_BIRTH", "value": None}, {"key": "NATIONALITY", "value": "India"}]}, {"document_type": None, "document_information": []}], "end_user":{"customer_user_id": "1234567"}}, {
            "key": "05bd4d91-acf6-4f24-972f-fd1e315a9f18", "reviewed_at": "2019-12-18T08:03:16.239Z", "review_status": False, "created_at": "2019-12-18T07:58:08.924Z", "additional_attributes": {"identifier": "vivek.n@singularitynet.io", "country_code": "in", "identifier_type": "email", "customer_user_id": "123"}, "authentication_assessments": {"facematch": {"value": "0.0"}, "id_authenticity": {"value": "0.0"}, "liveness": {"value": "0.930943828332993"}, "overall": {"value": "0.23273595708324826"}}, "authentication_document": "NATIONAL_ID_CARD", "additional_document": None, "documents": [{"document_type": "NATIONAL_ID_CARD", "document_information": [{"key": "DATE_OF_EXPIRY", "value": None}, {"key": "DATE_OF_ISSUE", "value": None}, {"key": "DATE_OF_BIRTH", "value": None}, {"key": "NATIONALITY", "value": "India"}]}, {"document_type": None, "document_information": []}], "end_user":{"customer_user_id": "123"}}], "number_of_authentications": 2, "status": "success", "code": "200"}

        response_obj = Response()
        response_obj.__setattr__("status_code", 200)
        response_obj.__setattr__("_content", json.dumps(
            mock_response_json).encode("utf-8"))

        mock_requests.return_value = response_obj

        response = PassbaseVerificationService().get_all_authentications()

        assert(response == {"authentications": [{"key": "b007b547-8a2c-4e46-9fe0-514398d1be58", "reviewed_at": None, "review_status": None, "created_at": "2019-12-18T06:03:32.692Z", "additional_attributes": {"identifier": "vivek.n@singularitynet.io", "country_code": "in", "identifier_type": "email", "customer_user_id": "1234567"}, "authentication_assessments": {"facematch": {"value": "0.0"}, "id_authenticity": {"value": "0.0"}, "liveness": {"value": "0.9133184035386636"}, "overall": {"value": "0.2283296008846659"}}, "authentication_document": "NATIONAL_ID_CARD", "additional_document": None, "documents": [{"document_type": "NATIONAL_ID_CARD", "document_information": [{"key": "DATE_OF_EXPIRY", "value": None}, {"key": "DATE_OF_ISSUE", "value": None}, {"key": "DATE_OF_BIRTH", "value": None}, {"key": "NATIONALITY", "value": "India"}]}, {"document_type": None, "document_information": []}], "end_user":{"customer_user_id": "1234567"}}, {
               "key": "05bd4d91-acf6-4f24-972f-fd1e315a9f18", "reviewed_at": "2019-12-18T08:03:16.239Z", "review_status": False, "created_at": "2019-12-18T07:58:08.924Z", "additional_attributes": {"identifier": "vivek.n@singularitynet.io", "country_code": "in", "identifier_type": "email", "customer_user_id": "123"}, "authentication_assessments": {"facematch": {"value": "0.0"}, "id_authenticity": {"value": "0.0"}, "liveness": {"value": "0.930943828332993"}, "overall": {"value": "0.23273595708324826"}}, "authentication_document": "NATIONAL_ID_CARD", "additional_document": None, "documents": [{"document_type": "NATIONAL_ID_CARD", "document_information": [{"key": "DATE_OF_EXPIRY", "value": None}, {"key": "DATE_OF_ISSUE", "value": None}, {"key": "DATE_OF_BIRTH", "value": None}, {"key": "NATIONALITY", "value": "India"}]}, {"document_type": None, "document_information": []}], "end_user":{"customer_user_id": "123"}}], "number_of_authentications": 2, "status": "success", "code": "200"})
