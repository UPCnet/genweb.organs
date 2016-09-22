# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from genweb.organs.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of genweb.organs into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if genweb.organs is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('genweb.organs'))

    def test_uninstall(self):
        """Test if genweb.organs is cleanly uninstalled."""
        self.installer.uninstallProducts(['genweb.organs'])
        self.assertFalse(self.installer.isProductInstalled('genweb.organs'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IGenwebOrgansLayer is registered."""
        from genweb.organs.interfaces import IGenwebOrgansLayer
        from plone.browserlayer import utils
        self.failUnless(IGenwebOrgansLayer in utils.registered_layers())
