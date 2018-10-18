# import unittest
from genweb.organs.testing import GENWEB_ORGANS_INTEGRATION_TESTING
from zope.component import getMultiAdapter
# from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import login, logout
from plone.app.testing import setRoles
# from genweb.core.adapters import IImportant
# from transaction import commit
# from plone import api
from genweb.organs.tests import organsTestBase
from genweb.organs.browser import tools


class IntegrationTestCase(organsTestBase):
    """Base class for integration tests."""

    layer = GENWEB_ORGANS_INTEGRATION_TESTING

    def setUp(self):
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

        # Create Base folder
        from plone import api
        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='test-og',
            title='Organ Tests',
            container=self.portal['ca'])

        tools.create_organ_content(og_unit, 'open_organ', 'OG.OPEN', 'Organ TEST Obert', 'obert')

        logout()

    # def createAllOrgans(self):
    #     # Creates GW ca/es/en default structure
    #     setRoles(self.portal, TEST_USER_ID, ['Manager'])
    #     login(self.portal, TEST_USER_NAME)
    #     commit()
    #     logout()

    # def openBrowserURL(self, browser, url):
    #     portalURL = self.portal.absolute_url()
    #     self.loginBrowser(browser, portalURL)
    #     browser.open(portalURL + url)

    def test_create_organ_as_manager(self):
        """ Install all kind of Organs
        """
        username = 'usuari.manager'
        login(self.portal, username)
        # TODO
        self.portal.ca['test-og'].obert.planificada.punt

    # def test_create_organ_as_editor(self):
    #     """ Install all kind of Organs
    #     """
    #     username = 'usuari.editor'
    #     login(self.portal, username)
    #     self.create_organ(organ_type="Closed")
