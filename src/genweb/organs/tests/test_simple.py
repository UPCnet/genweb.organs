# -*- coding: utf-8 -*-
"""Simple tests to verify basic functionality."""
import unittest
from plone import api
from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING


class TestSimpleFunctionality(unittest.TestCase):
    """Simple tests to verify basic functionality."""

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
