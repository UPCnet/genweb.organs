# -*- coding: utf-8 -*-
"""Base test case for genweb.organs functional tests."""
import unittest
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login, logout, setRoles
from plone.testing.zope import Browser
from AccessControl import Unauthorized
from plone import api
from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        """Set up test fixtures."""
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.browser = Browser(self.app)

        # Create default GW directories
        self._setup_multilingual()

        # Enable the possibility to add Organs folder
        self._setup_organs_constraints()

        # Create test organs
        self._create_test_organs()

        logout()

    def _setup_multilingual(self):
        """Set up multilingual support."""
        try:
            # Check if plone.app.multilingual is available
            from plone.app.multilingual.setup import setupMultilingualSite

            # Setup multilingual site
            setupMultilingualSite(self.portal)

            # Get the default language folder
            default_lang = self.portal.portal_languages.getDefaultLanguage()
            if default_lang in self.portal:
                self.default_lang_folder = self.portal[default_lang]
            else:
                # Create default language folder if it doesn't exist
                self.default_lang_folder = self.portal

            print(f"Multilingual setup completed. "
                  f"Default language: {default_lang}")
        except ImportError:
            # plone.app.multilingual not available, using portal root
            self.default_lang_folder = self.portal
        except Exception as e:
            print(f"Warning: Could not setup multilingual: {e}")
            self.default_lang_folder = self.portal

    def _setup_organs_constraints(self):
        """Set up constraints for organs folder."""
        try:
            try:
                from plone.base.interfaces.constrains import (
                    ISelectableConstrainTypes)
            except ImportError:
                from Products.CMFPlone.interfaces.constrains import (
                    ISelectableConstrainTypes)

            # Use the default language folder or portal root
            container = getattr(self, 'default_lang_folder', self.portal)
            behavior = ISelectableConstrainTypes(container)
            behavior.setConstrainTypesMode(1)
            behavior.setLocallyAllowedTypes(
                ['genweb.organs.organsfolder'])
            behavior.setImmediatelyAddableTypes(
                ['genweb.organs.organsfolder'])
        except Exception as e:
            # Constraints setup failed, but this is not critical for tests
            pass

    def _create_test_organs(self):
        """Create test organs for testing."""
        # Use the default language folder or portal root
        container = getattr(self, 'default_lang_folder', self.portal)

        # Ensure we're logged in as Manager to create organs
        self.login_as_manager()

        # Create Base folder to create base test folders
        try:
            api.content.delete(
                obj=container['testingfolder'],
                check_linkintegrity=False)
        except Exception:
            pass

        # Create default Organs Test Folder
        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='testingfolder',
            title='Organ Tests',
            container=container)

        # Create different types of organs with basic content
        self._create_simple_organ(og_unit, 'obert', 'OG.OPEN',
                                  'Organ TEST Obert')
        self._create_simple_organ(og_unit, 'afectats', 'OG.AFFECTED',
                                  'Organ TEST restringit a AFECTATS')
        self._create_simple_organ(og_unit, 'membres', 'OG.MEMBERS',
                                  'Organ TEST restringit a MEMBRES')

    def _create_simple_organ(self, container, organ_id, acronym, title):
        """Create a simple organ without complex dependencies."""
        organ = api.content.create(
            type='genweb.organs.organgovern',
            id=organ_id,
            title=title,
            container=container,
            safe_id=True)
        organ.acronim = acronym
        organ.organType = acronym
        organ.visiblefields = True
        organ.eventsColor = 'green'

        # Grant permissions to test users on the organ
        # This simulates what would happen in production
        organ.manage_setLocalRoles('usuari.secretari', ['OG1-Secretari'])
        organ.manage_setLocalRoles('usuari.editor', ['OG2-Editor'])
        organ.manage_setLocalRoles('usuari.membre', ['OG3-Membre'])
        organ.manage_setLocalRoles('usuari.afectat', ['OG4-Afectat'])
        organ.manage_setLocalRoles('usuari.convidat', ['OG5-Convidat'])
        organ.reindexObjectSecurity()

        return organ

    def login_as_manager(self):
        """Login as manager user."""
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def login_as_secretari(self):
        """Login as secretari user."""
        login(self.portal, 'usuari.secretari')
        setRoles(self.portal, 'usuari.secretari', ['OG1-Secretari'])

    def login_as_editor(self):
        """Login as editor user."""
        login(self.portal, 'usuari.editor')
        setRoles(self.portal, 'usuari.editor', ['OG2-Editor'])

    def login_as_membre(self):
        """Login as membre user."""
        login(self.portal, 'usuari.membre')
        setRoles(self.portal, 'usuari.membre', ['OG3-Membre'])

    def login_as_afectat(self):
        """Login as afectat user."""
        login(self.portal, 'usuari.afectat')
        setRoles(self.portal, 'usuari.afectat', ['OG4-Afectat'])

    def login_as_convidat(self):
        """Login as convidat user."""
        login(self.portal, 'usuari.convidat')
        setRoles(self.portal, 'usuari.convidat', ['OG5-Convidat'])

    def logout(self):
        """Logout current user."""
        logout()

    def assertUnauthorized(self, func, *args, **kwargs):
        """Assert that a function raises Unauthorized."""
        with self.assertRaises(Unauthorized):
            func(*args, **kwargs)

    def assertCanCreate(self, content_type, container, **kwargs):
        """Assert that content can be created."""
        try:
            content = api.content.create(
                type=content_type,
                container=container,
                **kwargs
            )
            self.assertIsNotNone(content)
            return content
        except Unauthorized:
            self.fail(
                f"User should be able to create {content_type} "
                f"but got Unauthorized")

    def assertCannotCreate(self, content_type, container, **kwargs):
        """Assert that content cannot be created."""
        with self.assertRaises(Unauthorized):
            api.content.create(
                type=content_type,
                container=container,
                **kwargs
            )
