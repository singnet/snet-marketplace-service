from math import isclose

import pytest
import json
from datetime import datetime, UTC
from unittest.mock import patch
from http import HTTPStatus

from contract_api.application.handlers.service_handlers import get_service
from contract_api.domain.models.service_tag import NewServiceTagDomain
from contract_api.domain.models.service_media import NewServiceMediaDomain
from contract_api.domain.models.service_group import NewServiceGroupDomain
from contract_api.domain.models.org_group import NewOrgGroupDomain
from contract_api.application.handlers.service_handlers import get_services
from contract_api.constant import SortKeys, SortOrder, FilterKeys
from contract_api.domain.models.service_endpoint import NewServiceEndpointDomain


class TestGetService:
    """Tests for get_service handler."""
    
    def test_get_service_success(self, db_session, base_service, base_organization, service_repo):
        """Test successful service retrieval."""
        # Setup
        org_id = base_organization.org_id
        service_id = base_service.service_id
        
        # Add tags
        tag1 = NewServiceTagDomain(
            service_row_id=base_service.row_id,
            org_id=org_id,
            service_id=service_id,
            tag_name="ai"
        )
        tag2 = NewServiceTagDomain(
            service_row_id=base_service.row_id,
            org_id=org_id,
            service_id=service_id,
            tag_name="machine-learning"
        )
        service_repo.create_service_tag(db_session, tag1)
        service_repo.create_service_tag(db_session, tag2)
        
        # Add media
        hero_media = NewServiceMediaDomain(
            service_row_id=base_service.row_id,
            org_id=org_id,
            service_id=service_id,
            url="https://example.com/hero.jpg",
            order=1,
            file_type="image",
            asset_type="hero_image",
            alt_text="Hero image",
            hash_uri="ipfs://hero-hash"
        )
        gallery_media = NewServiceMediaDomain(
            service_row_id=base_service.row_id,
            org_id=org_id,
            service_id=service_id,
            url="https://example.com/gallery1.jpg",
            order=2,
            file_type="image", 
            asset_type="media_gallery",
            alt_text="Gallery image",
            hash_uri="ipfs://gallery-hash"
        )
        service_repo.upsert_service_media(db_session, hero_media)
        service_repo.upsert_service_media(db_session, gallery_media)
        
        db_session.commit()
        
        # Create Lambda event
        event = {
            "pathParameters": {
                "orgId": org_id,
                "serviceId": service_id
            }
        }
        
        # Execute
        response = get_service(event, context=None)
        
        # Assertions
        assert response["statusCode"] == HTTPStatus.OK
        
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert "data" in body
        
        data = body["data"]
        
        # Check main fields
        assert data["orgId"] == org_id
        assert data["serviceId"] == service_id
        assert data["displayName"] == "Test Service"
        assert data["description"] == "Test service description"
        assert data["shortDescription"] == "Short test description"
        assert data["organizationName"] == "Test Organization"
        
        # Check contacts
        assert "supportContacts" in data
        assert data["supportContacts"]["email"] == "support@test.com"
        assert data["supportContacts"]["phone"] == "+1234567890"
        
        # Check tags
        assert "tags" in data
        assert set(data["tags"]) == {"ai", "machine-learning"}
        
        # Check media
        assert "media" in data
        assert len(data["media"]) == 2
        media_by_type = {m["assetType"]: m for m in data["media"]}
        assert "hero_image" in media_by_type
        assert "media_gallery" in media_by_type
        assert media_by_type["hero_image"]["url"] == "https://example.com/hero.jpg"
        
        # Check groups and endpoints
        assert "groups" in data
        assert len(data["groups"]) == 1
        group = data["groups"][0]
        assert group["groupId"] == "default-group"
        assert group["groupName"] == "Default Group"
        assert "endpoints" in group
        assert len(group["endpoints"]) == 1
        endpoint = group["endpoints"][0]
        assert endpoint["endpoint"] == "https://test-service-endpoint.com:8080"
        assert endpoint["isAvailable"] is True
        
        # Check availability
        assert data["isAvailable"] is True
        
        # Check demo component
        assert "demoComponentRequired" in data
        assert data["demoComponentRequired"] is False
        
        # Check rating
        assert isclose(data["rating"], 0.0)
        assert data["numberOfRatings"] == 0
        
        # Check contributors
        assert "contributors" in data
        assert data["contributors"] == ["Test Developer"]
    
    def test_get_service_not_found(self):
        """Test getting non-existent service."""
        event = {
            "pathParameters": {
                "orgId": "non-existent-org",
                "serviceId": "non-existent-service"
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
        body = json.loads(response["body"])
        # Check that error contains information about service not found
        assert "Service not found" in str(body) or "not found" in str(body).lower()
    
    def test_get_service_uncurated(self, db_session, org_repo, service_repo, test_data_factory):
        """Test getting uncurated service (should return 400)."""
        # Create organization
        org_data = test_data_factory.create_organization_data(org_id="test-org-uncurated")
        org_repo.upsert_organization(db_session, org_data)
        db_session.commit()  # First save organization
        
        # Create group
        group_data = test_data_factory.create_org_group_data(org_data.org_id)
        org_repo.create_org_groups(db_session, [group_data])
        db_session.commit()  # Then save group

        # Create uncurated service
        service_data = test_data_factory.create_service_data(
            org_data.org_id, 
            service_id="uncurated-service",
            is_curated=False  # Uncurated
        )
        service = service_repo.upsert_service(db_session, service_data)
        
        metadata_data = test_data_factory.create_service_metadata_data(
            service.row_id, org_data.org_id, service_data.service_id
        )
        service_repo.upsert_service_metadata(db_session, metadata_data)
        
        db_session.commit()
        
        event = {
            "pathParameters": {
                "orgId": org_data.org_id,
                "serviceId": service_data.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
        body = json.loads(response["body"])
        assert "Service not found" in str(body) or "not found" in str(body).lower()
    
    def test_get_service_unavailable_endpoint(self, db_session, base_service, base_organization, service_repo, org_repo):
        """Test service with unavailable endpoint."""
        # Create unavailable endpoint

        
        # First create org group for the unavailable group
        unavailable_org_group = NewOrgGroupDomain(
            org_id=base_organization.org_id,
            group_id="unavailable-group",
            group_name="Unavailable Group",
            payment={
                "payment_address": "0xabcdef1234567890",
                "payment_expiration_threshold": 3600,
                "payment_channel_storage_type": "etcd"
            }
        )
        org_repo.create_org_groups(db_session, [unavailable_org_group])
        
        # Create service group
        unavailable_group = NewServiceGroupDomain(
            service_row_id=base_service.row_id,
            org_id=base_organization.org_id,
            service_id=base_service.service_id,
            group_id="unavailable-group",
            group_name="Unavailable Group",
            free_call_signer_address="0xabcdef1234567890",
            free_calls=0,
            pricing=[]
        )
        
        # Create unavailable endpoint
        unavailable_endpoint = NewServiceEndpointDomain(
            service_row_id=base_service.row_id,
            org_id=base_organization.org_id,
            service_id=base_service.service_id,
            group_id="unavailable-group",
            endpoint="https://unavailable-endpoint.com:8080",
            is_available=False,
            last_check_timestamp=datetime.now(UTC)
        )
        
        service_repo.upsert_service_group(db_session, unavailable_group)
        service_repo.upsert_service_endpoint(db_session, unavailable_endpoint)
        db_session.commit()
        
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        data = body["data"]
        
        # Should be 2 groups, but overall availability True due to base endpoint
        assert len(data["groups"]) == 2
        assert data["isAvailable"] is True  # At least one available endpoint exists
        
        # Check that unavailable endpoint is marked correctly
        unavailable_group_data = None
        for group in data["groups"]:
            if group["groupId"] == "unavailable-group":
                unavailable_group_data = group
                break
        
        assert unavailable_group_data is not None
        assert unavailable_group_data["endpoints"][0]["isAvailable"] is False
    
    def test_get_service_with_rating(self, db_session, base_service, base_organization, service_repo):
        """Test service with rating."""
        # Update rating through repository
        rating_data = {
            "rating": 4.5,
            "total_users_rated": 150
        }
        service_repo.update_service_rating(
            db_session, 
            base_organization.org_id, 
            base_service.service_id, 
            rating_data
        )
        db_session.commit()
        
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        data = body["data"]
        
        assert isclose(data["rating"], 4.5)
        assert data["numberOfRatings"] == 150
    
    def test_get_service_invalid_path_parameters(self):
        """Test with invalid path parameters."""
        # Test without orgId
        event = {
            "pathParameters": {
                "serviceId": "test-service"
            }
        }
        
        response = get_service(event, context=None)
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
        
        # Test without serviceId
        event = {
            "pathParameters": {
                "orgId": "test-org"
            }
        }
        
        response = get_service(event, context=None)
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
        
        # Test without pathParameters
        event = {}
        
        response = get_service(event, context=None)
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    
    def test_get_service_empty_values(self):
        """Test with empty parameter values."""
        event = {
            "pathParameters": {
                "orgId": "",
                "serviceId": ""
            }
        }
        
        response = get_service(event, context=None)
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    
    @patch('contract_api.application.services.service_service.ServiceService.get_service')
    def test_get_service_internal_error(self, mock_get_service, base_organization):
        """Test internal error handling."""
        mock_get_service.side_effect = Exception("Database error")
        
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": "test-service"
            }
        }
        
        response = get_service(event, context=None)
        assert response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    
    def test_get_service_cors_headers(self, base_service, base_organization):
        """Test CORS headers presence."""
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        assert "headers" in response
        # Check for CORS headers
        assert response["headers"]["Access-Control-Allow-Origin"] == "*"
        assert "Access-Control-Allow-Headers" in response["headers"]
    
    def test_get_service_multiple_media_types(self, db_session, base_service, base_organization, service_repo):
        """Test service with different media types."""
        media_items = [
            NewServiceMediaDomain(
                service_row_id=base_service.row_id,
                org_id=base_organization.org_id,
                service_id=base_service.service_id,
                url="https://example.com/hero.jpg",
                order=1,
                file_type="image",
                asset_type="hero_image",
                alt_text="Hero image",
                hash_uri="ipfs://hero-hash"
            ),
            NewServiceMediaDomain(
                service_row_id=base_service.row_id,
                org_id=base_organization.org_id,
                service_id=base_service.service_id,
                url="https://example.com/demo.mp4",
                order=2,
                file_type="video",
                asset_type="media_gallery",
                alt_text="Demo video",
                hash_uri="ipfs://video-hash"
            ),
            NewServiceMediaDomain(
                service_row_id=base_service.row_id,
                org_id=base_organization.org_id,
                service_id=base_service.service_id,
                url="https://example.com/proto-stub.py",
                order=3,
                file_type="grpc-stub",
                asset_type="grpc-stub/python",
                alt_text="Python stub",
                hash_uri=""
            )
        ]
        
        for media in media_items:
            service_repo.upsert_service_media(db_session, media)
        
        db_session.commit()
        
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        data = body["data"]
        
        assert len(data["media"]) == 3
        
        # Check that all media types are present
        asset_types = {m["assetType"] for m in data["media"]}
        expected_types = {"hero_image", "media_gallery", "grpc-stub/python"}
        assert asset_types == expected_types
    
    def test_get_service_without_tags(self, base_service, base_organization):
        """Test service without any tags."""
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        data = body["data"]
        
        # Service should have empty tags list
        assert "tags" in data
        assert data["tags"] == []
    
    def test_get_service_without_media(self, base_service, base_organization):
        """Test service without any media."""
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        data = body["data"]
        
        # Service should have empty media list
        assert "media" in data
        assert data["media"] == []
    
    def test_get_service_with_demo_component_config(self, db_session, base_service, base_organization, service_repo):
        """Test service with demo component configuration."""
        from contract_api.domain.models.offchain_service_attribute import NewOffchainServiceConfigDomain
        
        # Add demo component config
        demo_config = NewOffchainServiceConfigDomain(
            org_id=base_organization.org_id,
            service_id=base_service.service_id,
            parameter_name="demo_component_required",
            parameter_value="1"
        )
        
        service_repo.upsert_offchain_service_config(db_session, [demo_config])
        db_session.commit()
        
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        data = body["data"]
        
        # Demo component should be required
        assert data["demoComponentRequired"] is True
    
    def test_get_service_all_endpoints_unavailable(self, db_session, org_repo, service_repo, test_data_factory):
        """Test service where all endpoints are unavailable."""
        # Create new org and service
        org_data = test_data_factory.create_organization_data(org_id="test-org-no-endpoints")
        org_repo.upsert_organization(db_session, org_data)
        db_session.commit()
        
        group_data = test_data_factory.create_org_group_data(org_data.org_id)
        org_repo.create_org_groups(db_session, [group_data])
        db_session.commit()
        
        service_data = test_data_factory.create_service_data(org_data.org_id, service_id="no-available-endpoints")
        service = service_repo.upsert_service(db_session, service_data)
        
        metadata_data = test_data_factory.create_service_metadata_data(
            service.row_id, org_data.org_id, service_data.service_id
        )
        service_repo.upsert_service_metadata(db_session, metadata_data)
        
        # Create group and unavailable endpoint
        group = test_data_factory.create_service_group_data(
            service.row_id, org_data.org_id, service_data.service_id
        )
        service_repo.upsert_service_group(db_session, group)
        
        endpoint = test_data_factory.create_service_endpoint_data(
            service.row_id, org_data.org_id, service_data.service_id,
            is_available=False
        )
        service_repo.upsert_service_endpoint(db_session, endpoint)
        
        db_session.commit()
        
        event = {
            "pathParameters": {
                "orgId": org_data.org_id,
                "serviceId": service_data.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        data = body["data"]
        
        # Service should be marked as unavailable
        assert data["isAvailable"] is False
        

class TestGetServices:
    """Tests for get_services handler."""
    
    def test_get_services_basic(self, base_service):
        """Test basic get services without filters."""
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {},
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert "data" in body
        
        data = body["data"]
        assert "totalCount" in data
        assert "services" in data
        assert data["totalCount"] == 1
        assert len(data["services"]) == 1
        
        service = data["services"][0]
        assert service["orgId"] == base_service.org_id
        assert service["serviceId"] == base_service.service_id
        assert service["displayName"] == "Test Service"
        assert service["isAvailable"] is True
    
    def test_get_services_pagination(self, db_session, org_repo, service_repo, test_data_factory):
        """Test pagination functionality."""
        # Create multiple services
        org_data = test_data_factory.create_organization_data(org_id="test-org-pagination")
        org_repo.upsert_organization(db_session, org_data)
        db_session.commit()

        group_data = test_data_factory.create_org_group_data(org_data.org_id)
        org_repo.create_org_groups(db_session, [group_data])
        db_session.commit()
        
        # Create 5 services
        for i in range(5):
            service_data = test_data_factory.create_service_data(
                org_data.org_id, 
                service_id=f"service-{i}"
            )
            service = service_repo.upsert_service(db_session, service_data)
            
            metadata_data = test_data_factory.create_service_metadata_data(
                service.row_id, 
                org_data.org_id, 
                service_data.service_id,
                display_name=f"Service {i}"
            )
            service_repo.upsert_service_metadata(db_session, metadata_data)
            
            # Add group and endpoint
            group = test_data_factory.create_service_group_data(
                service.row_id, org_data.org_id, service_data.service_id
            )
            service_repo.upsert_service_group(db_session, group)
            
            endpoint = test_data_factory.create_service_endpoint_data(
                service.row_id, org_data.org_id, service_data.service_id
            )
            service_repo.upsert_service_endpoint(db_session, endpoint)
        
        db_session.commit()
        
        # Test first page
        event = {
            "body": json.dumps({
                "limit": 2,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {},
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]
        
        assert data["totalCount"] == 5  # 5 new + 1 from base_service
        assert len(data["services"]) == 2
        
        # Test second page
        event["body"] = json.dumps({
            "limit": 2,
            "page": 2,
            "sort": SortKeys.DISPLAY_NAME.value,
            "order": SortOrder.ASC.value,
            "filter": {},
            "q": ""
        })
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]
        
        assert len(data["services"]) == 2
    
    def test_get_services_sort_by_display_name(self, db_session, service_repo, test_data_factory, base_organization):
        """Test sorting by display name."""
        # Create services with different names
        services_names = ["Zebra Service", "Alpha Service", "Beta Service"]
        
        for i, name in enumerate(services_names):
            service_data = test_data_factory.create_service_data(
                base_organization.org_id, 
                service_id=f"service-sort-{i}"
            )
            service = service_repo.upsert_service(db_session, service_data)
            
            metadata_data = test_data_factory.create_service_metadata_data(
                service.row_id, 
                base_organization.org_id, 
                service_data.service_id,
                display_name=name
            )
            service_repo.upsert_service_metadata(db_session, metadata_data)
            
            # Add group and endpoint
            group = test_data_factory.create_service_group_data(
                service.row_id, base_organization.org_id, service_data.service_id
            )
            service_repo.upsert_service_group(db_session, group)
            
            endpoint = test_data_factory.create_service_endpoint_data(
                service.row_id, base_organization.org_id, service_data.service_id
            )
            service_repo.upsert_service_endpoint(db_session, endpoint)
        
        db_session.commit()
        
        # Test ASC order
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {},
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        services = body["data"]["services"]
        
        # Check ascending order
        display_names = [s["displayName"] for s in services]
        assert display_names == sorted(display_names)
        
        # Test DESC order
        event["body"] = json.dumps({
            "limit": 10,
            "page": 1,
            "sort": SortKeys.DISPLAY_NAME.value,
            "order": SortOrder.DESC.value,
            "filter": {},
            "q": ""
        })
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        services = body["data"]["services"]
        
        # Check descending order
        display_names = [s["displayName"] for s in services]
        assert display_names == sorted(display_names, reverse=True)
    
    def test_get_services_sort_by_rating(self, db_session, service_repo, test_data_factory, base_organization):
        """Test sorting by rating."""
        # Create services with different ratings
        ratings = [
            {"rating": 4.5, "total_users_rated": 100},
            {"rating": 3.0, "total_users_rated": 50},
            {"rating": 5.0, "total_users_rated": 200}
        ]
        
        for i, rating_data in enumerate(ratings):
            service_data = test_data_factory.create_service_data(
                base_organization.org_id, 
                service_id=f"service-rating-{i}"
            )
            service = service_repo.upsert_service(db_session, service_data)

            metadata_data = test_data_factory.create_service_metadata_data(
                service.row_id, 
                base_organization.org_id, 
                service_data.service_id,
                display_name=f"Service Rating {i}"
            )
            service_repo.upsert_service_metadata(db_session, metadata_data)
            
            group = test_data_factory.create_service_group_data(
                service.row_id, base_organization.org_id, service_data.service_id
            )
            service_repo.upsert_service_group(db_session, group)
            
            endpoint = test_data_factory.create_service_endpoint_data(
                service.row_id, base_organization.org_id, service_data.service_id
            )
            service_repo.upsert_service_endpoint(db_session, endpoint)
            # Update rating
            service_repo.update_service_rating(
                db_session, 
                base_organization.org_id, 
                service_data.service_id, 
                rating_data
            )
            
            # Add group and endpoint

        
        db_session.commit()
        
        # Test sorting by rating DESC
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.RATING.value,
                "order": SortOrder.DESC.value,
                "filter": {},
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        services = body["data"]["services"]
        
        # Check that services are sorted by rating in descending order
        ratings = [s["rating"] for s in services if s["rating"] > 0]
        assert ratings == sorted(ratings, reverse=True)
        assert isclose(ratings[0], 5.0)
    
    def test_get_services_filter_by_org_id(self, db_session, org_repo, service_repo, test_data_factory, base_service):
        """Test filtering by organization ID."""
        # Create another organization with services
        org2_data = test_data_factory.create_organization_data(org_id="test-org-2")
        org_repo.upsert_organization(db_session, org2_data)
        db_session.commit()

        group2_data = test_data_factory.create_org_group_data(org2_data.org_id)
        org_repo.create_org_groups(db_session, [group2_data])
        db_session.commit()
        
        service2_data = test_data_factory.create_service_data(org2_data.org_id, service_id="service-org2")
        service2 = service_repo.upsert_service(db_session, service2_data)
        
        metadata2_data = test_data_factory.create_service_metadata_data(
            service2.row_id, org2_data.org_id, service2_data.service_id
        )
        service_repo.upsert_service_metadata(db_session, metadata2_data)
        
        # Add group and endpoint for service2
        group = test_data_factory.create_service_group_data(
            service2.row_id, org2_data.org_id, service2_data.service_id
        )
        service_repo.upsert_service_group(db_session, group)
        
        endpoint = test_data_factory.create_service_endpoint_data(
            service2.row_id, org2_data.org_id, service2_data.service_id
        )
        service_repo.upsert_service_endpoint(db_session, endpoint)
        
        db_session.commit()
        
        # Filter by first org
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {
                    FilterKeys.ORG_ID.value: [base_service.org_id]
                },
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]
        
        assert data["totalCount"] == 1
        assert len(data["services"]) == 1
        assert data["services"][0]["orgId"] == base_service.org_id
        
        # Filter by both orgs
        event["body"] = json.dumps({
            "limit": 10,
            "page": 1,
            "sort": SortKeys.DISPLAY_NAME.value,
            "order": SortOrder.ASC.value,
            "filter": {
                FilterKeys.ORG_ID.value: [base_service.org_id, org2_data.org_id]
            },
            "q": ""
        })
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]
        
        assert data["totalCount"] == 2
        assert len(data["services"]) == 2
    
    def test_get_services_filter_by_tags(self, db_session, base_service, service_repo):
        """Test filtering by tags."""
        # Add tags to base service
        tag1 = NewServiceTagDomain(
            service_row_id=base_service.row_id,
            org_id=base_service.org_id,
            service_id=base_service.service_id,
            tag_name="ai"
        )
        tag2 = NewServiceTagDomain(
            service_row_id=base_service.row_id,
            org_id=base_service.org_id,
            service_id=base_service.service_id,
            tag_name="nlp"
        )
        service_repo.create_service_tag(db_session, tag1)
        service_repo.create_service_tag(db_session, tag2)
        
        db_session.commit()
        
        # Filter by one tag
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {
                    FilterKeys.TAG_NAME.value: ["ai"]
                },
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]
        
        assert data["totalCount"] == 1
        assert len(data["services"]) == 1
        
        # Filter by non-existent tag
        event["body"] = json.dumps({
            "limit": 10,
            "page": 1,
            "sort": SortKeys.DISPLAY_NAME.value,
            "order": SortOrder.ASC.value,
            "filter": {
                FilterKeys.TAG_NAME.value: ["blockchain"]
            },
            "q": ""
        })
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]
        
        assert data["totalCount"] == 0
        assert len(data["services"]) == 0
    
    def test_get_services_filter_only_available(self, db_session, org_repo, service_repo, test_data_factory, base_organization):
        """Test filtering only available services."""
        # Create service with unavailable endpoint
        service_data = test_data_factory.create_service_data(
            base_organization.org_id, 
            service_id="unavailable-service"
        )
        service = service_repo.upsert_service(db_session, service_data)
        db_session.commit()
        metadata_data = test_data_factory.create_service_metadata_data(
            service.row_id, 
            base_organization.org_id, 
            service_data.service_id,
            display_name="Unavailable Service"
        )
        service_repo.upsert_service_metadata(db_session, metadata_data)
        
        # Add group and unavailable endpoint
        group = test_data_factory.create_service_group_data(
            service.row_id, base_organization.org_id, service_data.service_id
        )
        service_repo.upsert_service_group(db_session, group)
        
        endpoint = test_data_factory.create_service_endpoint_data(
            service.row_id, 
            base_organization.org_id, 
            service_data.service_id,
            is_available=True
        )
        service_repo.upsert_service_endpoint(db_session, endpoint)
        
        db_session.commit()
        
        # Filter only available
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {
                    FilterKeys.ONLY_AVAILABLE.value: True
                },
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]

        # Should only return services with available endpoints
        assert data["totalCount"] == 1
        assert all(s["isAvailable"] for s in data["services"])
    
    def test_get_services_search_query(self, db_session, org_repo, service_repo, test_data_factory, base_organization):
        """Test search functionality."""
        # Create services with searchable content
        services_data = [
            ("neural-network", "Neural Network Service", "Deep learning neural networks"),
            ("image-recognition", "Image Recognition", "Computer vision and image analysis"),
            ("text-analysis", "Text Analysis", "Natural language processing")
        ]
        
        for service_id, display_name, description in services_data:
            service_data = test_data_factory.create_service_data(
                base_organization.org_id, 
                service_id=service_id
            )
            service = service_repo.upsert_service(db_session, service_data)
            
            metadata_data = test_data_factory.create_service_metadata_data(
                service.row_id, 
                base_organization.org_id, 
                service_data.service_id,
                display_name=display_name,
                short_description=description
            )
            service_repo.upsert_service_metadata(db_session, metadata_data)
            
            # Add group and endpoint
            group = test_data_factory.create_service_group_data(
                service.row_id, base_organization.org_id, service_data.service_id
            )
            service_repo.upsert_service_group(db_session, group)
            
            endpoint = test_data_factory.create_service_endpoint_data(
                service.row_id, base_organization.org_id, service_data.service_id
            )
            service_repo.upsert_service_endpoint(db_session, endpoint)
        
        db_session.commit()
        
        # Search by display name
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {},
                "q": "neural"
            })
        }
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]
        
        assert data["totalCount"] == 1
        assert "neural" in data["services"][0]["displayName"].lower()
        
        # Search by description
        event["body"] = json.dumps({
            "limit": 10,
            "page": 1,
            "sort": SortKeys.DISPLAY_NAME.value,
            "order": SortOrder.ASC.value,
            "filter": {},
            "q": "vision"
        })
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]
        
        assert data["totalCount"] == 1
        assert "vision" in data["services"][0]["shortDescription"].lower()
    
    def test_get_services_with_media(self, db_session, base_service, service_repo):
        """Test services with media (hero image)."""
        # Add hero image to base service
        hero_media = NewServiceMediaDomain(
            service_row_id=base_service.row_id,
            org_id=base_service.org_id,
            service_id=base_service.service_id,
            url="https://example.com/hero.jpg",
            order=1,
            file_type="image",
            asset_type="hero_image",
            alt_text="Hero image",
            hash_uri="ipfs://hero-hash"
        )
        service_repo.upsert_service_media(db_session, hero_media)
        
        db_session.commit()
        
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {},
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]
        
        assert len(data["services"]) == 1
        service = data["services"][0]
        assert "serviceImageUrl" in service
        assert service["serviceImageUrl"] == "https://example.com/hero.jpg"
    
    def test_get_services_invalid_sort_key(self):
        """Test with invalid sort key."""
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": "invalidSort",
                "order": SortOrder.ASC.value,
                "filter": {},
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
        body = json.loads(response["body"])
        assert "Invalid sort parameter" in str(body)
    
    def test_get_services_invalid_order(self):
        """Test with invalid order."""
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": "invalidOrder",
                "filter": {},
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
        body = json.loads(response["body"])
        assert "Invalid order parameter" in str(body)
    
    def test_get_services_invalid_filter_key(self):
        """Test with invalid filter key."""
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {
                    "invalidFilter": ["value"]
                },
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
        body = json.loads(response["body"])
        assert "Invalid filter parameter" in str(body)
    
    def test_get_services_empty_result(self):
        """Test when no services match criteria."""
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {},
                "q": "nonexistentservice123456"
            })
        }
        
        response = get_services(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        data = body["data"]
        
        assert data["totalCount"] == 0
        assert len(data["services"]) == 0
    
    def test_get_services_uncurated_excluded(self, db_session, org_repo, service_repo, test_data_factory, base_organization, base_service):
        """Test that uncurated services are excluded."""
        # Create uncurated service
        service_data = test_data_factory.create_service_data(
            base_organization.org_id, 
            service_id="uncurated-service",
            is_curated=False
        )
        service = service_repo.upsert_service(db_session, service_data)
        
        metadata_data = test_data_factory.create_service_metadata_data(
            service.row_id, 
            base_organization.org_id, 
            service_data.service_id
        )
        service_repo.upsert_service_metadata(db_session, metadata_data)
        
        db_session.commit()
        
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {},
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        body = json.loads(response["body"])
        data = body["data"]
        
        # Should only return curated services
        assert data["totalCount"] == 1  # Only base_service
        assert all(s["serviceId"] != "uncurated-service" for s in data["services"])
    
    def test_get_services_invalid_body(self):
        """Test with invalid request body."""
        event = {
            "body": "invalid json"
        }
        
        response = get_services(event, context=None)
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    
    def test_get_services_missing_required_fields(self):
        """Test with missing required fields."""
        event = {
            "body": json.dumps({
                "limit": 10,
                # Missing page, sort, order
            })
        }
        
        response = get_services(event, context=None)
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    
    @patch('contract_api.application.services.service_service.ServiceService.get_services')
    def test_get_services_internal_error(self, mock_get_services):
        """Test internal error handling."""
        mock_get_services.side_effect = Exception("Database error")
        
        event = {
            "body": json.dumps({
                "limit": 10,
                "page": 1,
                "sort": SortKeys.DISPLAY_NAME.value,
                "order": SortOrder.ASC.value,
                "filter": {},
                "q": ""
            })
        }
        
        response = get_services(event, context=None)
        assert response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR