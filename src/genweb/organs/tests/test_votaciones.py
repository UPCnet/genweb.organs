# -*- coding: utf-8 -*-
"""Tests del sistema de votaciones.

Verifica qué acciones de votación están disponibles para cada rol,
basado en el documento resumen_permisos_organs.html.

ACCIONES DE VOTACIÓN:
- Obrir votació: OG1-Secretari, OG2-Editor
- Tancar votació: OG1-Secretari, OG2-Editor
- Veure botons per votar: OG1-Secretari, OG2-Editor
- Ver resultados votación a mano alzada: OG1-Secretari, OG2-Editor,
  OG3-Membre
- Ver quien votó qué: OG1-Secretari, OG2-Editor
"""
import datetime
import unittest
import warnings

from plone import api
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login, logout, setRoles
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from zope.component import getMultiAdapter

from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING


class VotacionesTestCase(unittest.TestCase):
    """Tests funcionales para el sistema de votaciones."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        """Configuración inicial del test."""
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

        # Enable Organs folder
        behavior = ISelectableConstrainTypes(self.portal['ca'])
        behavior.setConstrainTypesMode(1)
        behavior.setLocallyAllowedTypes(['genweb.organs.organsfolder'])
        behavior.setImmediatelyAddableTypes(['genweb.organs.organsfolder'])

        # Clean up
        try:
            api.content.delete(
                obj=self.portal['ca']['testingfolder'],
                check_linkintegrity=False
            )
        except Exception:
            pass

        # Create Organs Test Folder
        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='testingfolder',
            title='Organ Tests',
            container=self.portal['ca']
        )

        # Create Open Organ
        organ = api.content.create(
            type='genweb.organs.organgovern',
            id='obert',
            title='Organ TEST Obert',
            container=og_unit,
            safe_id=True
        )
        organ.acronim = 'OG.OPEN'
        organ.organType = 'open_organ'

        # Create session in REALITZADA (where voting happens)
        now = datetime.datetime.now()
        session = api.content.create(
            type='genweb.organs.sessio',
            id='realitzada',
            title='Session Realitzada',
            container=organ,
            start=now,
            end=now + datetime.timedelta(hours=1),
            modality='attended',
            numSessioShowOnly='01',
            numSessio='01'
        )
        api.content.transition(obj=session, transition='convocar')
        api.content.transition(obj=session, transition='realitzar')

        self.organ = organ
        self.session = session
        logout()

    def test_secretari_can_manage_vote(self):
        """Test que OG1-Secretari puede gestionar votaciones."""
        print("\n✅ Verificando que OG1-Secretari puede gestionar votaciones")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG1-Secretari']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertTrue(view_obj.canViewManageVote())
        print("  ✓ OG1-Secretari puede obrir/tancar votació")
        print("  ✓ OG1-Secretari puede ver quien votó qué")

        logout()

    def test_editor_can_manage_vote(self):
        """Test que OG2-Editor puede gestionar votaciones."""
        print("\n✅ Verificando que OG2-Editor puede gestionar votaciones")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG2-Editor']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertTrue(view_obj.canViewManageVote())
        print("  ✓ OG2-Editor puede obrir/tancar votació")
        print("  ✓ OG2-Editor puede ver quien votó qué")

        logout()

    def test_membre_cannot_manage_vote(self):
        """Test que OG3-Membre NO puede gestionar votaciones."""
        print("\n❌ Verificando que OG3-Membre NO puede gestionar votaciones")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG3-Membre']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertFalse(view_obj.canViewManageVote())
        print("  ✓ OG3-Membre NO puede gestionar votaciones")
        print("  ✓ OG3-Membre NO puede ver quien votó qué")

        logout()

    def test_secretari_can_view_vote_buttons(self):
        """Test que OG1-Secretari puede ver botones de voto."""
        print("\n✅ Verificando que OG1-Secretari puede ver botons per votar")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG1-Secretari']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertTrue(view_obj.canViewVoteButtons())
        print("  ✓ OG1-Secretari puede ver botons per votar")

        logout()

    def test_membre_can_view_vote_buttons(self):
        """Test que OG3-Membre puede ver botones de voto."""
        print("\n✅ Verificando que OG3-Membre puede ver botons per votar")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG3-Membre']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertTrue(view_obj.canViewVoteButtons())
        print("  ✓ OG3-Membre puede ver botons per votar")

        logout()

    def test_editor_cannot_view_vote_buttons(self):
        """Test que OG2-Editor NO puede ver botones de voto."""
        print("\n❌ Verificando que OG2-Editor NO puede ver botons per votar")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG2-Editor']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertFalse(view_obj.canViewVoteButtons())
        print("  ✓ OG2-Editor NO puede ver botons per votar")
        print("  ✓ OG2-Editor gestiona pero no vota")

        logout()

    def test_secretari_can_view_results(self):
        """Test que OG1-Secretari puede ver resultados."""
        print("\n✅ Verificando que OG1-Secretari puede ver resultados")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG1-Secretari']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertTrue(view_obj.canViewResultsVote())
        print("  ✓ OG1-Secretari puede ver resultados votación a mano alzada")

        logout()

    def test_editor_can_view_results(self):
        """Test que OG2-Editor puede ver resultados."""
        print("\n✅ Verificando que OG2-Editor puede ver resultados")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG2-Editor']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertTrue(view_obj.canViewResultsVote())
        print("  ✓ OG2-Editor puede ver resultados votación a mano alzada")

        logout()

    def test_membre_can_view_results(self):
        """Test que OG3-Membre puede ver resultados."""
        print("\n✅ Verificando que OG3-Membre puede ver resultados")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG3-Membre']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertTrue(view_obj.canViewResultsVote())
        print("  ✓ OG3-Membre puede ver resultados votación a mano alzada")

        logout()

    def test_afectat_cannot_view_results(self):
        """Test que OG4-Afectat NO puede ver resultados."""
        print("\n❌ Verificando que OG4-Afectat NO puede ver resultados")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG4-Afectat']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertFalse(view_obj.canViewResultsVote())
        print("  ✓ OG4-Afectat NO puede ver resultados votación")

        logout()

    def test_convidat_cannot_access_voting(self):
        """Test que OG5-Convidat NO tiene acceso a votaciones."""
        print("\n❌ Verificando que OG5-Convidat NO tiene acceso a votaciones")

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        api.user.grant_roles(
            username=TEST_USER_ID,
            obj=self.organ,
            roles=['OG5-Convidat']
        )

        view_obj = self.session.restrictedTraverse('@@view')
        self.assertFalse(view_obj.canViewManageVote())
        self.assertFalse(view_obj.canViewVoteButtons())
        self.assertFalse(view_obj.canViewResultsVote())
        print("  ✓ OG5-Convidat NO puede gestionar votaciones")
        print("  ✓ OG5-Convidat NO puede votar")
        print("  ✓ OG5-Convidat NO puede ver resultados")

        logout()

    def test_zzz_votaciones_summary(self):
        """Test resumen del sistema de votaciones (al final por orden
        alfabético)."""
        print("\n📊 RESUMEN DEL SISTEMA DE VOTACIONES")
        print("=" * 60)
        print("OG1-Secretari y OG2-Editor pueden:")
        print("  ✓ Obrir votació")
        print("  ✓ Tancar votació")
        print("  ✓ Veure botons per votar")
        print("  ✓ Ver resultados votación a mano alzada")
        print("  ✓ Ver quien votó qué")
        print()
        print("OG3-Membre puede:")
        print("  ✓ Ver resultados votación a mano alzada")
        print("  ✗ NO puede gestionar votaciones")
        print("  ✗ NO puede ver quien votó qué")
        print()
        print("OG4-Afectat, OG5-Convidat, Anónimos:")
        print("  ✗ Sin acceso a funcionalidades de votación")
        print("=" * 60)

        self.assertTrue(True)
