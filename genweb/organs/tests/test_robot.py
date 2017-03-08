from genweb.organs.testing import FunctionalTestCase
from plone.testing import layered
import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("robot_test.txt"),
                layer=FunctionalTestCase),
        layered(robotsuite.RobotTestSuite("robot_hello_world.txt"),
                layer=FunctionalTestCase)
    ])
    return suite
