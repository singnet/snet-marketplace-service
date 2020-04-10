from registry.migration.database.new_repository.base_repository import BaseRepository as RegistryRepository
from registry.migration.database.old_repository.base_repository import BaseRepository as ContractRegistry

registry_repo = RegistryRepository()
contract_repo = ContractRegistry()

delta_org_id_uuid_mapping = {}
delta_orgs = []
delta_service = []
failed_service = []


def org_migrate():
    contract_organization = contract_repo.get_all_org()
    registry_org_id = registry_repo.get_all_org_id()
    for org in contract_organization:
        if org.id not in registry_org_id:
            groups = contract_repo.get_groups(org.id)
            for group in groups:
                group.org_uuid = org.uuid
            delta_org_id_uuid_mapping[org.id] = org.uuid
            org.groups = groups
            delta_orgs.append(org)


def migrate_service():
    contract_service = contract_repo.get_all_service()
    for service in contract_service:
        org_id = service.org_id
        service_id = service.service_id
        if service.org_id not in delta_org_id_uuid_mapping:
            failed_service.append(service)
            continue
        org_uuid = delta_org_id_uuid_mapping[service.org_id]
        service_uuid = service.uuid
        service.org_uuid = org_uuid
        service.tags = contract_repo.get_tags(service_id, org_id)
        groups = contract_repo.get_service_groups(service_id, org_id)
        for group in groups:
            group.org_uuid = org_uuid
            group.service_uuid = service_uuid
            group_id = group.group_id
            group.endpoints = contract_repo.get_endpoints(org_id, service_id, group_id)
        service.groups = groups
        delta_service.append(service)



org_migrate()
migrate_service()
registry_repo.add_org_service(delta_orgs, "PUBLISHED_UNAPPROVED", delta_service, "PUBLISHED_UNAPPROVED")
