# import unittest
from genweb.organs.testing import GENWEB_ORGANS_INTEGRATION_TESTING
from zope.component import getMultiAdapter
# from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import login, logout
from plone.app.testing import setRoles
# from genweb.core.adapters import IImportant
# from transaction import commit
# from plone import api
from genweb.organs.browser import tools
import unittest


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = GENWEB_ORGANS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

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
        from plone import api
        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='testingfolder',
            title='Organ Tests',
            container=self.portal['ca'])

        # Create Open Organ structure
        tools.create_organ_content(
            og_unit,
            'restricted_to_affected_organ',
            'OG.AFFECTED',
            'Organ TEST restringit a AFECTATS',
            'afectats')

        logout()

    def test_organ_afectats(self):
        """ Test organ restringit a afectats
        """

        # Test as OG1-Secretari #
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        print "\n    ----Login as OG1-Secretari"
        self.assertTrue(self.portal.ca.testingfolder.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO PLANIFICADA - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO CONOVOCADA  - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO REALITZADA  - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO TANCADA     - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO MODIFICACIO - ES VEU"

        # Test as as OG2-Editor #
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        print "\n    ----Login as OG2-Editor"

        self.assertTrue(self.portal.ca.testingfolder.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG2-EDITOR - SESSIO PLANIFICADA - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG2-EDITOR - SESSIO CONOVOCADA  - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG2-EDITOR - SESSIO REALITZADA  - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG2-EDITOR - SESSIO TANCADA     - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG2-EDITOR - SESSIO MODIFICACIO - ES VEU"

        # Test as as OG3-Membre #
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        print "\n    ----Login as OG3-Membre"

        self.assertRaises(Unauthorized, self.portal.ca.testingfolder.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO PLANIFICADA - NO ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO CONOVOCADA  - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO REALITZADA  - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO TANCADA     - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO MODIFICACIO - ES VEU"

        # Test as as OG4-Afectat #
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        print "\n    ----Login as OG4-Afectat"

        self.assertRaises(Unauthorized, self.portal.ca.testingfolder.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO PLANIFICADA - NO ES VEU"
        self.assertRaises(Unauthorized, self.portal.ca.testingfolder.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO CONOVOCADA  - NO ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO REALITZADA  - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO TANCADA     - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO MODIFICACIO - ES VEU"

        # Test as Anonim #
        logout()
        print "\n    ----Login as Anonymous"

        self.assertRaises(Unauthorized, self.portal.ca.testingfolder.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO PLANIFICADA - NO ES VEU"
        self.assertRaises(Unauthorized, self.portal.ca.testingfolder.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO CONOVOCADA  - NO ES VEU"
        self.assertRaises(Unauthorized, self.portal.ca.testingfolder.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO REALITZADA  - NO ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO TANCADA     - ES VEU"
        self.assertTrue(self.portal.ca.testingfolder.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO MODIFICACIO - ES VEU"
