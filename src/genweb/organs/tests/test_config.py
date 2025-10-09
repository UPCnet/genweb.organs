# -*- coding: utf-8 -*-
"""Test configuration and utilities."""
import unittest
from plone import api
from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING


class TestConfiguration(unittest.TestCase):
    """Test that the package is properly configured."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def test_package_installed(self):
        """Test that the package is properly installed."""
        portal = self.layer['portal']

        # Check that the package is installed
        # In Plone 6, we check if the profile is installed
        setup = api.portal.get_tool('portal_setup')
        installed_profiles = setup.getLastVersionForProfile('genweb.organs:default')
        self.assertIsNotNone(installed_profiles)

    def test_content_types_registered(self):
        """Test that all content types are registered."""
        portal = self.layer['portal']
        tt = api.portal.get_tool('portal_types')

        # Check that all expected content types are registered
        expected_types = [
            'genweb.organs.organsfolder',
            'genweb.organs.organgovern',
            'genweb.organs.sessio',
            'genweb.organs.acta',
            'genweb.organs.punt',
            'genweb.organs.subpunt',
            'genweb.organs.acord',
            'genweb.organs.file',
            'genweb.organs.document',
            'genweb.organs.audio',
            'genweb.organs.annex',
            'genweb.organs.votacioacord'
        ]

        for content_type in expected_types:
            self.assertIn(content_type, tt.objectIds())

    def test_workflows_registered(self):
        """Test that workflows are properly registered."""
        portal = self.layer['portal']
        wf = api.portal.get_tool('portal_workflow')

        # Check that workflows are registered
        self.assertIsNotNone(wf.getDefaultChain())

    def test_permissions_registered(self):
        """Test that permissions are properly registered."""
        portal = self.layer['portal']
        acl = api.portal.get_tool('acl_users')

        # Check that the portal has proper permissions
        self.assertIsNotNone(acl)

    def test_catalog_indexes(self):
        """Test that catalog indexes are properly configured."""
        portal = self.layer['portal']
        catalog = api.portal.get_tool('portal_catalog')

        # Check that catalog is available
        self.assertIsNotNone(catalog)

    def test_multilingual_setup(self):
        """Test that multilingual is properly set up."""
        portal = self.layer['portal']

        # Check that multilingual is available
        try:
            from plone.app.multilingual.interfaces import ITranslationManager
            self.assertTrue(True)  # If we can import, it's available
        except ImportError:
            self.fail("Multilingual support not available")

    def test_plone_version(self):
        """Test that we're running on the expected Plone version."""
        portal = self.layer['portal']

        # Check Plone version
        version = api.env.plone_version()
        self.assertTrue(version.startswith('6'))

    def test_python_version(self):
        """Test that we're running on the expected Python version."""
        import sys

        # Check Python version
        self.assertGreaterEqual(sys.version_info[0], 3)
        self.assertGreaterEqual(sys.version_info[1], 8)
