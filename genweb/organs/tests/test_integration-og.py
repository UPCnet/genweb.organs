import unittest2 as unittest
from genweb.organs.testing import FUNCTIONAL_TESTING
from zope.component import getMultiAdapter
from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import login, logout
from plone.app.testing import setRoles
from genweb.core.adapters import IImportant
from transaction import commit


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
