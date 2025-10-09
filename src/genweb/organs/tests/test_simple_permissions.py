# -*- coding: utf-8 -*-
"""Test simple permissions for genweb.organs."""

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from plone.api.exc import InvalidParameterError
from AccessControl.unauthorized import Unauthorized
from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING
from plone.app.testing import FunctionalTesting
from plone.testing import z2
import unittest


class TestSimplePermissions(unittest.TestCase):
    """Test simple permissions for genweb.organs."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        """Set up test fixtures."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_manager_can_create_organs(self):
        """Test that Manager can create organs."""
        # Login as Manager
        login(self.portal, 'usuari.manager')
        setRoles(self.portal, 'usuari.manager', ['Manager'])

        # Try to create an organ
        try:
            organ = self.portal.invokeFactory(
                'genweb.organs.organsfolder',
                id='test-organ',
                title='Test Organ'
            )
            self.assertIsNotNone(organ)
            print(f"✅ Manager can create organs: {organ}")
        except Unauthorized:
            self.fail("Manager should be able to create organs")
        finally:
            logout()

    def test_secretari_cannot_create_organs(self):
        """Test that Secretari cannot create organs."""
        # Login as Secretari
        login(self.portal, 'usuari.secretari')
        setRoles(self.portal, 'usuari.secretari', ['OG1-Secretari'])

        # Try to create an organ
        try:
            organ = self.portal.invokeFactory(
                'genweb.organs.organsfolder',
                id='test-organ-secretari',
                title='Test Organ Secretari'
            )
            self.fail("Secretari should not be able to create organs")
        except Unauthorized:
            print("✅ Secretari cannot create organs (as expected)")
        finally:
            logout()

    def test_manager_can_create_sessions(self):
        """Test that Manager can create sessions."""
        # First create an organ as Manager
        login(self.portal, 'usuari.manager')
        setRoles(self.portal, 'usuari.manager', ['Manager'])

        try:
            organ = self.portal.invokeFactory(
                'genweb.organs.organsfolder',
                id='test-organ-sessions',
                title='Test Organ Sessions'
            )
            self.assertIsNotNone(organ)

            # Now try to create a session in the organ
            session = self.portal[organ].invokeFactory(
                'genweb.organs.sessio',
                id='test-session',
                title='Test Session'
            )
            self.assertIsNotNone(session)
            print(f"✅ Manager can create sessions: {session}")
        except Unauthorized as e:
            self.fail(f"Manager should be able to create sessions: {e}")
        finally:
            logout()

    def test_secretari_can_create_sessions(self):
        """Test that Secretari can create sessions."""
        # First create an organ as Manager
        login(self.portal, 'usuari.manager')
        setRoles(self.portal, 'usuari.manager', ['Manager'])

        try:
            organ = self.portal.invokeFactory(
                'genweb.organs.organsfolder',
                id='test-organ-secretari-sessions',
                title='Test Organ Secretari Sessions'
            )
            self.assertIsNotNone(organ)
        except Unauthorized as e:
            self.fail(f"Manager should be able to create organs: {e}")
        finally:
            logout()

        # Now login as Secretari and try to create a session
        login(self.portal, 'usuari.secretari')
        setRoles(self.portal, 'usuari.secretari', ['OG1-Secretari'])

        try:
            session = self.portal['test-organ-secretari-sessions'].invokeFactory(
                'genweb.organs.sessio',
                id='test-session-secretari',
                title='Test Session Secretari'
            )
            self.assertIsNotNone(session)
            print(f"✅ Secretari can create sessions: {session}")
        except Unauthorized as e:
            self.fail(f"Secretari should be able to create sessions: {e}")
        finally:
            logout()

    def test_membre_cannot_create_sessions(self):
        """Test that Membre cannot create sessions."""
        # First create an organ as Manager
        login(self.portal, 'usuari.manager')
        setRoles(self.portal, 'usuari.manager', ['Manager'])

        try:
            organ = self.portal.invokeFactory(
                'genweb.organs.organsfolder',
                id='test-organ-membre-sessions',
                title='Test Organ Membre Sessions'
            )
            self.assertIsNotNone(organ)
        except Unauthorized as e:
            self.fail(f"Manager should be able to create organs: {e}")
        finally:
            logout()

        # Now login as Membre and try to create a session
        login(self.portal, 'usuari.membre')
        setRoles(self.portal, 'usuari.membre', ['OG3-Membre'])

        try:
            session = self.portal['test-organ-membre-sessions'].invokeFactory(
                'genweb.organs.sessio',
                id='test-session-membre',
                title='Test Session Membre'
            )
            self.fail("Membre should not be able to create sessions")
        except Unauthorized:
            print("✅ Membre cannot create sessions (as expected)")
        finally:
            logout()


def test_suite():
    """Test suite."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSimplePermissions))
    return suite
