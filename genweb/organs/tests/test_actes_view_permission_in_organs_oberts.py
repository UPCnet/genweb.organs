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

    def test_organ_obert_view_actes_as_secretari(self):
        """Test as OG1-Secretari Actes i Audios
        """
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG1-Secretari'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder.obert
        request = TestRequest()
        # START check sessio PLANIFICADA
        self.assertTrue(root_path.planificada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.planificada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.planificada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.planificada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.planificada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.planificada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.planificada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio CONVOCADA
        self.assertTrue(root_path.convocada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.convocada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.convocada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.convocada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.convocada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.convocada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.convocada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio REALITZADA
        self.assertTrue(root_path.realitzada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.realitzada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.realitzada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.realitzada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.realitzada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.realitzada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.realitzada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio TANCADA
        self.assertTrue(root_path.tancada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.tancada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.tancada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.tancada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.tancada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.tancada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.tancada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio EN CORRECCIO
        self.assertTrue(root_path.correccio.restrictedTraverse('@@view')())
        self.assertTrue(root_path.correccio.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.correccio.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.correccio.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.correccio.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.correccio.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.correccio.acta.audio, request).publishTraverse(request, 'file')())

    def test_organ_obert_view_actes_as_editor(self):
        """Test as OG2-Editor Actes i Audios
        """
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG2-Editor'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder.obert
        request = TestRequest()
        # START check sessio PLANIFICADA
        self.assertTrue(root_path.planificada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.planificada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.planificada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.planificada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.planificada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.planificada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.planificada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio CONVOCADA
        self.assertTrue(root_path.convocada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.convocada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.convocada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.convocada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.convocada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.convocada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.convocada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio REALITZADA
        self.assertTrue(root_path.realitzada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.realitzada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.realitzada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.realitzada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.realitzada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.realitzada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.realitzada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio TANCADA
        self.assertTrue(root_path.tancada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.tancada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.tancada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.tancada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.tancada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.tancada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.tancada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio EN CORRECCIO
        self.assertTrue(root_path.correccio.restrictedTraverse('@@view')())
        self.assertTrue(root_path.correccio.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.correccio.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.correccio.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.correccio.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.correccio.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.correccio.acta.audio, request).publishTraverse(request, 'file')())

    def test_organ_obert_view_actes_as_membre(self):
        """Test as OG3-Membre Actes i Audios
        """
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG3-Membre'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder.obert
        request = TestRequest()
        # START check sessio PLANIFICADA
        self.assertRaises(Unauthorized, root_path.planificada.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, root_path.planificada.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.planificada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.planificada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.planificada.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.planificada.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.planificada.acta.audio, request).publishTraverse(request, 'file'))
        # START check sessio CONVOCADA
        self.assertTrue(root_path.convocada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.convocada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.convocada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.convocada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.convocada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.convocada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.convocada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio REALITZADA
        self.assertTrue(root_path.realitzada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.realitzada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.realitzada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.realitzada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.realitzada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.realitzada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.realitzada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio TANCADA
        self.assertTrue(root_path.tancada.restrictedTraverse('@@view')())
        self.assertTrue(root_path.tancada.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.tancada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.tancada.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.tancada.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.tancada.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.tancada.acta.audio, request).publishTraverse(request, 'file')())
        # START check sessio EN CORRECCIO
        self.assertTrue(root_path.correccio.restrictedTraverse('@@view')())
        self.assertTrue(root_path.correccio.acta.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.correccio.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.correccio.acta, request).publishTraverse(request, 'file')())
        self.assertTrue(root_path.correccio.acta.audio.restrictedTraverse('@@view')())
        self.assertTrue(DisplayFile(root_path.correccio.acta.audio, request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.correccio.acta.audio, request).publishTraverse(request, 'file')())

    def test_organ_obert_view_actes_as_afectat(self):
        """Test as OG4-Afectat Actes i Audios
        """
        logout()
        setRoles(self.portal, TEST_USER_ID, ['OG4-Afectat'])
        login(self.portal, TEST_USER_NAME)
        root_path = self.portal.ca.testingfolder.obert
        request = TestRequest()
        # START check sessio PLANIFICADA
        self.assertRaises(Unauthorized, root_path.planificada.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, root_path.planificada.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.planificada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.planificada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.planificada.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.planificada.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.planificada.acta.audio, request).publishTraverse(request, 'file'))
        # START check sessio CONVOCADA
        self.assertRaises(Unauthorized, root_path.convocada.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, root_path.convocada.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.convocada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.convocada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.convocada.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.convocada.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.convocada.acta.audio, request).publishTraverse(request, 'file'))
        # START check sessio REALITZADA
        self.assertTrue(root_path.realitzada.restrictedTraverse('@@view')())
        self.assertRaises(Unauthorized, root_path.realitzada.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.realitzada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.realitzada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.realitzada.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.realitzada.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.realitzada.acta.audio, request).publishTraverse(request, 'file'))
        # START check sessio TANCADA
        self.assertTrue(root_path.tancada.restrictedTraverse('@@view')())
        self.assertRaises(Unauthorized, root_path.tancada.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.tancada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.tancada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.tancada.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.tancada.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.tancada.acta.audio, request).publishTraverse(request, 'file'))
        # START check sessio EN CORRECCIO
        self.assertTrue(root_path.correccio.restrictedTraverse('@@view')())
        self.assertRaises(Unauthorized, root_path.correccio.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.correccio.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.correccio.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.correccio.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.correccio.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.correccio.acta.audio, request).publishTraverse(request, 'file'))

    def test_organ_obert_view_actes_as_anonim(self):
        """Test as ANONIM Actes i Audios
        """
        logout()
        root_path = self.portal.ca.testingfolder.obert
        request = TestRequest()
        # START check sessio PLANIFICADA
        self.assertRaises(Unauthorized, root_path.planificada.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, root_path.planificada.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.planificada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.planificada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.planificada.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.planificada.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.planificada.acta.audio, request).publishTraverse(request, 'file'))
        # START check sessio CONVOCADA
        self.assertRaises(Unauthorized, root_path.convocada.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, root_path.convocada.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.convocada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.convocada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.convocada.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.convocada.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.convocada.acta.audio, request).publishTraverse(request, 'file'))
        # START check sessio REALITZADA
        self.assertRaises(Unauthorized, root_path.realitzada.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, root_path.realitzada.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.realitzada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.realitzada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.realitzada.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.realitzada.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.realitzada.acta.audio, request).publishTraverse(request, 'file'))
        # START check sessio TANCADA
        self.assertTrue(root_path.tancada.restrictedTraverse('@@view')())
        self.assertRaises(Unauthorized, root_path.tancada.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.tancada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.tancada.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.tancada.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.tancada.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.tancada.acta.audio, request).publishTraverse(request, 'file'))
        # START check sessio EN CORRECCIO
        self.assertTrue(root_path.correccio.restrictedTraverse('@@view')())
        self.assertRaises(Unauthorized, root_path.correccio.acta.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.correccio.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.correccio.acta, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, root_path.correccio.acta.audio.restrictedTraverse('@@view'))
        self.assertRaises(Unauthorized, DisplayFile(root_path.correccio.acta.audio, request).publishTraverse(request, 'file'))
        self.assertRaises(Unauthorized, Download(root_path.correccio.acta.audio, request).publishTraverse(request, 'file'))
