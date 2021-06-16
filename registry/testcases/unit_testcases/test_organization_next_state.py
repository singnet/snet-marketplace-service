from unittest import TestCase
from unittest.mock import Mock

from common.exceptions import OperationNotAllowed
from registry.constants import OrganizationStatus, OrganizationActions
from registry.domain.models.organization import Organization


class TestOrganizationNext(TestCase):

    def test_changes_after_onboarding(self):
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.ONBOARDING.value))
        self.assertEqual(OrganizationStatus.ONBOARDING_APPROVED.value,
                         Organization.next_state(current_org, Mock(), OrganizationActions.DRAFT.value))

        self.assertEqual(OrganizationStatus.ONBOARDING_APPROVED.value,
                         Organization.next_state(current_org, Mock(), OrganizationActions.SUBMIT.value))

    def test_changes_after_rejected(self):
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.REJECTED.value))
        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.DRAFT.value)

        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.SUBMIT.value)

    def test_changes_after_onboarding_approved(self):
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.ONBOARDING_APPROVED.value))
        self.assertEqual(OrganizationStatus.ONBOARDING_APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.DRAFT.value))

        self.assertEqual(OrganizationStatus.ONBOARDING_APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.SUBMIT.value))

    def test_changes_after_approved(self):
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.APPROVED.value))
        self.assertEqual(OrganizationStatus.APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.DRAFT.value))

        self.assertEqual(OrganizationStatus.APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.SUBMIT.value))

    def test_changes_after_published(self):
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.PUBLISHED.value))
        self.assertEqual(OrganizationStatus.APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.DRAFT.value))

        self.assertEqual(OrganizationStatus.APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.SUBMIT.value))
