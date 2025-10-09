# -*- coding: utf-8 -*-
"""Functional tests for organs functionality."""
import unittest
from plone import api
from genweb.organs.tests.base import FunctionalTestCase


class TestOrgansFunctionality(FunctionalTestCase):
    """Test basic organs functionality."""

    def test_organ_creation(self):
        """Test that organs can be created properly."""
        self.login_as_manager()

        # Create a new organ
        organ = self.assertCanCreate(
            'genweb.organs.organgovern',
            self.portal.ca.testingfolder,
            id='test_organ',
            title='Test Organ'
        )

        # Verify organ properties
        self.assertEqual(organ.id, 'test_organ')
        self.assertEqual(organ.title, 'Test Organ')

        self.logout()

    def test_organ_folder_creation(self):
        """Test that organ folders can be created properly."""
        self.login_as_manager()

        # Create a new organ folder
        organ_folder = self.assertCanCreate(
            'genweb.organs.organsfolder',
            self.portal.ca,
            id='test_organ_folder',
            title='Test Organ Folder'
        )

        # Verify organ folder properties
        self.assertEqual(organ_folder.id, 'test_organ_folder')
        self.assertEqual(organ_folder.title, 'Test Organ Folder')

        self.logout()

    def test_organ_content_structure(self):
        """Test that organ content structure is created properly."""
        organ = self.portal.ca.testingfolder.obert

        # Verify organ has the expected structure
        self.assertTrue(hasattr(organ, 'planificada'))
        self.assertEqual(organ.planificada.portal_type, 'genweb.organs.sessio')

        # Verify session has points
        session = organ.planificada
        self.assertTrue(hasattr(session, 'punt'))
        self.assertEqual(session.punt.portal_type, 'genweb.organs.punt')

    def test_organ_workflow(self):
        """Test organ workflow functionality."""
        organ = self.portal.ca.testingfolder.obert

        # Test workflow states
        self.login_as_manager()

        # Check initial state
        initial_state = api.content.get_state(organ)
        self.assertIsNotNone(initial_state)

        # Test publishing
        api.content.transition(obj=organ, transition='publish')
        published_state = api.content.get_state(organ)
        self.assertEqual(published_state, 'published')

        self.logout()

    def test_organ_permissions(self):
        """Test organ permissions for different roles."""
        organ = self.portal.ca.testingfolder.obert

        # Test that all roles can view the organ
        for role_method in [self.login_as_secretari, self.login_as_editor,
                            self.login_as_membre, self.login_as_afectat,
                            self.login_as_convidat]:
            role_method()

            # Should be able to access the organ
            self.assertTrue(api.content.get_state(organ))

            self.logout()

    def test_organ_search(self):
        """Test organ search functionality."""
        # Test catalog search for organs
        catalog = api.portal.get_tool('portal_catalog')

        # Search for organs
        results = catalog.searchResults(portal_type='genweb.organs.organgovern')
        self.assertGreater(len(results), 0)

        # Search for organ folders
        results = catalog.searchResults(portal_type='genweb.organs.organsfolder')
        self.assertGreater(len(results), 0)

    def test_organ_navigation(self):
        """Test organ navigation functionality."""
        organ = self.portal.ca.testingfolder.obert

        # Test that organ is navigable
        self.assertTrue(hasattr(organ, 'absolute_url'))
        self.assertTrue(organ.absolute_url().endswith('/obert'))

        # Test that organ has proper parent
        self.assertEqual(organ.aq_parent.id, 'testingfolder')

    def test_organ_content_types(self):
        """Test that organ supports all expected content types."""
        organ = self.portal.ca.testingfolder.obert

        # Get allowed content types
        allowed_types = organ.getLocallyAllowedTypes()

        # Verify expected content types are allowed
        expected_types = [
            'genweb.organs.sessio',
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

    def test_organ_multilingual(self):
        """Test organ multilingual functionality."""
        # Test that organs work with multilingual setup
        self.login_as_manager()

        # Create organ in Catalan
        organ_ca = self.assertCanCreate(
            'genweb.organs.organgovern',
            self.portal.ca.testingfolder,
            id='test_organ_ca',
            title='Organ de Prova'
        )

        # Test that organ is created successfully
        self.assertEqual(organ_ca.title, 'Organ de Prova')

        self.logout()
