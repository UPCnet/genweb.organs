# -*- coding: utf-8 -*-
import unittest
import warnings

from AccessControl import Unauthorized
from genweb.organs.browser import tools
from genweb.organs.namedfilebrowser import DisplayFile, Download
from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, logout, setRoles
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from zope.component import getMultiAdapter
from zope.publisher.interfaces import NotFound


class FunctionalTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        # Suprimir ResourceWarnings de archivos blob no cerrados explícitamente
        warnings.filterwarnings("ignore", category=ResourceWarning)

        # Suprimir DeprecationWarnings de Plone (opcional)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # Create default GW directories
        setupview = getMultiAdapter(
            (self.portal, self.request),
            name='setup-view'
        )
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
                check_linkintegrity=False
            )
        except Exception:
            pass

        # Create default Organs Test Folder
        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='testingfolder',
            title='Organ Tests',
            container=self.portal['ca']
        )

        # Create Organ structure
        tools.create_organ_content(
            og_unit,
            'open_organ',
            'OG.OPEN',
            'Organ TEST Obert',
            'obert'
        )

        logout()

    def should_view_as_secretari(self, root_path, roles_info=""):
        if roles_info:
            print(f"  ✓ Verificando permisos como OG1-Secretari ({roles_info})")
        else:
            print("  ✓ Verificando permisos como OG1-Secretari")
        request = self.request
        # Check session state PLANIFICADA
        print("    → Estado PLANIFICADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CONVOCADA
        print("    → Estado CONVOCADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.convocada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state REALITZADA
        print("    → Estado REALITZADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.realitzada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state TANCADA
        print("    → Estado TANCADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.punt.restringit, request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CORRECCIO
        print("    → Estado CORRECCIO: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.correccio.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        print("  ✓ Verificación completa como OG1-Secretari")

    def should_view_as_editor(self, root_path, roles_info=""):
        if roles_info:
            print(f"  ✓ Verificando permisos como OG2-Editor ({roles_info})")
        else:
            print("  ✓ Verificando permisos como OG2-Editor")
        request = self.request
        # Check session state PLANIFICADA
        print("    → Estado PLANIFICADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.planificada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CONVOCADA
        print("    → Estado CONVOCADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.convocada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state REALITZADA
        print("    → Estado REALITZADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.realitzada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state TANCADA
        print("    → Estado TANCADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.punt.restringit, request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CORRECCIO
        print("    → Estado CORRECCIO: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.correccio.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        print("  ✓ Verificación completa como OG2-Editor")

    def should_view_as_membre_or_convidat(self, root_path, roles_info=""):
        if roles_info:
            print(
                f"  ✓ Verificando permisos como OG3-Membre/OG5-Convidat ({roles_info})")
        else:
            print("  ✓ Verificando permisos como OG3-Membre/OG5-Convidat")
        request = self.request
        # Check session state PLANIFICADA
        print("    → Estado PLANIFICADA: Sin acceso (restringido)")
        # PUNT
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.public, request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.public,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.restringit,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        # PUNT/SUBPUNT
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.subpunt.public,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        # PUNT/SUBACORD
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.acord.public,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.acord.restringit,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.acord['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt.acord['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.acord['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt.acord['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        # ACORD
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.acord.public,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.acord.restringit,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        #
        # Check session state CONVOCADA
        print("    → Estado CONVOCADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.convocada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state REALITZADA
        print("    → Estado REALITZADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.realitzada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state TANCADA
        print("    → Estado TANCADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.punt.restringit, request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CORRECCIO
        print("    → Estado CORRECCIO: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.correccio.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        print("  ✓ Verificación completa como OG3-Membre/OG5-Convidat")

    def should_view_as_anonymous(self, root_path):
        print("  ✓ Verificando permisos como Anónimo")
        request = self.request
        # Check session state PLANIFICADA
        print("    → Estado PLANIFICADA: Sin acceso")
        # PUNT
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.public, request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.public,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        #
        # Check session state CONVOCADA
        print("    → Estado CONVOCADA: Solo acceso a archivo público (visiblefile)")
        # PUNT - Solo visible
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        # PUNT - public-restringit: solo visible, hidden denegado
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')()
        # PUNT - restringit: sin acceso
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.convocada.punt.restringit,
                     request).publishTraverse(request, 'hiddenfile')()
        #
        # Check session state REALITZADA
        print("    → Estado REALITZADA: Solo acceso a archivo público (visiblefile)")
        # PUNT - Solo visible
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.realitzada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        # PUNT - public-restringit: solo visible, hidden denegado
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')()
        #
        # Check session state TANCADA
        print("    → Estado TANCADA: Solo acceso a archivo público (visiblefile)")
        # PUNT - Solo visible
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        # PUNT - public-restringit: solo visible, hidden denegado
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')()
        #
        # Check session state CORRECCIO
        print("    → Estado CORRECCIO: Solo acceso a archivo público (visiblefile)")
        # PUNT - Solo visible
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        # PUNT - public-restringit: solo visible, hidden denegado
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')()
        print("  ✓ Verificación completa como Anónimo")

    def should_view_as_afectat(self, root_path):
        print("  ✓ Verificando permisos como OG4-Afectat")
        request = self.request
        # Check session state PLANIFICADA
        print("    → Estado PLANIFICADA: Sin acceso (restringido)")
        # PUNT
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.public, request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.public,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.restringit,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        # PUNT/SUBPUNT
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.subpunt.public,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt.subpunt['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        # PUNT/SUBACORD
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.acord.public,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.punt.acord.restringit,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.acord['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt.acord['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.punt.acord['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.punt.acord['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        # ACORD
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.acord.public,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.acord.public,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.planificada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.planificada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.obert.planificada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(root_path.obert.planificada.acord.restringit,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.obert.planificada.acord['public-restringit'],
                request).publishTraverse(
                request, 'hiddenfile')()
        #
        # Check session state CONVOCADA
        print("    → Estado CONVOCADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(root_path.obert.convocada.restrictedTraverse('@@view'))
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(Download(root_path.obert.convocada.punt.public,
                        request).publishTraverse(request, 'visiblefile'))
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.convocada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(Download(root_path.obert.convocada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile'))
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(Download(root_path.obert.convocada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # PUNT/SUBCORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile'))
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(Download(root_path.obert.convocada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            Download(
                root_path.obert.convocada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile'))
        self.assertTrue(Download(root_path.obert.convocada.acord.public,
                        request).publishTraverse(request, 'visiblefile'))
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.convocada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.convocada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(Download(root_path.obert.convocada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        self.assertTrue(
            Download(
                root_path.obert.convocada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile'))
        #
        # Check session state REALITZADA
        print("    → Estado REALITZADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(root_path.obert.realitzada.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.realitzada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt.restringit,
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.realitzada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.realitzada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.realitzada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state TANCADA
        print("    → Estado TANCADA: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(root_path.obert.tancada.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.tancada.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.punt.restringit, request).publishTraverse(
                request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # SUBPUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # SUBPUNT/ACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.punt.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.tancada.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.tancada.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.tancada.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.tancada.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.tancada.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        #
        # Check session state CORRECCIO
        print("    → Estado CORRECCIO: Acceso completo a ambos archivos")
        # PUNT
        self.assertTrue(root_path.obert.correccio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(
                root_path.obert.correccio.punt.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBPUNT
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.subpunt.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.subpunt.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.subpunt.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.subpunt.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.subpunt['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.subpunt
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # PUNT/SUBACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.acord.public,
                        request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.punt.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.punt.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.punt.acord
                ['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        # ACORD
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(Download(root_path.obert.correccio.acord.public,
                        request).publishTraverse(request, 'visiblefile')())
        with self.assertRaises(NotFound):
            DisplayFile(
                root_path.obert.correccio.acord.public, request).publishTraverse(
                request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.acord.public,
                     request).publishTraverse(request, 'hiddenfile')()
        with self.assertRaises(NotFound):
            DisplayFile(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'visiblefile')()
        with self.assertRaises(NotFound):
            Download(root_path.obert.correccio.acord.restringit,
                     request).publishTraverse(request, 'visiblefile')()
        self.assertTrue(DisplayFile(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(Download(root_path.obert.correccio.acord.restringit,
                        request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'visiblefile')())
        self.assertTrue(
            DisplayFile(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        self.assertTrue(
            Download(
                root_path.obert.correccio.acord['public-restringit'],
                request).publishTraverse(request, 'hiddenfile')())
        print("  ✓ Verificación completa como OG4-Afectat")

    def test_organobert_must_be_shown_as_secretari(self):
        """Test permisos de OG1-Secretari en órgano oberts"""
        print("\n✅ Verificando permisos del rol OG1-Secretari en órgano oberts")
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(
            self.portal, TEST_USER_ID,
            ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(
            root_path, "con OG2-Editor, OG3-Membre y OG4-Afectat")
        logout()
        setRoles(self.portal, TEST_USER_ID, [
                 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path, "con OG2-Editor y OG3-Membre")
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari', 'OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path, "con OG2-Editor")
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari', 'OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path, "con OG3-Membre")
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path, "con OG4-Afectat")
        logout()
        setRoles(self.portal, TEST_USER_ID, [
                 'OG1-Secretari', 'OG2-Editor', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path, "con OG2-Editor y OG4-Afectat")
        logout()
        setRoles(self.portal, TEST_USER_ID, [
                 'OG1-Secretari', 'OG3-Membre', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path, "con OG3-Membre y OG4-Afectat")
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_secretari(root_path, "solo")
        logout()

    def test_organobert_must_be_shown_as_editor(self):
        """Test permisos de OG2-Editor en órgano oberts"""
        print("\n✅ Verificando permisos del rol OG2-Editor en órgano oberts")
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor', 'OG3-Membre', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_editor(root_path, "con OG3-Membre y OG4-Afectat")
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor', 'OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_editor(root_path, "con OG3-Membre")
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_editor(root_path, "con OG4-Afectat")
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_editor(root_path, "solo")
        logout()

    def test_organobert_must_be_shown_as_membre(self):
        """Test permisos de OG3-Membre en órgano oberts"""
        print("\n❌ Verificando restricciones del rol OG3-Membre en órgano oberts")
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(self.portal, TEST_USER_ID, ['OG3-Membre', 'OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_membre_or_convidat(root_path, "OG3-Membre con OG4-Afectat")
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(self.portal, TEST_USER_ID, ['OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_membre_or_convidat(root_path, "OG3-Membre solo")
        logout()

    def test_organobert_must_be_shown_as_afectat(self):
        """Test permisos de OG4-Afectat en órgano oberts"""
        print("\n❌ Verificando restricciones del rol OG4-Afectat en órgano oberts")
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(self.portal, TEST_USER_ID, ['OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_afectat(root_path)
        logout()

    def test_organobert_must_be_shown_as_convidat(self):
        """Test permisos de OG5-Convidat en órgano oberts"""
        print("\n❌ Verificando restricciones del rol OG5-Convidat en órgano oberts")
        logout()
        root_path = self.portal.ca.testingfolder
        setRoles(self.portal, TEST_USER_ID, ['OG5-Convidat'])
        login(self.portal, TEST_USER_NAME)
        self.should_view_as_membre_or_convidat(root_path, "OG5-Convidat solo")
        logout()

    def test_organobert_must_be_shown_as_anonymous(self):
        """Test permisos de usuario Anónimo en órgano oberts"""
        print("\n🌐 Verificando permisos de usuario Anónimo en órgano oberts")
        logout()
        root_path = self.portal.ca.testingfolder
        # Sin setRoles ni login - usuario anónimo
        self.should_view_as_anonymous(root_path)
        logout()
