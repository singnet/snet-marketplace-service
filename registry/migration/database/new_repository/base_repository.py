from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from registry.migration.config import NEW_DB
from registry.migration.database.new_repository.models import Organization, OrganizationMember, OrganizationState, \
    Group, Service, \
    ServiceState, ServiceGroup

engine = create_engine(
    f"{NEW_DB['DB_DRIVER']}://{NEW_DB['DB_USER']}:"
    f"{NEW_DB['DB_PASSWORD']}"
    f"@{NEW_DB['DB_HOST']}:"
    f"{NEW_DB['DB_PORT']}/{NEW_DB['DB_NAME']}", echo=False)

Session = sessionmaker(bind=engine)
default_session = Session()


class BaseRepository:

    def __init__(self):
        self.session = default_session

    def add_item(self, item):
        try:
            self.session.add(item)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def add_all_items(self, items):
        try:
            self.session.add_all(items)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_all_org_id(self):
        organization = self.session.query(Organization.org_id, Organization.uuid).all()
        return [org.org_id for org in organization]

    def add_all_organization(self, organization_list, state):
        current_time = datetime.utcnow()
        org_member = []
        organization_db_list = []
        for organization in organization_list:
            org_member.extend(
                [OrganizationMember(
                    invite_code=member.invite_code, org_uuid=member.org_uuid, role=member.role,
                    username=member.username, address=member.address, status=member.status,
                    transaction_hash=member.transaction_hash, invited_on=member.invited_on,
                    created_on=member.created_on, updated_on=member.updated_on
                ) for member in organization.members]
            )
            group_db = [
                Group(name=group.name, id=group.group_id, org_uuid=group.org_uuid,
                      payment_address=group.payment_address, payment_config=group.payment_config, status=group.status)
                for group in organization.groups
            ]
            org_state = [
                OrganizationState(
                    org_uuid=organization.uuid, state=state, transaction_hash="",
                    wallet_address="", created_by="", created_on=current_time,
                    updated_by="", updated_on=current_time, reviewed_by="")]

            organization_db_list.append(Organization(
                uuid=organization.uuid, name=organization.name, org_id=organization.id,
                org_type=organization.org_type, origin=organization.origin, description=organization.description,
                short_description=organization.short_description, url=organization.url,
                duns_no=organization.duns_no, contacts=organization.contacts, assets=organization.assets,
                metadata_uri=organization.metadata_uri, org_state=org_state, groups=group_db
            ))
        self.session.add_all(organization_db_list)
        self.session.flush()
        self.session.add_all(org_member)
        self.session.flush()

    def get_all_group_ids(self):
        groups = self.session.query(Group.id).all()
        return [group[0] for group in groups]

    def add_all_service(self, services, state):
        current_time = datetime.utcnow()
        services_db = []
        for service in services:
            service_state_db = ServiceState(
                org_uuid=service.org_uuid, service_uuid=service.uuid, state=state, transaction_hash="",
                test_transaction_hash="", created_by="", updated_by="", approved_by="", created_on=current_time,
                updated_on=current_time)
            groups = service.groups
            group_db = [
                ServiceGroup(
                    org_uuid=group.org_uuid, service_uuid=group.service_uuid, group_id=group.group_id,
                    group_name=group.group_name, pricing=group.pricing, endpoints=group.endpoints,
                    test_endpoints=group.test_endpoints, daemon_address=group.daemon_address,
                    free_calls=group.free_calls,
                    free_call_signer_address=group.free_call_signer_address, created_on=current_time,
                    updated_on=current_time
                ) for group in groups]
            services_db.append(
                Service(
                    org_uuid=service.org_uuid, uuid=service.uuid, display_name=service.display_name,
                    service_id=service.service_id, metadata_uri=service.metadata_uri, proto=service.proto,
                    short_description=service.short_description, description=service.description,
                    project_url=service.project_url, assets=service.assets, rating=service.rating,
                    ranking=service.ranking,
                    contributors=service.contributors, tags=service.tags, mpe_address=service.mpe_address,
                    created_on=current_time, updated_on=current_time, groups=group_db, service_state=service_state_db
                )
            )
        self.session.add_all(services_db)
        self.session.flush()

    def add_org_service(self, organizations, org_state, services, service_state):
        try:
            self.add_all_organization(organizations, org_state)
            self.add_all_service(services, service_state)
            self.session.commit()
        except:
            self.session.rollback()
            raise
