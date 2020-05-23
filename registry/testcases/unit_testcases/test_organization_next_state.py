from unittest import TestCase
from unittest.mock import Mock

from common.exceptions import OperationNotAllowed
from registry.constants import OrganizationStatus, OrganizationActions
from registry.domain.models.organization import Organization


class TestOrganizationNext(TestCase):

    def test_changes_after_onboarding(self):
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.ONBOARDING.value))
        self.assertEqual(OrganizationStatus.ONBOARDING.value,
                         Organization.next_state(current_org, Mock(), OrganizationActions.DRAFT.value))

        self.assertEqual(OrganizationStatus.ONBOARDING.value,
                         Organization.next_state(current_org, Mock(), OrganizationActions.SUBMIT.value))

    def test_changes_after_rejected(self):
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.REJECTED.value))
        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.DRAFT.value)

        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.SUBMIT.value)

        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.ONBOARDING_REJECTED.value))
        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.DRAFT.value)

        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.SUBMIT.value)

    def test_changes_after_onboarding_approved(self):
        """ Non Major changes """
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.ONBOARDING_APPROVED.value),
                           is_major_change=Mock(return_value=(False, None)))
        self.assertEqual(OrganizationStatus.ONBOARDING_APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.DRAFT.value))

        self.assertEqual(OrganizationStatus.ONBOARDING_APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.SUBMIT.value))

        """ Major changes """
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.ONBOARDING_APPROVED.value),
                           is_major_change=Mock(return_value=(True, {})))
        self.assertEqual(OrganizationStatus.ONBOARDING_APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.DRAFT.value))

        self.assertEqual(OrganizationStatus.ONBOARDING_APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.SUBMIT.value))

        """ Major changes with org_id """
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.ONBOARDING_APPROVED.value),
                           is_major_change=Mock(return_value=(True, {"values_changed": {"root._Organization__id"}})))
        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.DRAFT.value)

        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.SUBMIT.value)

    def test_changes_after_approved(self):
        """ Non Major changes """
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.APPROVED.value),
                           is_major_change=Mock(return_value=(False, None)))
        self.assertEqual(OrganizationStatus.APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.DRAFT.value))

        self.assertEqual(OrganizationStatus.APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.SUBMIT.value))

        """ Major changes """
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.APPROVED.value),
                           is_major_change=Mock(return_value=(True, {})))
        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.DRAFT.value)

        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.SUBMIT.value)

    def test_changes_after_published(self):
        """ Non Major changes """
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.PUBLISHED.value),
                           is_major_change=Mock(return_value=(False, None)))
        self.assertEqual(OrganizationStatus.APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.DRAFT.value))

        self.assertEqual(OrganizationStatus.APPROVED.value, Organization.next_state(
            current_org, Mock(), OrganizationActions.SUBMIT.value))

        """ Major changes """
        current_org = Mock(get_status=Mock(return_value=OrganizationStatus.PUBLISHED.value),
                           is_major_change=Mock(return_value=(True, {})))
        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.DRAFT.value)

        self.assertRaises(OperationNotAllowed, Organization.next_state,
                          current_org, Mock(), OrganizationActions.SUBMIT.value)
