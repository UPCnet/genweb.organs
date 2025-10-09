# -*- coding: utf-8 -*-
"""Functional tests for file permissions in different organ types."""
import unittest
from plone import api
from genweb.organs.tests.base import FunctionalTestCase


class TestFilePermissionsOpenOrgans(FunctionalTestCase):
    """Test file permissions in open organs."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.organ = self.portal.ca.testingfolder.obert
        self.session = self.organ.planificada

    def test_file_permissions_secretari(self):
        """Test file permissions for Secretari role in open organs."""
        self.login_as_secretari()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file',
            title='Test File'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_editor(self):
        """Test file permissions for Editor role in open organs."""
        self.login_as_editor()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_editor',
            title='Test File Editor'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_membre(self):
        """Test file permissions for Membre role in open organs."""
        self.login_as_membre()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_membre',
            title='Test File Membre'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_afectat(self):
        """Test file permissions for Afectat role in open organs."""
        self.login_as_afectat()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_afectat',
            title='Test File Afectat'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_convidat(self):
        """Test file permissions for Convidat role in open organs."""
        self.login_as_convidat()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_convidat',
            title='Test File Convidat'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()


class TestFilePermissionsMembersOrgans(FunctionalTestCase):
    """Test file permissions in members-only organs."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.organ = self.portal.ca.testingfolder.membres
        self.session = self.organ.planificada

    def test_file_permissions_secretari(self):
        """Test file permissions for Secretari role in members organs."""
        self.login_as_secretari()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file',
            title='Test File'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_editor(self):
        """Test file permissions for Editor role in members organs."""
        self.login_as_editor()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_editor',
            title='Test File Editor'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_membre(self):
        """Test file permissions for Membre role in members organs."""
        self.login_as_membre()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_membre',
            title='Test File Membre'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_afectat(self):
        """Test file permissions for Afectat role in members organs."""
        self.login_as_afectat()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_afectat',
            title='Test File Afectat'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_convidat(self):
        """Test file permissions for Convidat role in members organs."""
        self.login_as_convidat()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_convidat',
            title='Test File Convidat'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()


class TestFilePermissionsAffectedOrgans(FunctionalTestCase):
    """Test file permissions in affected-only organs."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.organ = self.portal.ca.testingfolder.afectats
        self.session = self.organ.planificada

    def test_file_permissions_secretari(self):
        """Test file permissions for Secretari role in affected organs."""
        self.login_as_secretari()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file',
            title='Test File'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_editor(self):
        """Test file permissions for Editor role in affected organs."""
        self.login_as_editor()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_editor',
            title='Test File Editor'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_membre(self):
        """Test file permissions for Membre role in affected organs."""
        self.login_as_membre()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_membre',
            title='Test File Membre'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_afectat(self):
        """Test file permissions for Afectat role in affected organs."""
        self.login_as_afectat()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_afectat',
            title='Test File Afectat'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()

    def test_file_permissions_convidat(self):
        """Test file permissions for Convidat role in affected organs."""
        self.login_as_convidat()

        # Should be able to create files
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            self.session,
            id='test_file_convidat',
            title='Test File Convidat'
        )

        # Should be able to view files
        self.assertTrue(api.content.get_state(file_obj))

        self.logout()
