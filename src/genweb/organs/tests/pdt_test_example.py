# -*- coding: utf-8 -*-
import unittest
from plone.app.testing import TEST_USER_ID, setRoles, login, logout
from plone.api.env import adopt_roles
from genweb.organs.testing import GENWEB_ORGANS_INTEGRATION_TESTING
from AccessControl import Unauthorized
from plone import api


class TestOrgansSetup(unittest.TestCase):

    layer = GENWEB_ORGANS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        # Asignar rol Manager al usuario de test
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_ID)

    def tearDown(self):
        logout()

    def test_portal_title(self):
        # Comprobamos el título del portal
        self.assertIn('Plone site', self.portal.Title())

    def test_create_content_with_roles(self):
        # Crear contenido como Manager
        with adopt_roles(['Manager']):
            folder = api.content.create(
                type='Folder',
                id='folder_test',
                title='Folder Test',
                container=self.portal
            )
            self.assertIsNotNone(folder)

        # Probar Unauthorized para otro rol
        with self.assertRaises(Unauthorized):
            with adopt_roles(['Member']):
                api.content.create(
                    type='Folder',
                    id='folder_fail',
                    title='Folder Fail',
                    container=self.portal
                )
