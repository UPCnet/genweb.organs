import unittest2 as unittest
from genweb.organs.testing import INTEGRATION_TESTING
from zope.component import getMultiAdapter
from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import login, logout
from plone.app.testing import setRoles
from genweb.core.adapters import IImportant
from transaction import commit


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def createDefaultDirectories(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        setupview = getMultiAdapter((self.portal, self.request), name='setup-view')
        setupview.apply_default_language_settings()
        setupview.setup_multilingual()
        setupview.createContent('n4')
        commit()
        logout()

    def loginBrowser(self, browser, portalURL):
        browser.open(portalURL + "/login_form")
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()

    def openBrowserURL(self, browser, url):
        portalURL = self.portal.absolute_url()
        self.loginBrowser(browser, portalURL)
        browser.open(portalURL + url)

    def testInstalledOrganGovern(self):
        """ TODO : Test organs installed
        """
        self.createDefaultDirectories()
        login(self.portal, TEST_USER_NAME)
        news_id = 'testnews'
        self.portal.ca.noticies.invokeFactory('News Item', news_id, title=u"This is a test")
        self.assertTrue(self.portal.ca.noticies.get(news_id, False))

        news_test = self.portal.ca.noticies.testnews
        IImportant(news_test).is_important = True

        commit()
        logout()

        self.assertTrue(IImportant(news_test).is_important)

        browser = Browser(self.app)
        self.openBrowserURL(browser, "/ca/noticies/folder_contents")
        search_important = ""
        for line in browser.contents.split('\n'):
            if "id=\"folder-contents-item-" + news_id + "\"" in line:
                search_important = line
                break
        self.assertIn("item-important", search_important)
