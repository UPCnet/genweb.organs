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
from plone.testing.z2 import Browser
from genweb.organs.namedfilebrowser import DisplayFile, Download
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import NotFound


class FunctionalTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

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
        # Create default Organs Test Folder
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

    def test_allroles_organ_obert_view_files_as_secretari(self):
        """Test as OG1-Secretari
        """
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre' 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = TestRequest()
        # Check session state PLANIFICADA
        print "\n    ORGAN OBERT - [Secretari] - SESSIO PLANIFICADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN PLANIFICADA
        #
        # Check session state CONVOCADA
        print "    ORGAN OBERT - [Secretari] - SESSIO CONVOCADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN CONVOCADA
        #
        # Check session state REALITZADA
        print "    ORGAN OBERT - [Secretari] - SESSIO REALITZADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN REALITZADA
        #
        # Check session state TANCADA
        print "    ORGAN OBERT - [Secretari] - SESSIO TANCADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN TANCADA
        #
        # Check session state CORRECCIO
        print "    ORGAN OBERT - [Secretari] - SESSIO EN MODIFICACIO"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # FIN EN CORRECCIO

    def test_allroles_organ_obert_view_files_as_editor(self):
        """Test as OG2-Editor
        """
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre' 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = TestRequest()
        # Check session state PLANIFICADA
        print "\n    ORGAN OBERT - [Editor] - SESSIO PLANIFICADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN PLANIFICADA
        #
        # Check session state CONVOCADA
        print "    ORGAN OBERT - [Editor] - SESSIO CONVOCADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN CONVOCADA
        #
        # Check session state REALITZADA
        print "    ORGAN OBERT - [Editor] - SESSIO REALITZADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN REALITZADA
        #
        # Check session state TANCADA
        print "    ORGAN OBERT - [Editor] - SESSIO TANCADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN TANCADA
        #
        # Check session state CORRECCIO
        print "    ORGAN OBERT - [Editor] - SESSIO EN MODIFICACIO"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # FIN EN CORRECCIO

    def test_allroles_organ_obert_view_files_as_membre(self):
        """ Test viewing files in OG Obert as user OG3-Membre
        """
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre' 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = TestRequest()
        # Check session state PLANIFICADA
        print "\n    ORGAN OBERT - [Membre] - SESSIO PLANIFICADA"
        # PUNT
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # PUNT/SUBPUNT
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # PUNT/SUBACORD
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # ACORD
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        #
        # FIN PLANIFICADA
        #
        # Check session state CONVOCADA
        print "    ORGAN OBERT - [Membre] - SESSIO CONVOCADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN CONVOCADA
        #
        # Check session state REALITZADA
        print "    ORGAN OBERT - [Membre] - SESSIO REALITZADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN REALITZADA
        #
        # Check session state TANCADA
        print "    ORGAN OBERT - [Membre] - SESSIO TANCADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        #
        # FIN TANCADA
        #
        # Check session state CORRECCIO
        print "    ORGAN OBERT - [Membre] - SESSIO EN MODIFICACIO"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - View"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - View"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - View"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - View"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer restringit (camp hidden) - Download - View"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - View"
        self.assertTrue(Download(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile')())
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - View"
        # FIN EN CORRECCIO

    def test_allroles_organ_obert_view_files_as_afectat(self):
        """Test as OG4-Afectat
        """
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre' 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = TestRequest()
        # Check session state PLANIFICADA
        print "\n    ORGAN OBERT - [Afectat] - SESSIO PLANIFICADA"
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # PUNT/SUBPUNT
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # PUNT/SUBACORD
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # ACORD
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.planificada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        #
        # FIN PLANIFICADA
        #
        # Check session state CONVOCADA
        print "    ORGAN OBERT - [Afectat] - SESSIO CONVOCADA"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # PUNT/SUBPUNT
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # PUNT/SUBCORD
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # ACORD
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public (camp visible) - Download - Unauthorized"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - Unauthorized"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.convocada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        #
        # FIN CONVOCADA
        #
        # Check session state REALITZADA
        print "    ORGAN OBERT - [Afectat] - SESSIO REALITZADA"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.realitzada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        #
        # FIN REALITZADA
        #
        # Check session state TANCADA
        print "    ORGAN OBERT - [Afectat] - SESSIO TANCADA"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # SUBPUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # SUBPUNT/ACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.tancada.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        #
        # FIN TANCADA
        #
        # Check session state CORRECCIO
        print "    ORGAN OBERT - [Afectat] - SESSIO EN MODIFICACIO"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.punt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.punt.subpunt.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.punt.subpunt['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBPUNT/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.punt.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        PUNT/SUBACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public (camp visible) - Download - True"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public (camp hidden) - Download - NotFound"
        self.assertRaises(NotFound, DisplayFile(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - NotFound"
        self.assertRaises(NotFound, Download(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - NotFound"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer restringit (camp hidden) - Download - Unauthorized"
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - DisplayFile - True"
        self.assertTrue(Download(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'visiblefile')())
        print "        ACORD/Fitxer public i restringit (camp visible) - Download - True"
        self.assertRaises(Unauthorized, DisplayFile(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - DisplayFile - Unauthorized"
        self.assertRaises(Unauthorized, Download(root_path.obert.correccio.acord['public-restringit'], request).publishTraverse(request, 'hiddenfile'))
        print "        ACORD/Fitxer public i restringit (camp hidden) - Download - Unauthorized"
        # FIN EN CORRECCIO

