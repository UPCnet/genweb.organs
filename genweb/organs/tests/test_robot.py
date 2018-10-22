# -*- coding: utf-8 -*-
# from plone.app.testing import ROBOT_TEST_LEVEL
from plone.testing import layered
from genweb.organs.testing import GENWEB_ORGANS_ACCEPTANCE_TESTING
from genweb.organs.testing import GENWEB_ORGANS_INTEGRATION_TESTING
from zope.component import getMultiAdapter
# from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import login, logout
from plone.app.testing import setRoles
# from genweb.core.adapters import IImportant
# from transaction import commit
# from plone import api
from genweb.organs.browser import tools

import os
import robotsuite
import unittest


def setUP(self):
    # Inicializar el entorno de pruebas
    self.app = self.layer['app']
    self.portal = self.layer['portal']
    self.request = self.layer['request']

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
    from plone import api
    api.content.create(
        type='genweb.organs.organsfolder',
        id='testingfolder',
        title='Organ Tests',
        container=self.portal['ca'])


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in os.listdir(robot_dir)
        if doc.endswith('.robot') and doc.startswith('test_')
    ]

    for robot_test in robot_tests:
        robottestsuite = robotsuite.RobotTestSuite(robot_test, setUp=setUP)
        # robottestsuite.level = ROBOT_TEST_LEVEL
        suite.addTests([
            layered(
                robottestsuite,
                layer=GENWEB_ORGANS_ACCEPTANCE_TESTING,
            ),
        ])

    return suite
