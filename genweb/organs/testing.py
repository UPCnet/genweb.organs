# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from plone.app.multilingual.testing import SESSIONS_FIXTURE
from zope.component import getMultiAdapter
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

        # Create default users
        portal.acl_users.userFolderAddUser('usuari.secretari', 'secret', ['OG1-Secretari'], [])
        portal.acl_users.userFolderAddUser('usuari.editor', 'secret', ['OG2-Editor'], [])
        portal.acl_users.userFolderAddUser('usuari.membre', 'secret', ['OG3-Membre'], [])
        portal.acl_users.userFolderAddUser('usuari.afectat', 'secret', ['OG4-Afectat'], [])

        # setupview = getMultiAdapter((portal, request), name='setup-view')
        # setupview.apply_default_language_settings()
        # setupview.setup_multilingual()
        # setupview.createContent('n3')

    def tearDownZope(self, app):
        """Tear down Zope."""
        pass


GENWEB_ORGANS_FIXTURE = GenwebOrgansLayer()
GENWEB_ORGANS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GENWEB_ORGANS_FIXTURE,), name="GenwebOrgansLayer:Integration")

GENWEB_ORGANS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GENWEB_ORGANS_FIXTURE,), name="GenwebOrgansLayer:Functional")

GENWEB_ORGANS_ROBOT_TESTING = FunctionalTesting(
    bases=(GENWEB_ORGANS_FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="GenwebOrgansLayer:Robot")
