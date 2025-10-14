# -*- coding: utf-8 -*-
import datetime
import unittest
import warnings

from AccessControl import Unauthorized
from plone import api
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login, logout, setRoles
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobFile
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from zope.component import getMultiAdapter

from genweb.organs.namedfilebrowser import DisplayFile, Download
from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING


class OrgansFunctionalTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        # Suprimir ResourceWarnings de archivos blob no cerrados explícitamente
        warnings.filterwarnings("ignore", category=ResourceWarning)

        # Suprimir DeprecationWarnings de Plone (opcional, no recomendado)
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

        # Create Open Organ structure
        organ = api.content.create(
            type='genweb.organs.organgovern',
            id='obert',
            title='Organ TEST Obert',
            container=og_unit,
            safe_id=True
        )
        organ.acronim = 'OG.OPEN'
        organ.organType = 'open_organ'

        session_transitions = {
            'planificada': [],  # estado inicial
            'convocada': ['convocar'],
            'realitzada': ['convocar', 'realitzar'],
            'tancada': ['convocar', 'realitzar', 'tancar'],
            'correccio': ['convocar', 'realitzar', 'correccio']
        }

        now = datetime.datetime.now()
        for session_id, transitions in session_transitions.items():
            session = api.content.create(
                type='genweb.organs.sessio',
                id=session_id,
                title=f'Session {session_id.capitalize()}',
                container=organ,
                start=now,
                end=now + datetime.timedelta(hours=1),
                modality='attended',
                numSessioShowOnly='01',
                numSessio='01'
            )
            # Aplicar transiciones de workflow
            for transition in transitions:
                try:
                    api.content.transition(obj=session, transition=transition)
                except Exception:
                    pass  # Si la transición no existe, continuar

            acta = api.content.create(
                type='genweb.organs.acta', id='acta', title='Acta de la sessió',
                container=session,
                file=NamedBlobFile(
                    data=b'dummy acta content', filename='acta.txt',
                    contentType='text/plain'),
                membresConvocats=RichTextValue(
                    '<p>Membres convocats</p>', 'text/html', 'text/html'),
                membresConvidats=RichTextValue(
                    '<p>Membres convidats</p>', 'text/html', 'text/html'),
                llistaExcusats=RichTextValue(
                    '<p>Excusats</p>', 'text/html', 'text/html'),
                llistaNoAssistens=RichTextValue(
                    '<p>No assistents</p>', 'text/html', 'text/html'),
                ordenDelDia=RichTextValue(
                    '<p>Ordre del dia</p>', 'text/html', 'text/html'))

            api.content.create(
                type='genweb.organs.audio',
                id='audio',
                title='Audio de la sessió',
                container=acta,
                file=NamedBlobFile(
                    data=b'dummy audio content',
                    filename='audio.mp3',
                    contentType='audio/mpeg'
                )
            )

        logout()

    def test_organ_obert_view_actes_as_secretari(self):
        """Test as OG1-Secretari Actes i Audios"""
        logout()
        root_path = self.portal.ca.testingfolder.obert
        request = self.request

        print("\n✅ Verificando acceso del rol OG1-Secretari a las actas en "
              "órgano obert")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=root_path,
            roles=['OG1-Secretari']
        )
        # START check sessio PLANIFICADA
        view = root_path.planificada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.planificada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.planificada.acta, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.planificada.acta, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        view = root_path.planificada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.planificada.acta.audio, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.planificada.acta.audio, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        print("  ✓ Acceso correcto a actas en sesión PLANIFICADA")

        # START check sessio CONVOCADA
        view = root_path.convocada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.convocada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.convocada.acta, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.convocada.acta, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        view = root_path.convocada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.convocada.acta.audio, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.convocada.acta.audio, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        print("  ✓ Acceso correcto a actas en sesión CONVOCADA")

        # START check sessio REALITZADA
        view = root_path.realitzada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.realitzada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.realitzada.acta, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.realitzada.acta, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        view = root_path.realitzada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.realitzada.acta.audio, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.realitzada.acta.audio, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        print("  ✓ Acceso correcto a actas en sesión REALITZADA")

        # START check sessio TANCADA
        view = root_path.tancada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.tancada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.tancada.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.tancada.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.tancada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.tancada.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(
            Download(root_path.tancada.acta.audio, request).publishTraverse(
                request, 'file')())
        print("  ✓ Acceso correcto a actas en sesión TANCADA")

        # START check sessio EN CORRECCIO
        view = root_path.correccio.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.correccio.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.correccio.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.correccio.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.correccio.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.correccio.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.correccio.acta.audio,
                        request).publishTraverse(request, 'file')())
        print("  ✓ Acceso correcto a actas en sesión EN CORRECCIO")

    def test_organ_obert_view_actes_as_editor(self):
        """Test as OG2-Editor Actes i Audios"""
        logout()
        root_path = self.portal.ca.testingfolder.obert
        request = self.request

        print("\n✅ Verificando acceso del rol OG2-Editor a las actas en "
              "órgano obert")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(username=TEST_USER_ID, obj=root_path,
                             roles=['OG2-Editor'])
        # START check sessio PLANIFICADA
        view = root_path.planificada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.planificada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.planificada.acta, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.planificada.acta, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        view = root_path.planificada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.planificada.acta.audio, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.planificada.acta.audio, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        print("  ✓ Acceso correcto a actas en sesión PLANIFICADA")

        # START check sessio CONVOCADA
        view = root_path.convocada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.convocada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.convocada.acta, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.convocada.acta, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        view = root_path.convocada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.convocada.acta.audio, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.convocada.acta.audio, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        print("  ✓ Acceso correcto a actas en sesión CONVOCADA")

        # START check sessio REALITZADA
        view = root_path.realitzada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.realitzada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.realitzada.acta, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.realitzada.acta, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        view = root_path.realitzada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        display_file = DisplayFile(root_path.realitzada.acta.audio, request)
        self.assertTrue(display_file.publishTraverse(request, 'file')())
        download = Download(root_path.realitzada.acta.audio, request)
        self.assertTrue(download.publishTraverse(request, 'file')())
        print("  ✓ Acceso correcto a actas en sesión REALITZADA")

        # START check sessio TANCADA
        view = root_path.tancada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.tancada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.tancada.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.tancada.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.tancada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.tancada.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(
            Download(root_path.tancada.acta.audio, request).publishTraverse(
                request, 'file')())
        print("  ✓ Acceso correcto a actas en sesión TANCADA")

        # START check sessio EN CORRECCIO
        view = root_path.correccio.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.correccio.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.correccio.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.correccio.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.correccio.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.correccio.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.correccio.acta.audio,
                        request).publishTraverse(request, 'file')())
        print("  ✓ Acceso correcto a actas en sesión EN CORRECCIO")

    def test_organ_obert_view_actes_as_membre(self):
        """Test as OG3-Membre Actes i Audios"""
        logout()
        root_path = self.portal.ca.testingfolder.obert
        request = self.request

        print("\n❌ Verificando restricciones del rol OG3-Membre a las actas en "
              "órgano obert")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(username=TEST_USER_ID, obj=root_path, roles=['OG3-Membre'])
        # START check sessio PLANIFICADA
        with self.assertRaises(Unauthorized):
            root_path.planificada.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            root_path.planificada.acta.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            display_file = DisplayFile(root_path.planificada.acta, request)
            display_file.publishTraverse(request, 'file')()
        with self.assertRaises(Unauthorized):
            download = Download(root_path.planificada.acta, request)
            download.publishTraverse(request, 'file')()
        with self.assertRaises(Unauthorized):
            root_path.planificada.acta.audio.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            display_file = DisplayFile(root_path.planificada.acta.audio, request)
            display_file.publishTraverse(request, 'file')()
        with self.assertRaises(Unauthorized):
            download = Download(root_path.planificada.acta.audio, request)
            download.publishTraverse(request, 'file')()
        print("  ✓ Acceso denegado correctamente a actas en sesión PLANIFICADA")

        # START check sessio CONVOCADA
        # OG3-Membre puede ver actas y acceder a archivos en CONVOCADA
        view = root_path.convocada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.convocada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.convocada.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.convocada.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.convocada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.convocada.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.convocada.acta.audio,
                        request).publishTraverse(request, 'file')())
        print("  ✓ Acceso permitido a actas y archivos en sesión CONVOCADA")

        # START check sessio REALITZADA
        # OG3-Membre puede ver actas y acceder a archivos en REALITZADA
        view = root_path.realitzada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.realitzada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.realitzada.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.realitzada.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.realitzada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.realitzada.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.realitzada.acta.audio,
                        request).publishTraverse(request, 'file')())
        print("  ✓ Acceso permitido a actas y archivos en sesión REALITZADA")

        # START check sessio TANCADA
        # OG3-Membre puede ver actas y acceder a archivos en TANCADA
        view = root_path.tancada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.tancada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.tancada.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.tancada.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.tancada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.tancada.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(
            Download(root_path.tancada.acta.audio, request).publishTraverse(
                request, 'file')())
        print("  ✓ Acceso permitido a actas y archivos en sesión TANCADA")

        # START check sessio EN CORRECCIO
        # OG3-Membre puede ver actas y acceder a archivos en EN_CORRECCIO
        view = root_path.correccio.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.correccio.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.correccio.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.correccio.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.correccio.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.correccio.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.correccio.acta.audio,
                        request).publishTraverse(request, 'file')())
        print("  ✓ Acceso permitido a actas y archivos en sesión EN CORRECCIO")

    def test_organ_obert_view_actes_as_afectat(self):
        """Test as OG4-Afectat Actes i Audios"""
        logout()
        root_path = self.portal.ca.testingfolder.obert
        request = self.request

        print("\n❌ Verificando restricciones del rol OG4-Afectat a las actas en "
              "órgano obert")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(username=TEST_USER_ID, obj=root_path,
                             roles=['OG4-Afectat'])
        # START check sessio PLANIFICADA
        with self.assertRaises(Unauthorized):
            root_path.planificada.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            root_path.planificada.acta.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            display_file = DisplayFile(root_path.planificada.acta, request)
            display_file.publishTraverse(request, 'file')()
        with self.assertRaises(Unauthorized):
            download = Download(root_path.planificada.acta, request)
            download.publishTraverse(request, 'file')()
        with self.assertRaises(Unauthorized):
            root_path.planificada.acta.audio.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            display_file = DisplayFile(root_path.planificada.acta.audio, request)
            display_file.publishTraverse(request, 'file')()
        with self.assertRaises(Unauthorized):
            download = Download(root_path.planificada.acta.audio, request)
            download.publishTraverse(request, 'file')()
        print("  ✓ Acceso denegado correctamente a actas en sesión PLANIFICADA")

        # START check sessio CONVOCADA
        # OG4-Afectat puede ver sesión pero no actas en estado CONVOCADA
        self.assertTrue(root_path.convocada.restrictedTraverse('view')())
        with self.assertRaises(Unauthorized):
            root_path.convocada.acta.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.convocada.acta, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.convocada.acta, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            root_path.convocada.acta.audio.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.convocada.acta.audio, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.convocada.acta.audio, request).publishTraverse(
                request, 'file')()
        print("  ✓ Acceso denegado correctamente a actas en sesión CONVOCADA")

        # START check sessio REALITZADA
        # OG4-Afectat puede ver sesión pero no actas en estado REALITZADA
        self.assertTrue(root_path.realitzada.restrictedTraverse('view')())
        with self.assertRaises(Unauthorized):
            root_path.realitzada.acta.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.realitzada.acta, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.realitzada.acta, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            root_path.realitzada.acta.audio.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.realitzada.acta.audio, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.realitzada.acta.audio, request).publishTraverse(
                request, 'file')()
        print("  ✓ Acceso denegado correctamente a actas en sesión REALITZADA")

        # START check sessio TANCADA
        # OG4-Afectat puede ver actas y acceder a archivos en estado TANCADA
        view = root_path.tancada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.tancada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.tancada.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.tancada.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.tancada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.tancada.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(
            Download(root_path.tancada.acta.audio, request).publishTraverse(
                request, 'file')())
        print("  ✓ Acceso permitido a actas y archivos en sesión TANCADA")

        # START check sessio EN CORRECCIO
        # OG4-Afectat puede ver sesión pero no actas en estado EN CORRECCIO
        self.assertTrue(root_path.correccio.restrictedTraverse('view')())
        with self.assertRaises(Unauthorized):
            root_path.correccio.acta.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.correccio.acta, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.correccio.acta, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            root_path.correccio.acta.audio.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            DisplayFile(
                root_path.correccio.acta.audio, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            Download(
                root_path.correccio.acta.audio, request).publishTraverse(
                request, 'file')()
        print("  ✓ Acceso denegado correctamente a actas en sesión EN CORRECCIO")

    def test_organ_obert_view_actes_as_convidat(self):
        """Test as OG5-Convidat Actes i Audios"""
        logout()
        root_path = self.portal.ca.testingfolder.obert
        request = self.request

        print("\n❌ Verificando restricciones del rol OG5-Convidat a las actas en "
              "órgano obert")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(username=TEST_USER_ID, obj=root_path,
                             roles=['OG5-Convidat'])
        # START check sessio PLANIFICADA
        with self.assertRaises(Unauthorized):
            root_path.planificada.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            root_path.planificada.acta.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            display_file = DisplayFile(root_path.planificada.acta, request)
            display_file.publishTraverse(request, 'file')()
        with self.assertRaises(Unauthorized):
            download = Download(root_path.planificada.acta, request)
            download.publishTraverse(request, 'file')()
        with self.assertRaises(Unauthorized):
            root_path.planificada.acta.audio.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            display_file = DisplayFile(root_path.planificada.acta.audio, request)
            display_file.publishTraverse(request, 'file')()
        with self.assertRaises(Unauthorized):
            download = Download(root_path.planificada.acta.audio, request)
            download.publishTraverse(request, 'file')()
        print("  ✓ Acceso denegado correctamente a actas en sesión PLANIFICADA")

        # START check sessio CONVOCADA
        # OG5-Convidat puede ver actas y acceder a archivos en CONVOCADA
        view = root_path.convocada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.convocada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.convocada.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.convocada.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.convocada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.convocada.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.convocada.acta.audio,
                        request).publishTraverse(request, 'file')())
        print("  ✓ Acceso permitido a actas y archivos en sesión CONVOCADA")

        # START check sessio REALITZADA
        # OG5-Convidat puede ver actas y acceder a archivos en REALITZADA
        view = root_path.realitzada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.realitzada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.realitzada.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.realitzada.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.realitzada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.realitzada.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.realitzada.acta.audio,
                        request).publishTraverse(request, 'file')())
        print("  ✓ Acceso permitido a actas y archivos en sesión REALITZADA")

        # START check sessio TANCADA
        # OG5-Convidat puede ver actas y acceder a archivos en TANCADA
        view = root_path.tancada.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.tancada.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.tancada.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.tancada.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.tancada.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.tancada.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(
            Download(root_path.tancada.acta.audio, request).publishTraverse(
                request, 'file')())
        print("  ✓ Acceso permitido a actas y archivos en sesión TANCADA")

        # START check sessio EN CORRECCIO
        # OG5-Convidat puede ver actas y acceder a archivos en EN_CORRECCIO
        view = root_path.correccio.restrictedTraverse('view')
        self.assertTrue(view())
        view = root_path.correccio.acta.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(
            DisplayFile(root_path.correccio.acta, request).publishTraverse(
                request, 'file')())
        self.assertTrue(
            Download(root_path.correccio.acta, request).publishTraverse(
                request, 'file')())
        view = root_path.correccio.acta.audio.restrictedTraverse('view')
        self.assertTrue(view())
        self.assertTrue(DisplayFile(root_path.correccio.acta.audio,
                        request).publishTraverse(request, 'file')())
        self.assertTrue(Download(root_path.correccio.acta.audio,
                        request).publishTraverse(request, 'file')())
        print("  ✓ Acceso permitido a actas y archivos en sesión EN CORRECCIO")
