# -*- coding: utf-8 -*-
"""Debug permissions for genweb.organs."""

from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import logout
from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING
import unittest


class TestPermissionDebug(unittest.TestCase):
    """Debug permissions for genweb.organs."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        """Set up test fixtures."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_debug_permissions(self):
        """Debug permissions."""
        # Login as Manager
        login(self.portal, 'usuari.manager')
        setRoles(self.portal, 'usuari.manager', ['Manager'])

        # Check if user has the permission
        from AccessControl import getSecurityManager
        sm = getSecurityManager()

        # Check if user can add organs
        can_add_organs = sm.checkPermission('Genweb Organs: Add Organs', self.portal)
        print(f"Can add organs: {can_add_organs}")

        # Check if user can add portal content
        can_add_portal_content = sm.checkPermission('Add portal content', self.portal)
        print(f"Can add portal content: {can_add_portal_content}")

        # Check if user can add folder
        can_add_folder = sm.checkPermission('Add folder', self.portal)
        print(f"Can add folder: {can_add_folder}")

        # Try to create a simple folder first
        try:
            folder = self.portal.invokeFactory(
                'Folder',
                id='test-folder',
                title='Test Folder'
            )
            print(f"✅ Can create Folder: {folder}")
        except Exception as e:
            print(f"❌ Cannot create Folder: {e}")

        # Try to create an organ
        try:
            organ = self.portal.invokeFactory(
                'genweb.organs.organsfolder',
                id='test-organ',
                title='Test Organ'
            )
            print(f"✅ Can create Organ: {organ}")
        except Exception as e:
            print(f"❌ Cannot create Organ: {e}")

        logout()


def test_suite():
    """Test suite."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPermissionDebug))
    return suite

