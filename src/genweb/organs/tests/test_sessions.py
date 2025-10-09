# -*- coding: utf-8 -*-
"""Functional tests for session creation and management."""
from plone import api
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login, logout, setRoles
from plone.api.env import adopt_roles
from AccessControl import Unauthorized
from genweb.organs.tests.base import FunctionalTestCase


class TestSessionCreation(FunctionalTestCase):
    """Test session creation permissions for different organ types."""

    def test_create_sessions_in_all_organs(self):
        """Test users who can create sessions in all organ types."""
        # Get the testing folder from the default language folder
        # or portal root
        container = getattr(self, 'default_lang_folder', self.portal)
        root_obert = container.testingfolder.obert
        root_membres = container.testingfolder.membres
        root_afectats = container.testingfolder.afectats

        # Test open organ (obert)
        self._test_organ_permissions(root_obert, "ORGAN OBERT")

        # Test members organ (membres)
        self._test_organ_permissions(
            root_membres, "ORGAN RESTRINGIT MEMBRES")

        # Test affected organ (afectats)
        self._test_organ_permissions(
            root_afectats, "ORGAN RESTRINGIT AFECTATS")

    def _test_organ_permissions(self, organ_container, organ_name):
        """Test permissions for a specific organ type."""
        # Assign local roles to test user on the organ
        organ_container.manage_setLocalRoles(TEST_USER_ID,
                                             ['OG1-Secretari', 'OG2-Editor'])
        organ_container.reindexObjectSecurity()

        # Test Secretari role (OG1-Secretari) - should work
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(api.content.create(
            type='genweb.organs.sessio',
            id='session1',
            title='Session1',
            container=organ_container))
        print(f"\n    {organ_name} [Secretari] - Add Session - True")
        logout()

        # Test Editor role (OG2-Editor) - should work
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(api.content.create(
            type='genweb.organs.sessio',
            id='session2',
            title='Session2',
            container=organ_container))
        print(f"    {organ_name} [Editor]    - Add Session - True")
        logout()

        # Test Membre role (OG3-Membre) - should fail
        with self.assertRaises(Unauthorized):
            with adopt_roles('OG3-Membre'):
                api.content.create(
                    type='genweb.organs.sessio',
                    id='session3',
                    title='Session3',
                    container=organ_container)
        print(f"    {organ_name} [Membre]    - Add Session - Unauthorized")
        logout()

        # Test Afectat role (OG4-Afectat) - should fail
        with self.assertRaises(Unauthorized):
            with adopt_roles('OG4-Afectat'):
                api.content.create(
                    type='genweb.organs.sessio',
                    id='session4',
                    title='Session4',
                    container=organ_container)
        print(f"    {organ_name} [Afectat]   - Add Session - Unauthorized")
        logout()

        # Test Convidat role (OG5-Convidat) - should fail
        with self.assertRaises(Unauthorized):
            with adopt_roles('OG5-Convidat'):
                api.content.create(
                    type='genweb.organs.sessio',
                    id='session5',
                    title='Session5',
                    container=organ_container)
        print(f"    {organ_name} [Convidat]   - Add Session - Unauthorized")
        logout()

        # Test Anonymous role - should fail
        with self.assertRaises(Unauthorized):
            with adopt_roles('Anonim'):
                api.content.create(
                    type='genweb.organs.sessio',
                    id='session6',
                    title='Session6',
                    container=organ_container)
        print(f"    {organ_name} [Anonim]    - Add Session - Unauthorized")

    def test_session_content_creation(self):
        """Test that sessions can have content created inside them."""
        # Get the testing folder from the default language folder
        # or portal root
        container = getattr(self, 'default_lang_folder', self.portal)
        root_obert = container.testingfolder.obert

        # Create a session as manager
        logout()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        session = api.content.create(
            type='genweb.organs.sessio',
            id='test_session',
            title='Test Session',
            container=root_obert
        )
        self.assertIsNotNone(session)

        # Test creating points in the session
        point = api.content.create(
            type='genweb.organs.punt',
            id='test_point',
            title='Test Point',
            container=session
        )
        self.assertIsNotNone(point)

        # Test creating subpoints
        subpoint = api.content.create(
            type='genweb.organs.subpunt',
            id='test_subpoint',
            title='Test Subpoint',
            container=point
        )
        self.assertIsNotNone(subpoint)

        # Test creating agreements
        agreement = api.content.create(
            type='genweb.organs.acord',
            id='test_agreement',
            title='Test Agreement',
            container=session
        )
        self.assertIsNotNone(agreement)

        logout()

        # Verify content was created
        self.assertEqual(session.id, 'test_session')
        self.assertEqual(point.id, 'test_point')
        self.assertEqual(subpoint.id, 'test_subpoint')
        self.assertEqual(agreement.id, 'test_agreement')
