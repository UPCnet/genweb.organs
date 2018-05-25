# -*- coding: utf-8 -*-
# from plone.app.testing import ROBOT_TEST_LEVEL
from plone.testing import layered
from genweb.organs.testing import GENWEB_ORGANS_ACCEPTANCE_TESTING

import os
import robotsuite
import unittest


def setUP(testCase=None):
    # Inicializar el entorno de pruebas
    pass


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
