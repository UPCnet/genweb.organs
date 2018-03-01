# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from plone.app.multilingual.testing import SESSIONS_FIXTURE
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE


class GenwebOrgansLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE, SESSIONS_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import genweb.upc
        import genweb.organs
        self.loadZCML(package=genweb.upc)
        self.loadZCML(package=genweb.organs)
        z2.installProduct(app, 'genweb.upc')
        z2.installProduct(app, 'genweb.organs')

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Needed for PAC not complain about not having one... T_T
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")

        # Install into Plone site using portal_setup
        applyProfile(portal, 'genweb.upc:default')
        applyProfile(portal, 'genweb.organs:default')

    def tearDownZope(self, app):
        """Tear down Zope."""
        pass


FIXTURE = GenwebOrgansLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="GenwebOrgansLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="GenwebOrgansLayer:Functional")
GENWEB_ORGANS_ROBOT_TESTING = FunctionalTesting(
    bases=(FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="GenwebOrgansLayer:Robot")
