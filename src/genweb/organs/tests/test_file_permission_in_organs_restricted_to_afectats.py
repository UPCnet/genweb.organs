#   WARNING!!!!
#
#     Las vistas con assertTrue llevan () al final para ejecutar la vista
#       self.assertTrue(root_path.afectats.tancada.restrictedTraverse('@@view')())
#
#     Para check de Unauthorized con assertRaises NO lleva el ()
#     porque la excepción se lanza durante restrictedTraverse
#       self.assertRaises(Unauthorized, root_path.afectats.planificada.restrictedTraverse, '@@view')
#

import unittest
import warnings
from AccessControl import Unauthorized
from plone import api
from plone.app.testing import (
    TEST_USER_ID,
    TEST_USER_NAME,
    login,
    logout,
    setRoles,
)
from zope.component import getMultiAdapter
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from zope.publisher.interfaces import NotFound

from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING
from genweb.organs.browser import tools
from genweb.organs.namedfilebrowser import DisplayFile, Download


class FunctionalTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        # Suprimir warnings molestos
        warnings.filterwarnings("ignore", category=ResourceWarning,
                                message=".*unclosed file.*")
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']  # ✅ Usar request del layer

        # Create default GW directories
        setupview = getMultiAdapter((self.portal, self.request), name='setup-view')
        setupview.apply_default_language_settings()
        setupview.setup_multilingual()
        setupview.createContent()

        # Enable the possibility to add Organs folder
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
        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='testingfolder',
            title='Organ Tests',
            container=self.portal['ca'])

        # Create Organ structure
        tools.create_organ_content(
            og_unit,
            'restricted_to_affected_organ',
            'OG.AFFECTED',
            'Organ TEST restringit a AFECTATS',
            'afectats')

        logout()

    def test_organ_restricted_to_afectats_view_files_as_secretari(self):
        """Test permisos de OG1-Secretari en órgano restringido a afectados."""
        print("\n✅ Verificando permisos del rol OG1-Secretari en órgano restringido a afectados")

        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = self.request  # ✅ Usar request del layer

        # Check session state PLANIFICADA
        print("   → Estado PLANIFICADA: Acceso completo a ambos archivos")
        self.assertTrue(root_path.afectats.planificada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.acord.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.acord.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state CONVOCADA
        print("   → Estado CONVOCADA: Acceso completo a ambos archivos")
        self.assertTrue(root_path.afectats.convocada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.convocada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.convocada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state REALITZADA
        print("   → Estado REALITZADA: Acceso completo a ambos archivos")
        self.assertTrue(root_path.afectats.realitzada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state TANCADA
        print("   → Estado TANCADA: Acceso completo a ambos archivos")
        self.assertTrue(root_path.afectats.tancada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.afectats.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.tancada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.tancada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.afectats.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state CORRECCIO
        print("   → Estado CORRECCIO: Acceso completo a ambos archivos")
        self.assertTrue(root_path.afectats.correccio.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.correccio.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.correccio.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        logout()

    def test_organ_restricted_to_afectats_view_files_as_editor(self):
        """Test permisos de OG2-Editor en órgano restringido a afectados."""
        print("\n✅ Verificando permisos del rol OG2-Editor en órgano restringido a afectados")

        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = self.request  # ✅ Usar request del layer

        # Check session state PLANIFICADA
        print("   → Estado PLANIFICADA: Acceso completo a ambos archivos")
        self.assertTrue(root_path.afectats.planificada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.acord.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.acord.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.planificada.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.planificada.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state CONVOCADA
        print("   → Estado CONVOCADA: Acceso completo a ambos archivos")
        self.assertTrue(root_path.afectats.convocada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.convocada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.convocada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state REALITZADA
        print("   → Estado REALITZADA: Acceso completo a ambos archivos")
        self.assertTrue(root_path.afectats.realitzada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state TANCADA
        print("   → Estado TANCADA: Acceso completo a ambos archivos")
        self.assertTrue(root_path.afectats.tancada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.afectats.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.tancada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.tancada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.afectats.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state CORRECCIO
        print("   → Estado CORRECCIO: Acceso completo a ambos archivos")
        self.assertTrue(root_path.afectats.correccio.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.correccio.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.correccio.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        logout()

    def test_organ_restricted_to_afectats_view_files_as_membre(self):
        """Test restricciones de OG3-Membre en órgano restringido a afectados."""
        print("\n❌ Verificando restricciones del rol OG3-Membre en órgano restringido a afectados")

        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = self.request  # ✅ Usar request del layer

        # Check session state PLANIFICADA
        print("   → Estado PLANIFICADA: Sin acceso")
        self.assertRaises(
            Unauthorized, root_path.afectats.planificada.restrictedTraverse, '@@view')
        # PUNT
        self.assertRaises(Unauthorized, DisplayFile(root_path.afectats.planificada.punt.public,
                                                    request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(root_path.afectats.planificada.punt.public,
                                                 request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.afectats.planificada.punt.restringit,
                                                    request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(root_path.afectats.planificada.punt.restringit,
                                                 request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.afectats.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.afectats.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.afectats.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.afectats.planificada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBACORD
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.afectats.planificada.punt.acord.public,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.afectats.planificada.punt.acord.public,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.acord.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.acord.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          DisplayFile(
                              root_path.afectats.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.afectats.planificada.punt.acord.restringit,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(Unauthorized, DisplayFile(root_path.afectats.planificada.acord.public,
                                                    request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, Download(root_path.afectats.planificada.acord.public,
                                                 request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.planificada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.afectats.planificada.acord.restringit,
                                                    request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(root_path.afectats.planificada.acord.restringit,
                                                 request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))

        # Check session state CONVOCADA
        print("   → Estado CONVOCADA: Acceso a visiblefile, restricción en public-restringit")
        self.assertTrue(root_path.afectats.convocada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.afectats.convocada.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.convocada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.convocada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.convocada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.convocada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.convocada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state REALITZADA
        print("   → Estado REALITZADA: Acceso a visiblefile, restricción en public-restringit")
        self.assertTrue(root_path.afectats.realitzada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.realitzada.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.realitzada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.realitzada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state TANCADA
        print("   → Estado TANCADA: Acceso a visiblefile, restricción en public-restringit")
        self.assertTrue(root_path.afectats.tancada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.afectats.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.afectats.tancada.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt['public-restringit'],
                        request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.punt.subpunt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.tancada.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.tancada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.tancada.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(root_path.afectats.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.tancada.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.afectats.tancada.acord['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.tancada.acord['public-restringit'],
                        request).publishTraverse(request, 'hiddenfile')())

        # Check session state CORRECCIO
        print("   → Estado CORRECCIO: Acceso a visiblefile, restricción en public-restringit")
        self.assertTrue(root_path.afectats.correccio.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized,
                          Download(
                              root_path.afectats.correccio.punt['public-restringit'],
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt['public-restringit'],
                        request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.correccio.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.correccio.punt.subpunt.public,
                              request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.correccio.punt.subpunt.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.punt.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound,
                          DisplayFile(
                              root_path.afectats.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound,
                          Download(
                              root_path.afectats.correccio.punt.acord.restringit,
                              request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.afectats.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.acord.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.correccio.acord.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(DisplayFile(root_path.afectats.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.afectats.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        logout()

    def test_organ_restricted_to_afectats_view_files_as_afectat(self):
        """Test restricciones de OG4-Afectat en órgano restringido a afectados."""
        print("\n❌ Verificando restricciones del rol OG4-Afectat en órgano restringido a afectados")

        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = self.request  # ✅ Usar request del layer

        # Check session state PLANIFICADA
        print("   → Estado PLANIFICADA: Sin acceso")
        self.assertRaises(
            Unauthorized, root_path.afectats.planificada.restrictedTraverse, '@@view')

        # Check session state CONVOCADA - AFECTAT NO tiene acceso
        print("   → Estado CONVOCADA: Sin acceso")
        self.assertRaises(
            Unauthorized, root_path.afectats.convocada.restrictedTraverse, '@@view')

        # Check session state REALITZADA - desde aquí SÍ tiene acceso
        print("   → Estado REALITZADA: Acceso a visiblefile, no a hiddenfile")
        self.assertTrue(root_path.afectats.realitzada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(DisplayFile(root_path.afectats.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.afectats.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.public, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(NotFound, DisplayFile(
            root_path.afectats.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(NotFound, Download(
            root_path.afectats.realitzada.punt.restringit, request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(Unauthorized, DisplayFile(
            root_path.afectats.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(Unauthorized, Download(
            root_path.afectats.realitzada.punt.restringit, request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))

        # Check session state TANCADA
        print("   → Estado TANCADA: Acceso a visiblefile, no a hiddenfile")
        self.assertTrue(root_path.afectats.tancada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))

        # Check session state CORRECCIO
        print("   → Estado CORRECCIO: Acceso a visiblefile, no a hiddenfile")
        self.assertTrue(root_path.afectats.correccio.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))

        logout()

    def test_organ_restricted_to_afectats_view_files_as_convidat(self):
        """Test permisos de OG5-Convidat en órgano restringido a afectados."""
        print("\n→ Rol OG5-Convidat en órgano restringido a afectados")

        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG5-Convidat'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder
        request = self.request

        # Check session state PLANIFICADA
        print("   → Estado PLANIFICADA: Sin acceso")
        self.assertRaises(
            Unauthorized, root_path.afectats.planificada.restrictedTraverse, '@@view')

        # Check session state CONVOCADA
        print("   → Estado CONVOCADA: Acceso completo excepto visiblefile de public-restringit")
        self.assertTrue(root_path.afectats.convocada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state REALITZADA
        print("   → Estado REALITZADA: Acceso completo excepto visiblefile de public-restringit")
        self.assertTrue(root_path.afectats.realitzada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state TANCADA
        print("   → Estado TANCADA: Acceso completo excepto visiblefile de public-restringit")
        self.assertTrue(root_path.afectats.tancada.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        # Check session state CORRECCIO
        print("   → Estado CORRECCIO: Acceso completo excepto visiblefile de public-restringit")
        self.assertTrue(root_path.afectats.correccio.restrictedTraverse('@@view')())
        # PUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'visiblefile')())
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())

        logout()

    def test_organ_restricted_to_afectats_view_files_as_anonim(self):
        """Test restricciones de usuarios Anónimo en órgano restringido a afectados."""
        print("\n→ Usuario Anónimo en órgano restringido a afectados")

        logout()
        root_path = self.portal.ca.testingfolder
        request = self.request

        # Check session state PLANIFICADA
        print("   → Estado PLANIFICADA: Sin acceso a sesión ni archivos")
        self.assertRaises(
            Unauthorized, root_path.afectats.planificada.restrictedTraverse, '@@view')
        # PUNT
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.planificada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.planificada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.planificada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.planificada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.planificada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/ACORD
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.planificada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.planificada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.planificada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.planificada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.planificada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.planificada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))

        # Check session state CONVOCADA
        print("   → Estado CONVOCADA: Sin acceso a sesión ni archivos")
        self.assertRaises(
            Unauthorized, root_path.afectats.convocada.restrictedTraverse, '@@view')
        # PUNT
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/ACORD
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.convocada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.convocada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))

        # Check session state REALITZADA
        print("   → Estado REALITZADA: Sin acceso a sesión ni archivos")
        self.assertRaises(
            Unauthorized, root_path.afectats.realitzada.restrictedTraverse, '@@view')
        # PUNT
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/ACORD
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))

        # Check session state TANCADA
        print("   → Estado TANCADA: Sin acceso a sesión ni archivos")
        self.assertRaises(
            Unauthorized, root_path.afectats.tancada.restrictedTraverse, '@@view')
        # PUNT
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/ACORD
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))

        # Check session state CORRECCIO
        print("   → Estado CORRECCIO: Sin acceso a sesión ni archivos")
        self.assertRaises(
            Unauthorized, root_path.afectats.correccio.restrictedTraverse, '@@view')
        # PUNT
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.subpunt.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/ACORD
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.acord.public,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            NotFound,
            DisplayFile(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            NotFound,
            Download(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.acord.restringit,
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile'))
        self.assertRaises(
            Unauthorized,
            DisplayFile(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertRaises(
            Unauthorized,
            Download(
                root_path.afectats.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))

        logout()
