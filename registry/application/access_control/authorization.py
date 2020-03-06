from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository

org_repository = OrganizationPublisherRepository()


def pre_token_auth_handler(event, context):
    org_members = org_repository.get_org_member(username=event['request']['userAttributes']['email'])

    roles = {}
    for org_member in org_members:
        roles[org_member.org_uuid] = org_member.role

    event['response'] = {
        "claimsOverrideDetails": {
            "claimsToAddOrOverride": {
                "roles": roles
            }
        }
    }
    return event
