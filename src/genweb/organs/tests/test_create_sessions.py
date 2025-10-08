#   WARNING!!!!

#     Las vistas llevan () al final para el AssertTrue
#       self.assertTrue(root_path.obert.xxtancadaxx.restrictedTraverse('@@view')())

#     Para check de Unauthorized/NotFound no lleva el ()
#       self.assertRaises(Unauthorized, root_path.obert.xxplanificadaxx.publishTraverse('@@view'))
#

import unittest
from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login, logout
from plone.app.testing import setRoles
from AccessControl import Unauthorized
from genweb.organs.browser import tools
from plone import api
from webtest import TestApp


class FunctionalTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.browser = TestApp(self.app)

        # Create default GW directories
        setupview = getMultiAdapter((self.portal, self.request), name='setup-view')
        setupview.apply_default_language_settings()
        setupview.setup_multilingual()
        setupview.createContent('n4')

        # Enable the possibility to add Organs folder
        from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
        behavior = ISelectableConstrainTypes(self.portal['ca'])
        behavior.setConstrainTypesMode(1)
        behavior.setLocallyAllowedTypes(['genweb.organs.organsfolder'])
        behavior.setImmediatelyAddableTypes(['genweb.organs.organsfolder'])

        # Create Base folder to create base test folders
        try:
            api.content.delete(
                obj=self.portal['ca']['testingfolder'],
                check_linkintegrity=False)
        except Exception:
            pass
        # Create default Organs Test Folder
        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='testingfolder',
            title='Organ Tests',
            container=self.portal['ca'])

        tools.create_organ_content(
            og_unit,
            'open_organ',
            'OG.OPEN',
            'Organ TEST Obert',
            'obert')
        tools.create_organ_content(
            og_unit,
            'restricted_to_affected_organ',
            'OG.AFFECTED',
            'Organ TEST restringit a AFECTATS',
            'afectats')
        tools.create_organ_content(
            og_unit,
            'restricted_to_members_organ',
            'OG.MEMBERS',
            'Organ TEST restringit a MEMBRES',
            'membres')

        logout()

    def test_create_sessions_in_all_organs(self):
        """ Test users who can create sessions
        """
        # Tree kind or organs
        root_obert = self.portal.ca.testingfolder.obert
        root_membres = self.portal.ca.testingfolder.membres
        root_afectats = self.portal.ca.testingfolder.afectats
        # Check roles
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(api.content.create(
            type='genweb.organs.sessio',
            id='session1',
            title='Session1',
            container=root_obert))
        print("\n    ORGAN OBERT [Secretari] - Add Session - True")
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(api.content.create(
            type='genweb.organs.sessio',
            id='session2',
            title='Session2',
            container=root_obert))
        print("    ORGAN OBERT [Editor]    - Add Session - True")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['OG3-Membre'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session3',
                title='Session3',
                container=root_obert)
        print("    ORGAN OBERT [Membre]    - Add Session - Unauthorized")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['OG4-Afectat'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session4',
                title='Session4',
                container=root_obert)
        print("    ORGAN OBERT [Afectat]   - Add Session - Unauthorized")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['OG5-Convidat'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session5',
                title='Session5',
                container=root_obert)
        print("    ORGAN OBERT [Convidat]   - Add Session - Unauthorized")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['Anonymous'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session6',
                title='Session6',
                container=root_obert)
        print("    ORGAN OBERT [Anonim]    - Add Session - Unauthorized")

        # Check organs membre
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(api.content.create(
            type='genweb.organs.sessio',
            id='session1',
            title='Session1',
            container=root_membres))
        print("\n    ORGAN RESTRINGIT MEMBRES [Secretari] - Add Session - True")
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(api.content.create(
            type='genweb.organs.sessio',
            id='session2',
            title='Session2',
            container=root_membres))
        print("    ORGAN RESTRINGIT MEMBRES [Editor]    - Add Session - True")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['OG3-Membre'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session3',
                title='Session3',
                container=root_membres)
        print("    ORGAN RESTRINGIT MEMBRES [Membre]    - Add Session - Unauthorized")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['OG4-Afectat'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session4',
                title='Session4',
                container=root_membres)
        print("    ORGAN RESTRINGIT MEMBRES [Afectat]   - Add Session - Unauthorized")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['OG5-Convidat'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session5',
                title='Session5',
                container=root_membres)
        print("    ORGAN RESTRINGIT MEMBRES [Convidat]   - Add Session - Unauthorized")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['Anonymous'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session6',
                title='Session6',
                container=root_membres)
        print("    ORGAN RESTRINGIT MEMBRES [Anonim]    - Add Session - Unauthorized")

        # Check organs afectat
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(api.content.create(
            type='genweb.organs.sessio',
            id='session1',
            title='Session1',
            container=root_afectats))
        print("\n    ORGAN RESTRINGIT AFECTATS [Secretari] - Add Session - True")
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(api.content.create(
            type='genweb.organs.sessio',
            id='session2',
            title='Session2',
            container=root_afectats))
        print("    ORGAN RESTRINGIT AFECTATS [Editor]    - Add Session - True")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['OG3-Membre'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session3',
                title='Session3',
                container=root_afectats)
        print("    ORGAN RESTRINGIT AFECTATS [Membre]    - Add Session - Unauthorized")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['OG4-Afectat'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session4',
                title='Session4',
                container=root_afectats)
        print("    ORGAN RESTRINGIT AFECTATS [Afectat]   - Add Session - Unauthorized")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['OG5-Convidat'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session5',
                title='Session5',
                container=root_afectats)
        print("    ORGAN RESTRINGIT AFECTATS [Convidat]   - Add Session - Unauthorized")
        logout()
        with self.assertRaises(Unauthorized):
            setRoles(self.portal, TEST_USER_ID, ['Anonymous'])
            login(self.portal, TEST_USER_NAME)
            api.content.create(
                type='genweb.organs.sessio',
                id='session6',
                title='Session6',
                container=root_afectats)
        print("    ORGAN RESTRINGIT AFECTATS [Anonim]    - Add Session - Unauthorized")
