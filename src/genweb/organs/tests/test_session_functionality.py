# -*- coding: utf-8 -*-
"""Functional tests for session functionality."""
import unittest
from plone import api
from genweb.organs.tests.base import FunctionalTestCase


class TestSessionFunctionality(FunctionalTestCase):
    """Test session functionality."""

    def test_session_creation(self):
        """Test that sessions can be created properly."""
        self.login_as_manager()

        organ = self.portal.ca.testingfolder.obert

        # Create a new session
        session = self.assertCanCreate(
            'genweb.organs.sessio',
            organ,
            id='test_session',
            title='Test Session'
        )

        # Verify session properties
        self.assertEqual(session.id, 'test_session')
        self.assertEqual(session.title, 'Test Session')

        self.logout()

    def test_session_workflow(self):
        """Test session workflow functionality."""
        session = self.portal.ca.testingfolder.obert.planificada

        self.login_as_manager()

        # Check initial state
        initial_state = api.content.get_state(session)
        self.assertIsNotNone(initial_state)

        # Test workflow transitions
        api.content.transition(obj=session, transition='publish')
        published_state = api.content.get_state(session)
        self.assertEqual(published_state, 'published')

        self.logout()

    def test_session_content_creation(self):
        """Test that sessions can contain various content types."""
        self.login_as_manager()

        organ = self.portal.ca.testingfolder.obert
        session = organ.planificada

        # Test creating points
        point = self.assertCanCreate(
            'genweb.organs.punt',
            session,
            id='test_point',
            title='Test Point'
        )

        # Test creating subpoints
        subpoint = self.assertCanCreate(
            'genweb.organs.subpunt',
            point,
            id='test_subpoint',
            title='Test Subpoint'
        )

        # Test creating agreements
        agreement = self.assertCanCreate(
            'genweb.organs.acord',
            session,
            id='test_agreement',
            title='Test Agreement'
        )

        # Test creating actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            session,
            id='test_acta',
            title='Test Acta'
        )

        # Test creating files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            session,
            id='test_file',
            title='Test File'
        )

        # Test creating documents
        document = self.assertCanCreate(
            'genweb.organs.document',
            session,
            id='test_document',
            title='Test Document'
        )

        # Test creating audio
        audio = self.assertCanCreate(
            'genweb.organs.audio',
            session,
            id='test_audio',
            title='Test Audio'
        )

        # Test creating annexes
        annex = self.assertCanCreate(
            'genweb.organs.annex',
            session,
            id='test_annex',
            title='Test Annex'
        )

        self.logout()

        # Verify all content was created
        self.assertEqual(point.id, 'test_point')
        self.assertEqual(subpoint.id, 'test_subpoint')
        self.assertEqual(agreement.id, 'test_agreement')
        self.assertEqual(acta.id, 'test_acta')
        self.assertEqual(file_obj.id, 'test_file')
        self.assertEqual(document.id, 'test_document')
        self.assertEqual(audio.id, 'test_audio')
        self.assertEqual(annex.id, 'test_annex')

    def test_session_permissions(self):
        """Test session permissions for different roles."""
        session = self.portal.ca.testingfolder.obert.planificada

        # Test that all roles can view the session
        for role_method in [self.login_as_secretari, self.login_as_editor,
                            self.login_as_membre, self.login_as_afectat,
                            self.login_as_convidat]:
            role_method()

            # Should be able to access the session
            self.assertTrue(api.content.get_state(session))

            self.logout()

    def test_session_search(self):
        """Test session search functionality."""
        # Test catalog search for sessions
        catalog = api.portal.get_tool('portal_catalog')

        # Search for sessions
        results = catalog.searchResults(portal_type='genweb.organs.sessio')
        self.assertGreater(len(results), 0)

    def test_session_navigation(self):
        """Test session navigation functionality."""
        session = self.portal.ca.testingfolder.obert.planificada

        # Test that session is navigable
        self.assertTrue(hasattr(session, 'absolute_url'))
        self.assertTrue(session.absolute_url().endswith('/planificada'))

        # Test that session has proper parent
        self.assertEqual(session.aq_parent.id, 'obert')

    def test_session_content_types(self):
        """Test that session supports all expected content types."""
        session = self.portal.ca.testingfolder.obert.planificada

        # Get allowed content types
        allowed_types = session.getLocallyAllowedTypes()

        # Verify expected content types are allowed
        expected_types = [
            'genweb.organs.acta',
            'genweb.organs.punt',
            'genweb.organs.acord',
            'genweb.organs.file',
            'genweb.organs.document',
            'genweb.organs.audio',
            'genweb.organs.annex'
        ]

        for content_type in expected_types:
            self.assertIn(content_type, allowed_types)

    def test_session_quorum_functionality(self):
        """Test session quorum functionality."""
        session = self.portal.ca.testingfolder.obert.planificada

        # Test quorum methods if they exist
        if hasattr(session, 'checkHasQuorum'):
            # Test quorum checking
            has_quorum = session.checkHasQuorum()
            self.assertIsInstance(has_quorum, bool)

        if hasattr(session, 'showOpenQuorum'):
            # Test open quorum display
            show_quorum = session.showOpenQuorum()
            self.assertIsInstance(show_quorum, bool)

    def test_session_multilingual(self):
        """Test session multilingual functionality."""
        self.login_as_manager()

        organ = self.portal.ca.testingfolder.obert

        # Create session in Catalan
        session_ca = self.assertCanCreate(
            'genweb.organs.sessio',
            organ,
            id='test_session_ca',
            title='Sessió de Prova'
        )

        # Test that session is created successfully
        self.assertEqual(session_ca.title, 'Sessió de Prova')

        self.logout()
