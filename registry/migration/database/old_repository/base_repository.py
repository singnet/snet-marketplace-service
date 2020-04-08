from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from registry.migration.config import OLD_DB
from registry.migration.database.old_repository.models import Organization, Group, Service, ServiceMetadata, \
    ServiceTags, ServiceGroup, \
    ServiceEndpoints
from registry.migration.mapper import OrganizationMapper, ServiceMapper

engine = create_engine(
    f"{OLD_DB['DB_DRIVER']}://{OLD_DB['DB_USER']}:"
    f"{OLD_DB['DB_PASSWORD']}"
    f"@{OLD_DB['DB_HOST']}:"
    f"{OLD_DB['DB_PORT']}/{OLD_DB['DB_NAME']}", echo=False)

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

    def get_all_org(self):
        organization_db = self.session.query(Organization).all()
        organization = OrganizationMapper.org_list_from_old_org(organization_db)
        self.session.commit()
        return organization

    def get_groups(self, org_id):
        group_db = self.session.query(Group).filter(Group.org_id == org_id).all()
        group = OrganizationMapper.groups_from_old_group_list(group_db)
        self.session.commit()
        return group

    def get_all_service(self):
        service_db = self.session.query(Service, ServiceMetadata) \
            .join(ServiceMetadata, Service.row_id == ServiceMetadata.service_row_id).all()
        service = ServiceMapper.service_from_old_service_list(service_db)
        self.session.commit()
        return service

    def get_tags(self, service_id, org_id):
        tags_db = self.session.query(ServiceTags.tag_name).filter(ServiceTags.org_id == org_id) \
            .filter(ServiceTags.service_id == service_id).all()
        tags = [tag.tag_name for tag in tags_db]
        self.session.commit()
        return tags

    def get_service_groups(self, service_id, org_id):
        service_group_db = self.session.query(ServiceGroup).filter(ServiceGroup.org_id == org_id) \
            .filter(ServiceGroup.service_id == service_id).all()
        service_group = ServiceMapper.group_from_old_group_list(service_group_db)
        self.session.commit()
        return service_group

    def get_endpoints(self, org_id, service_id, group_id):
        endpoints_db = self.session.query(ServiceEndpoints)\
            .filter(ServiceEndpoints.org_id == org_id)\
            .filter(ServiceEndpoints.service_id == service_id)\
            .filter(ServiceEndpoints.group_id == group_id)\
            .all()
        endpoints = [endpoint.endpoint for endpoint in endpoints_db]
        self.session.commit()
        return endpoints
