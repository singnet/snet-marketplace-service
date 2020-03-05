import unittest
import json
from unittest.mock import patch
from verification.services.verification_service import VerificationService
from requests import Response


class VerificationServiceTestCase(unittest.TestCase):

    @patch("requests.get")
    def test_get_fields(self, mock_requests):
        mock_response_json = [
            {
                "PersonInfo": {
                    "title": "PersonInfo",
                    "type": "object",
                    "properties": {
                        "FirstGivenName": {
                            "type": "string",
                            "description": "First name of the individual to be verified",
                            "label": "First Name"
                        },
                        "MiddleName": {
                            "type": "string",
                            "description": "Second given name of the individual to be verified",
                            "label": "Middle Name"
                        },
                        "FirstSurName": {
                            "type": "string",
                            "description": "Last name of the individual to be verified",
                            "label": "Last Name"
                        },
                        "DayOfBirth": {
                            "type": "int",
                            "description": "Day of birth date (e.g. 23 for a date of birth of 23/11/1975)",
                            "label": "Day Of Birth"
                        },
                        "MonthOfBirth": {
                            "type": "int",
                            "description": "Month of birth date (e.g. 11 for a date of birth of 23/11/1975)",
                            "label": "Month Of Birth"
                        },
                        "YearOfBirth": {
                            "type": "int",
                            "description": "Year of birth date (e.g. 1975 for a date of birth of 23/11/1975)",
                            "label": "Year Of Birth"
                        }
                    },
                    "required": [
                        "DayOfBirth",
                        "FirstGivenName",
                        "FirstSurName",
                        "MonthOfBirth",
                        "YearOfBirth"
                    ]
                },
                "Location": {
                    "title": "Location",
                    "type": "object",
                    "properties": {
                        "BuildingNumber": {
                            "type": "string",
                            "description": "Street number of primary residence",
                            "label": "Street Number"
                        },
                        "UnitNumber": {
                            "type": "string",
                            "description": "Flat/Unit/Apartment number of primary residence",
                            "label": "Unit Number"
                        },
                        "StreetName": {
                            "type": "string",
                            "description": "Street name of primary residence",
                            "label": "Street Name"
                        },
                        "StreetType": {
                            "type": "string",
                            "description": "Street type of primary residence (e.g. St, Rd, etc.)",
                            "label": "Street Type"
                        },
                        "Suburb": {
                            "type": "string",
                            "description": "City or Suburb of primary residence",
                            "label": "Suburb"
                        },
                        "StateProvinceCode": {
                            "type": "string",
                            "description": "State of primary residence. US sources expect 2 characters. Australian sources expect 2 or 3 characters.",
                            "label": "State"
                        },
                        "PostalCode": {
                            "type": "string",
                            "description": "ZIP Code or Postal Code of primary residence",
                            "label": "Postal Code"
                        }
                    },
                    "required": [
                        "PostalCode",
                        "StreetName"
                    ]
                },
                "Communication": {
                    "title": "Communication",
                    "type": "object",
                    "properties": {
                        "MobileNumber": {
                            "type": "string",
                            "description": "Cellular phone number",
                            "label": "Cell Number"
                        },
                        "Telephone": {
                            "type": "string",
                            "description": "Telephone number of the individual to be verified",
                            "label": "Telephone"
                        }
                    },
                    "required": []
                },
                "Passport": {
                    "title": "Passport",
                    "type": "object",
                    "properties": {
                        "Number": {
                            "type": "string",
                            "description": "Passport number of the individual to be verified",
                            "label": "Passport Number"
                        }
                    },
                    "required": [
                        "Number"
                    ]
                },
                "CountrySpecific": {
                    "title": "CountrySpecific",
                    "type": "object",
                    "properties": {
                        "AU": {
                            "title": "AU",
                            "type": "object",
                            "properties": {
                                "PassportCountry": {
                                    "type": "string",
                                    "description": "Passport Country (ISO 3166-1 alpha-2)",
                                    "label": "Passport Country"
                                },
                                "PassportNumber": {
                                    "type": "string",
                                    "description": "Passport number of the individual to be verified",
                                    "label": "Passport Number"
                                }
                            },
                            "required": [
                                "PassportCountry",
                                "PassportNumber"
                            ]
                        }
                    }
                }
            }
        ]
        response_obj = Response()
        response_obj.__setattr__("status_code", 200)
        response_obj.__setattr__("_content", json.dumps(
            mock_response_json).encode("utf-8"))
        mock_requests.return_value = response_obj

        configuration_name = "Identity Verification"
        country_code = "AU"

        response = VerificationService().get_fields(configuration_name, country_code)

        assert(response == [{'PersonInfo': {'title': 'PersonInfo', 'type': 'object', 'properties': {'FirstGivenName': {'type': 'string', 'description': 'First name of the individual to be verified', 'label': 'First Name'}, 'MiddleName': {'type': 'string', 'description': 'Second given name of the individual to be verified', 'label': 'Middle Name'}, 'FirstSurName': {'type': 'string', 'description': 'Last name of the individual to be verified', 'label': 'Last Name'}, 'DayOfBirth': {'type': 'int', 'description': 'Day of birth date (e.g. 23 for a date of birth of 23/11/1975)', 'label': 'Day Of Birth'}, 'MonthOfBirth': {'type': 'int', 'description': 'Month of birth date (e.g. 11 for a date of birth of 23/11/1975)', 'label': 'Month Of Birth'}, 'YearOfBirth': {'type': 'int', 'description': 'Year of birth date (e.g. 1975 for a date of birth of 23/11/1975)', 'label': 'Year Of Birth'}}, 'required': ['DayOfBirth', 'FirstGivenName', 'FirstSurName', 'MonthOfBirth', 'YearOfBirth']}, 'Location': {'title': 'Location', 'type': 'object', 'properties': {'BuildingNumber': {'type': 'string', 'description': 'Street number of primary residence', 'label': 'Street Number'}, 'UnitNumber': {'type': 'string', 'description': 'Flat/Unit/Apartment number of primary residence', 'label': 'Unit Number'}, 'StreetName': {'type': 'string', 'description': 'Street name of primary residence', 'label': 'Street Name'}, 'StreetType': {'type': 'string', 'description': 'Street type of primary residence (e.g. St, Rd, etc.)',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       'label': 'Street Type'}, 'Suburb': {'type': 'string', 'description': 'City or Suburb of primary residence', 'label': 'Suburb'}, 'StateProvinceCode': {'type': 'string', 'description': 'State of primary residence. US sources expect 2 characters. Australian sources expect 2 or 3 characters.', 'label': 'State'}, 'PostalCode': {'type': 'string', 'description': 'ZIP Code or Postal Code of primary residence', 'label': 'Postal Code'}}, 'required': ['PostalCode', 'StreetName']}, 'Communication': {'title': 'Communication', 'type': 'object', 'properties': {'MobileNumber': {'type': 'string', 'description': 'Cellular phone number', 'label': 'Cell Number'}, 'Telephone': {'type': 'string', 'description': 'Telephone number of the individual to be verified', 'label': 'Telephone'}}, 'required': []}, 'Passport': {'title': 'Passport', 'type': 'object', 'properties': {'Number': {'type': 'string', 'description': 'Passport number of the individual to be verified', 'label': 'Passport Number'}}, 'required': ['Number']}, 'CountrySpecific': {'title': 'CountrySpecific', 'type': 'object', 'properties': {'AU': {'title': 'AU', 'type': 'object', 'properties': {'PassportCountry': {'type': 'string', 'description': 'Passport Country (ISO 3166-1 alpha-2)', 'label': 'Passport Country'}, 'PassportNumber': {'type': 'string', 'description': 'Passport number of the individual to be verified', 'label': 'Passport Number'}}, 'required': ['PassportCountry', 'PassportNumber']}}}}])

    @patch("requests.get")
    def test_get_document_types(self, mock_requests):
        mock_response_json = {
            "DE": [
                "DrivingLicence",
                "IdentityCard",
                "Passport",
                "ResidencePermit"
            ]
        }
        response_obj = Response()
        response_obj.__setattr__("status_code", 200)
        response_obj.__setattr__("_content", json.dumps(
            mock_response_json).encode("utf-8"))
        mock_requests.return_value = response_obj

        country_code = "DE"

        reponse = VerificationService().get_document_types(country_code)

        assert(reponse == {
               "DE": ["DrivingLicence", "IdentityCard", "Passport", "ResidencePermit"]
               })
