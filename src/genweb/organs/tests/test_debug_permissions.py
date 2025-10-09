# -*- coding: utf-8 -*-
"""Debug permissions for genweb.organs."""

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING
import unittest


class TestDebugPermissions(unittest.TestCase):
    """Debug permissions for genweb.organs."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        """Set up test fixtures."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_debug_user_roles(self):
        """Debug user roles."""
        # Login as TEST_USER
        login(self.portal, TEST_USER_NAME)

        # Get user roles
        user = self.portal.acl_users.getUser(TEST_USER_ID)
        if user:
            roles = user.getRoles()
            print(f"User {TEST_USER_ID} has roles: {roles}")
        else:
            print(f"User {TEST_USER_ID} not found")

        # Try to set Manager role explicitly
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # Check roles again
        user = self.portal.acl_users.getUser(TEST_USER_ID)
        if user:
            roles = user.getRoles()
            print(f"After setRoles, user {TEST_USER_ID} has roles: {roles}")
        else:
            print(f"User {TEST_USER_ID} not found after setRoles")

        # Check if user can create organs
        try:
            organ = self.portal.invokeFactory(
                'genweb.organs.organsfolder',
                id='debug-organ',
                title='Debug Organ'
            )
            print(f"✅ User can create organs: {organ}")
        except Exception as e:
            print(f"❌ User cannot create organs: {e}")

        logout()

    def test_debug_custom_users(self):
        """Debug custom users."""
        # Check if custom users exist
        for user_id in ['usuari.manager', 'usuari.secretari', 'usuari.editor']:
            user = self.portal.acl_users.getUser(user_id)
            if user:
                roles = user.getRoles()
                print(f"User {user_id} has roles: {roles}")
            else:
                print(f"User {user_id} not found")


def test_suite():
    """Test suite."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDebugPermissions))
    return suite

