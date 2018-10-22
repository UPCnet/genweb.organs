import unittest
from genweb.organs.testing import GENWEB_ORGANS_INTEGRATION_TESTING
from zope.component import getMultiAdapter
# from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import login, logout
from plone.app.testing import setRoles
from AccessControl import Unauthorized
from genweb.organs.browser import tools
from plone import api
from plone.testing.z2 import Browser
from genweb.organs.namedfilebrowser import DisplayFile, Download
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import NotFound


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = GENWEB_ORGANS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.browser = Browser(self.app)

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
            api.content.delete(obj=self.portal['ca']['testingfolder'], check_linkintegrity=False)
        except:
            pass
        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='testingfolder',
            title='Organ Tests',
            container=self.portal['ca'])

        # Create Open Organ structure
        tools.create_organ_content(
            og_unit,
            'open_organ',
            'OG.OPEN',
            'Organ TEST Obert',
            'obert')

        logout()

    def test_organ_obert_secretari(self):
        """Test as OG1-Secretari
        """
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = TestRequest()
        print "\n    ----Login as OG1-Secretari"
        self.assertTrue(root_path.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO PLANIFICADA - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO CONVOCADA  - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO REALITZADA  - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO TANCADA     - ES VEU"

        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO MODIFICACIO - ES VEU"

        self.assertTrue(DisplayFile(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

    def test_organ_obert_editor(self):
        # Test as as OG2-Editor #
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = TestRequest()
        print "\n    ----Login as OG2-Editor"

        self.assertTrue(root_path.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG2-EDITOR - SESSIO PLANIFICADA - ES VEU"

        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG2-EDITOR - SESSIO CONOVOCADA  - ES VEU"

        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG2-EDITOR - SESSIO REALITZADA  - ES VEU"

        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG2-EDITOR - SESSIO TANCADA     - ES VEU"

        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG2-EDITOR - SESSIO MODIFICACIO - ES VEU"

        self.assertTrue(DisplayFile(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        # Test as as OG3-Membre #
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        print "\n    ----Login as OG3-Membre"

        self.assertRaises(Unauthorized, root_path.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO PLANIFICADA - NO ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO CONOVOCADA  - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO REALITZADA  - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())

        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO TANCADA     - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())

        self.assertTrue(root_path.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO MODIFICACIO - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())

        # Test as as OG4-Afectat #
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        print "\n    ----Login as OG4-Afectat"

        self.assertRaises(Unauthorized, root_path.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO PLANIFICADA - NO ES VEU"
        self.assertRaises(Unauthorized, root_path.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO CONOVOCADA  - NO ES VEU"
        self.assertTrue(root_path.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO REALITZADA  - ES VEU"
        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO TANCADA     - ES VEU"
        self.assertTrue(root_path.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO MODIFICACIO - ES VEU"

        # Test as Anonim #
        logout()
        print "\n    ----Login as Anonymous"

        self.assertRaises(Unauthorized, root_path.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO PLANIFICADA - NO ES VEU"
        self.assertRaises(Unauthorized, root_path.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO CONOVOCADA  - NO ES VEU"
        self.assertRaises(Unauthorized, root_path.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO REALITZADA  - NO ES VEU"
        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO TANCADA     - ES VEU"
        self.assertTrue(root_path.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO MODIFICACIO - ES VEU"

    def test_organ_obert_membre(self):
        """Test as OG3-Membre
        """
        setRoles(self.portal, TEST_USER_ID, ['OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        print "\n    ----Login as OG3-Membre"

        self.assertRaises(Unauthorized, root_path.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO PLANIFICADA - NO ES VEU"
        self.assertTrue(root_path.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO CONOVOCADA  - ES VEU"
        self.assertTrue(root_path.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO REALITZADA  - ES VEU"
        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO TANCADA     - ES VEU"
        self.assertTrue(root_path.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG3-MEMBRE - SESSIO MODIFICACIO - ES VEU"

        # Test as as OG4-Afectat #
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        print "\n    ----Login as OG4-Afectat"

        self.assertRaises(Unauthorized, root_path.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO PLANIFICADA - NO ES VEU"
        self.assertRaises(Unauthorized, root_path.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO CONOVOCADA  - NO ES VEU"
        self.assertTrue(root_path.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO REALITZADA  - ES VEU"
        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO TANCADA     - ES VEU"
        self.assertTrue(root_path.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG4-AFECTAT - SESSIO MODIFICACIO - ES VEU"

        # Test as Anonim #
        logout()
        print "\n    ----Login as Anonymous"

        self.assertRaises(Unauthorized, root_path.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO PLANIFICADA - NO ES VEU"
        self.assertRaises(Unauthorized, root_path.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO CONOVOCADA  - NO ES VEU"
        self.assertRaises(Unauthorized, root_path.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO REALITZADA  - NO ES VEU"
        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO TANCADA     - ES VEU"
        self.assertTrue(root_path.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - ANONIM - SESSIO MODIFICACIO - ES VEU"

    def test_organ_obert_afectat(self):
        """Test as OG1-Secretari
        """
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = TestRequest()
        print "\n    ----Login as OG1-Secretari"
        self.assertTrue(root_path.obert.planificada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO PLANIFICADA - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.convocada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO CONVOCADA  - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.realitzada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO REALITZADA  - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO TANCADA     - ES VEU"

        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

        self.assertTrue(root_path.obert.correcio.restrictedTraverse('@@view'))
        print "    OK! ORGAN OBERT - OG1-SECRETARI - SESSIO MODIFICACIO - ES VEU"

        self.assertTrue(DisplayFile(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        OK! FILE PUBLIC - DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE RESTRINGIT DOWNLOAD AND VIEW - ES VEU"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        OK! FILE AMB PUBLIC I RESTRINGIT - DOWNLOAD AND VIEW - ES VEU"

    def test_organ_obert_anonymous(self):
        """Test as Anonymous
        """
        logout()
        root_path = self.portal.ca.testingfolder
        request = TestRequest()
        print "\n    ---- User Anonymous. Not logged in."
        self.assertRaises(Unauthorized, root_path.obert.planificada.restrictedTraverse('@@view'))
        print "    ORGAN OBERT - [Anonim] - SESSIO PLANIFICADA - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertTrue(Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer restringit (camp hidden) DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer restringit (camp hidden) Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public i restringit (camp hidden) DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public i restringit (camp hidden) - Download - Unauthorized"

        self.assertRaises(Unauthorized, root_path.obert.convocada.restrictedTraverse('@@view'))
        print "    ORGAN OBERT - [Anonim] - SESSIO CONVOCADA - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer restringit (camp hidden) DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer restringit (camp hidden) Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public i restringit (camp hidden) DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public i restringit (camp hidden) - Download - Unauthorized"

        self.assertTrue(root_path.obert.realitzada.restrictedTraverse('@@view'))
        print "    ORGAN OBERT - [Anonim] - SESSIO REALITZADA  - True"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer restringit (camp hidden) DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer restringit (camp hidden) Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public i restringit (camp hidden) DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public i restringit (camp hidden) - Download - Unauthorized"

        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view'))
        print "    ORGAN OBERT - [Anonim] - SESSIO TANCADA - True"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public i restringit (camp hidden) - Download - Unauthorized"

        self.assertTrue(root_path.obert.correcio.restrictedTraverse('@@view'))
        print "    ORGAN OBERT - [Anonim] - SESSIO MODIFICACIO - True"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correcio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correcio.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correcio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        Fitxer public i restringit (camp hidden) - Download - Unauthorized"
