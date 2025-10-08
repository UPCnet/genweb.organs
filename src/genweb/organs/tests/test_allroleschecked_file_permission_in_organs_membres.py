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
        except:
            pass
        # Create default Organs Test Folder
        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='testingfolder',
            title='Organ Tests',
            container=self.portal['ca'])

        # Create Organ structure
        tools.create_organ_content(
            og_unit,
            'restricted_to_members_organ',
            'OG.MEMBERS',
            'Organ TEST restringit a MEMBRES',
            'membres')

        logout()

    def should_view_as_secretari(self, root_path):
        request = TestRequest()
        # Check session state PLANIFICADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CONVOCADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state REALITZADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state TANCADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CORRECCIO
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # FIN EN CORRECCIO

    def should_view_as_editor(self, root_path):
        request = TestRequest()
        # Check session state PLANIFICADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CONVOCADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state REALITZADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state TANCADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CORRECCIO
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

    def should_view_as_membre_or_convidat(self, root_path):
        request = TestRequest()
        # Check session state PLANIFICADA
        # PUNT
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        #
        # Check session state CONVOCADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.convocada.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.convocada.acord['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state REALITZADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.realitzada.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state TANCADA
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.tancada.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.tancada.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.tancada.acord['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CORRECCIO
        # PUNT
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.correccio.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.membres.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.membres.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.membres.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.membres.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.correccio.acord['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

    def should_view_as_afectat(self, root_path):
        request = TestRequest()
        # Check session state PLANIFICADA
        # PUNT
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.planificada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.planificada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        #
        # Check session state CONVOCADA
        # PUNT
        self.assertRaises(
            Unauthorized, root_path.membres.convocada.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.convocada.punt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(root_path.membres.convocada.punt.public, request).publishTraverse(
                request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.convocada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.convocada.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.convocada.punt['public-restringit'],
                              request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.convocada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.convocada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBCORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.convocada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.convocada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.convocada.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.convocada.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.convocada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.convocada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.convocada.acord['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.convocada.acord['public-restringit'],
                              request).publishTraverse(request, 'hiddenfile'))
        #
        # Check session state REALITZADA
        # PUNT
        self.assertRaises(
            Unauthorized, root_path.membres.realitzada.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.realitzada.punt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.realitzada.punt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.realitzada.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.realitzada.punt['public-restringit'],
                              request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.realitzada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.realitzada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.realitzada.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.realitzada.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.realitzada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.realitzada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        #
        # Check session state TANCADA
        # PUNT
        self.assertRaises(
            Unauthorized, root_path.membres.tancada.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.tancada.punt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(root_path.membres.tancada.punt.public, request).publishTraverse(
                request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.tancada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.tancada.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.tancada.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.tancada.punt['public-restringit'],
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.tancada.punt['public-restringit'],
                              request).publishTraverse(request, 'hiddenfile'))
        # SUBPUNT/SUBPUNT
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.tancada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.tancada.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # SUBPUNT/ACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.tancada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.tancada.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.punt.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.tancada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.tancada.punt.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.tancada.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(root_path.membres.tancada.acord.public, request).publishTraverse(
                request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.tancada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.tancada.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.tancada.acord['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.tancada.acord['public-restringit'],
                              request).publishTraverse(request, 'hiddenfile'))
        #
        # Check session state CORRECCIO
        # PUNT
        self.assertRaises(
            Unauthorized, root_path.membres.correccio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.correccio.punt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(root_path.membres.correccio.punt.public, request).publishTraverse(
                request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.membres.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.correccio.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.correccio.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.correccio.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.correccio.punt['public-restringit'],
                              request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.correccio.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.correccio.punt.subpunt.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.correccio.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.correccio.punt.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.membres.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.membres.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.membres.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.membres.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.correccio.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.correccio.acord.public, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.membres.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.membres.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.membres.correccio.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.membres.correccio.acord.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.correccio.acord['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.membres.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.membres.correccio.acord['public-restringit'],
                              request).publishTraverse(request, 'hiddenfile'))

    def test_organmembres_must_be_shown_as_secretari(self):
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(
            self.portal, TEST_USER_ID,
            ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path)
        logout()
        setRoles(self.portal, TEST_USER_ID, [
                 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path)
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari', 'OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path)
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari', 'OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path)
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path)
        logout()
        setRoles(self.portal, TEST_USER_ID, [
                 'OG1-Secretari', 'OG2-Editor', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path)
        logout()
        setRoles(self.portal, TEST_USER_ID, [
                 'OG1-Secretari', 'OG3-Membre', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path)
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path)
        logout()

    def test_organmembres_must_be_shown_as_editor(self):
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor', 'OG3-Membre', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_editor(root_path)
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor', 'OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_editor(root_path)
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_editor(root_path)
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_editor(root_path)
        logout()

    def test_organmembres_must_be_shown_as_membre(self):
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(self.portal, TEST_USER_ID, ['OG3-Membre', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_membre_or_convidat(root_path)
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(self.portal, TEST_USER_ID, ['OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_membre_or_convidat(root_path)
        logout()

    def test_organmembres_must_be_shown_as_afectat(self):
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(self.portal, TEST_USER_ID, ['OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_afectat(root_path)
        logout()

    def test_organmembres_must_be_shown_as_convidat(self):
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(self.portal, TEST_USER_ID, ['OG5-Convidat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_membre_or_convidat(root_path)
        logout()
