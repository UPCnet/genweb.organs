# -*- coding: utf-8 -*-
"""Tests de permisos de actas en órganos restringidos a afectados.

Basado en: https://serveistic.upc.edu/ca/organs-de-govern/documentacio/permisos-organ-restringit-a-afectats

PERMISOS DE ACTAS, AUDIOS y ANNEX en órganos restricted_to_affected_organ:
- PLANIFICADA: Solo OG1-Secretari, OG2-Editor (sin OG3-Membre, OG4-Afectat, OG5-Convidat, anónimos)
- CONVOCADA: OG1-Secretari, OG2-Editor, OG3-Membre, OG5-Convidat (sin OG4-Afectat, anónimos)
- REALITZADA: OG1-Secretari, OG2-Editor, OG3-Membre, OG5-Convidat (sin OG4-Afectat, anónimos)
- TANCADA: OG1-Secretari, OG2-Editor, OG3-Membre, OG5-Convidat (sin OG4-Afectat, anónimos)
- EN_CORRECCIO: OG1-Secretari, OG2-Editor, OG3-Membre, OG5-Convidat (sin OG4-Afectat, anónimos)

NOTA: OG4-Afectat nunca tiene acceso a actas/audios en este tipo de órgano
"""
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


class OrgansAfectatsActesFunctionalTestCase(unittest.TestCase):
    """Tests funcionales para actas en órganos restringidos a afectados."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        """Configuración inicial del test."""
        # Suprimir warnings molestos
        warnings.filterwarnings("ignore", category=ResourceWarning,
                                message=".*unclosed file.*")
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

        # Create Restricted to Affected Organ structure
        organ = api.content.create(
            type='genweb.organs.organgovern',
            id='afectats',
            title='Organ TEST restringit a AFECTATS',
            container=og_unit,
            safe_id=True
        )
        organ.acronim = 'OG.AFECTATS'
        organ.organType = 'restricted_to_affected_organ'

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
                type='genweb.organs.acta',
                id='acta',
                title='Acta de la sessió',
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

    def test_organ_afectats_view_actes_as_secretari(self):
        """Test permisos de OG1-Secretari sobre actas en órgano afectats."""
        print("\n✅ Verificando permisos del rol OG1-Secretari en órgano afectats")

        logout()
        root_path = self.portal.ca.testingfolder.afectats
        request = self.request

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=root_path,
            roles=['OG1-Secretari']
        )

        # OG1-Secretari tiene acceso en todos los estados
        for session_state in [
                'planificada', 'convocada', 'realitzada', 'tancada', 'correccio']:
            print(f"  ✓ Verificando acceso en sesión {session_state.upper()}")
            session = getattr(root_path, session_state)

            self.assertTrue(session.restrictedTraverse('view')())
            self.assertTrue(session.acta.restrictedTraverse('view')())
            self.assertTrue(
                DisplayFile(session.acta, request).publishTraverse(request, 'file')())
            self.assertTrue(
                Download(session.acta, request).publishTraverse(request, 'file')())
            self.assertTrue(session.acta.audio.restrictedTraverse('view')())
            self.assertTrue(
                DisplayFile(session.acta.audio, request).publishTraverse(
                    request, 'file')())
            self.assertTrue(
                Download(session.acta.audio, request).publishTraverse(
                    request, 'file')())

            print(f"  ✓ Acceso correcto en sesión {session_state.upper()}")

        print("  ✓ Verificación completa como OG1-Secretari")
        logout()

    def test_organ_afectats_view_actes_as_editor(self):
        """Test permisos de OG2-Editor sobre actas en órgano afectats."""
        print("\n✅ Verificando permisos del rol OG2-Editor en órgano afectats")

        logout()
        root_path = self.portal.ca.testingfolder.afectats
        request = self.request

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=root_path,
            roles=['OG2-Editor']
        )

        # OG2-Editor tiene acceso en todos los estados
        for session_state in [
                'planificada', 'convocada', 'realitzada', 'tancada', 'correccio']:
            print(f"  ✓ Verificando acceso en sesión {session_state.upper()}")
            session = getattr(root_path, session_state)

            self.assertTrue(session.restrictedTraverse('view')())
            self.assertTrue(session.acta.restrictedTraverse('view')())
            self.assertTrue(
                DisplayFile(session.acta, request).publishTraverse(request, 'file')())
            self.assertTrue(
                Download(session.acta, request).publishTraverse(request, 'file')())
            self.assertTrue(session.acta.audio.restrictedTraverse('view')())
            self.assertTrue(
                DisplayFile(session.acta.audio, request).publishTraverse(
                    request, 'file')())
            self.assertTrue(
                Download(session.acta.audio, request).publishTraverse(
                    request, 'file')())

            print(f"  ✓ Acceso correcto en sesión {session_state.upper()}")

        print("  ✓ Verificación completa como OG2-Editor")
        logout()

    def test_organ_afectats_view_actes_as_membre(self):
        """Test permisos de OG3-Membre sobre actas en órgano afectats."""
        print("\n❌ Verificando restricciones del rol OG3-Membre en órgano afectats")

        logout()
        root_path = self.portal.ca.testingfolder.afectats
        request = self.request

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=root_path,
            roles=['OG3-Membre']
        )

        # START check sessio PLANIFICADA - Sin acceso
        print("  ✓ Verificando restricciones en sesión PLANIFICADA")
        with self.assertRaises(Unauthorized):
            root_path.planificada.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            root_path.planificada.acta.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.planificada.acta, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            Download(root_path.planificada.acta, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            root_path.planificada.acta.audio.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.planificada.acta.audio, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            Download(root_path.planificada.acta.audio, request).publishTraverse(
                request, 'file')()
        print("  ✓ Acceso denegado correctamente en sesión PLANIFICADA")

        # Estados CONVOCADA, REALITZADA, TANCADA, EN_CORRECCIO - Tiene acceso
        for session_state in ['convocada', 'realitzada', 'tancada', 'correccio']:
            print(f"  ✓ Verificando acceso permitido en sesión {session_state.upper()}")
            session = getattr(root_path, session_state)

            self.assertTrue(session.restrictedTraverse('view')())
            self.assertTrue(session.acta.restrictedTraverse('view')())
            self.assertTrue(
                DisplayFile(session.acta, request).publishTraverse(request, 'file')())
            self.assertTrue(
                Download(session.acta, request).publishTraverse(request, 'file')())
            self.assertTrue(session.acta.audio.restrictedTraverse('view')())
            self.assertTrue(
                DisplayFile(session.acta.audio, request).publishTraverse(
                    request, 'file')())
            self.assertTrue(
                Download(session.acta.audio, request).publishTraverse(
                    request, 'file')())

            print(f"  ✓ Acceso permitido en sesión {session_state.upper()}")

        print("  ✓ Verificación completa como OG3-Membre")
        logout()

    def test_organ_afectats_view_actes_as_afectat(self):
        """Test restricciones de OG4-Afectat sobre actas en órgano afectats."""
        print("\n❌ Verificando restricciones del rol OG4-Afectat en órgano afectats")

        logout()
        root_path = self.portal.ca.testingfolder.afectats
        request = self.request

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=root_path,
            roles=['OG4-Afectat']
        )

        # OG4-Afectat NO tiene acceso a actas/audios en ningún estado
        # Pero puede ver la sesión en algunos estados
        for session_state in [
                'planificada', 'convocada', 'realitzada', 'tancada', 'correccio']:
            print(f"  ✓ Verificando restricciones en sesión {session_state.upper()}")
            session = getattr(root_path, session_state)

            # No puede ver actas
            with self.assertRaises(Unauthorized):
                session.acta.restrictedTraverse('view')()
            with self.assertRaises(Unauthorized):
                DisplayFile(session.acta, request).publishTraverse(request, 'file')()
            with self.assertRaises(Unauthorized):
                Download(session.acta, request).publishTraverse(request, 'file')()

            # No puede ver audios
            with self.assertRaises(Unauthorized):
                session.acta.audio.restrictedTraverse('view')()
            with self.assertRaises(Unauthorized):
                DisplayFile(
                    session.acta.audio, request).publishTraverse(
                    request, 'file')()
            with self.assertRaises(Unauthorized):
                Download(session.acta.audio, request).publishTraverse(request, 'file')()

            print(
                f"  ✓ Acceso denegado correctamente a actas/audios en sesión {session_state.upper()}")

        print("  ✓ Verificación completa como OG4-Afectat (sin acceso a actas/audios)")
        logout()

    def test_organ_afectats_view_actes_as_convidat(self):
        """Test permisos de OG5-Convidat sobre actas en órgano afectats."""
        print("\n❌ Verificando restricciones del rol OG5-Convidat en órgano afectats")

        logout()
        root_path = self.portal.ca.testingfolder.afectats
        request = self.request

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=root_path,
            roles=['OG5-Convidat']
        )

        # START check sessio PLANIFICADA - Sin acceso
        print("  ✓ Verificando restricciones en sesión PLANIFICADA")
        with self.assertRaises(Unauthorized):
            root_path.planificada.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            root_path.planificada.acta.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.planificada.acta, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            Download(root_path.planificada.acta, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            root_path.planificada.acta.audio.restrictedTraverse('view')()
        with self.assertRaises(Unauthorized):
            DisplayFile(root_path.planificada.acta.audio, request).publishTraverse(
                request, 'file')()
        with self.assertRaises(Unauthorized):
            Download(root_path.planificada.acta.audio, request).publishTraverse(
                request, 'file')()
        print("  ✓ Acceso denegado correctamente en sesión PLANIFICADA")

        # Estados CONVOCADA, REALITZADA, TANCADA, EN_CORRECCIO - Tiene acceso
        for session_state in ['convocada', 'realitzada', 'tancada', 'correccio']:
            print(f"  ✓ Verificando acceso permitido en sesión {session_state.upper()}")
            session = getattr(root_path, session_state)

            self.assertTrue(session.restrictedTraverse('view')())
            self.assertTrue(session.acta.restrictedTraverse('view')())
            self.assertTrue(
                DisplayFile(session.acta, request).publishTraverse(request, 'file')())
            self.assertTrue(
                Download(session.acta, request).publishTraverse(request, 'file')())
            self.assertTrue(session.acta.audio.restrictedTraverse('view')())
            self.assertTrue(
                DisplayFile(session.acta.audio, request).publishTraverse(
                    request, 'file')())
            self.assertTrue(
                Download(session.acta.audio, request).publishTraverse(
                    request, 'file')())

            print(f"  ✓ Acceso permitido en sesión {session_state.upper()}")

        print("  ✓ Verificación completa como OG5-Convidat")
        logout()
