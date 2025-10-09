# -*- coding: utf-8 -*-
"""Functional tests for acta permissions in different organ types."""
import unittest
from plone import api
from genweb.organs.tests.base import FunctionalTestCase


class TestActaPermissionsOpenOrgans(FunctionalTestCase):
    """Test acta permissions in open organs."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.organ = self.portal.ca.testingfolder.obert
        self.session = self.organ.planificada

    def test_acta_permissions_secretari(self):
        """Test acta permissions for Secretari role in open organs."""
        self.login_as_secretari()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta',
            title='Test Acta'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_editor(self):
        """Test acta permissions for Editor role in open organs."""
        self.login_as_editor()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_editor',
            title='Test Acta Editor'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_membre(self):
        """Test acta permissions for Membre role in open organs."""
        self.login_as_membre()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_membre',
            title='Test Acta Membre'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_afectat(self):
        """Test acta permissions for Afectat role in open organs."""
        self.login_as_afectat()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_afectat',
            title='Test Acta Afectat'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_convidat(self):
        """Test acta permissions for Convidat role in open organs."""
        self.login_as_convidat()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_convidat',
            title='Test Acta Convidat'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()


class TestActaPermissionsMembersOrgans(FunctionalTestCase):
    """Test acta permissions in members-only organs."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.organ = self.portal.ca.testingfolder.membres
        self.session = self.organ.planificada

    def test_acta_permissions_secretari(self):
        """Test acta permissions for Secretari role in members organs."""
        self.login_as_secretari()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta',
            title='Test Acta'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_editor(self):
        """Test acta permissions for Editor role in members organs."""
        self.login_as_editor()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_editor',
            title='Test Acta Editor'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_membre(self):
        """Test acta permissions for Membre role in members organs."""
        self.login_as_membre()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_membre',
            title='Test Acta Membre'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_afectat(self):
        """Test acta permissions for Afectat role in members organs."""
        self.login_as_afectat()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_afectat',
            title='Test Acta Afectat'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_convidat(self):
        """Test acta permissions for Convidat role in members organs."""
        self.login_as_convidat()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_convidat',
            title='Test Acta Convidat'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()


class TestActaPermissionsAffectedOrgans(FunctionalTestCase):
    """Test acta permissions in affected-only organs."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.organ = self.portal.ca.testingfolder.afectats
        self.session = self.organ.planificada

    def test_acta_permissions_secretari(self):
        """Test acta permissions for Secretari role in affected organs."""
        self.login_as_secretari()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta',
            title='Test Acta'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_editor(self):
        """Test acta permissions for Editor role in affected organs."""
        self.login_as_editor()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_editor',
            title='Test Acta Editor'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_membre(self):
        """Test acta permissions for Membre role in affected organs."""
        self.login_as_membre()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_membre',
            title='Test Acta Membre'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_afectat(self):
        """Test acta permissions for Afectat role in affected organs."""
        self.login_as_afectat()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_afectat',
            title='Test Acta Afectat'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()

    def test_acta_permissions_convidat(self):
        """Test acta permissions for Convidat role in affected organs."""
        self.login_as_convidat()

        # Should be able to create actas
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            self.session,
            id='test_acta_convidat',
            title='Test Acta Convidat'
        )

        # Should be able to view actas
        self.assertTrue(api.content.get_state(acta))

        self.logout()
