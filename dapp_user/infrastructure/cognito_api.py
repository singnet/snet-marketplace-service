import json
from typing import Dict, List

import boto3
from dapp_user.constant import CognitoAttributes
from dapp_user.domain.interfaces.user_identity_manager_interface import UserIdentityManager
from dapp_user.domain.models.user import NewUser
from dapp_user.settings import settings


class CognitoUserManager(UserIdentityManager):
    def __init__(self, user_pool_id: str):
        self.client = boto3.client("cognito-idp", region_name=settings.aws.region_name)
        self.user_pool_id = user_pool_id

    def get_all_users(self) -> List[NewUser]:
        users: List[NewUser] = []
        pagination_token = None

        while True:
            params = {
                "UserPoolId": self.user_pool_id,
                "Limit": 60,
            }
            if pagination_token:
                params["PaginationToken"] = pagination_token

            response = self.client.list_users(**params)

            for user in response["Users"]:
                attr_map: Dict[str, str] = {
                    attr["Name"]: attr["Value"] for attr in user.get("Attributes", [])
                }

                new_user = NewUser(
                    account_id=attr_map["sub"],
                    username=attr_map["email"],
                    name=attr_map["nickname"],
                    email=attr_map["email"],
                    email_verified=True,
                    email_alerts=True,
                    status=True,
                    is_terms_accepted=self._parse_terms_accepted(
                        attr_map.get(CognitoAttributes.TNC)
                    ),
                )
                users.append(new_user)

            pagination_token = response.get("PaginationToken")
            if not pagination_token:
                break

        return users

    def _parse_terms_accepted(self, json_str: str | None) -> bool:
        if not json_str:
            return False
        try:
            obj = json.loads(json_str)
            return obj.get("accepted", False) is True
        except Exception:
            return False
