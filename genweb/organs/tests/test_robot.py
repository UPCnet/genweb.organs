import unittest
import robotsuite

from genweb.organs.testing import GENWEB_ORGANS_ROBOT_TESTING
from plone.testing import layered


def setUP(testCase=None):
    # Inicializar el entorno de pruebas
    pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite(
                './robot/test_plone_is_installed.robot',
                setUp=setUP
            ),
            layer=GENWEB_ORGANS_ROBOT_TESTING
        ),
        layered(robotsuite.RobotTestSuite(
                './robot/tests_og_restricted_to_members.robot',
                setUp=setUP
            ),
            layer=GENWEB_ORGANS_ROBOT_TESTING
        ),
        layered(robotsuite.RobotTestSuite(
                './robot/tests_og_restricted_to_affecteds.robot',
                setUp=setUP
            ),
            layer=GENWEB_ORGANS_ROBOT_TESTING
        ),
    ])
    return suite
