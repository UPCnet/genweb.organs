# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from plone.app.multilingual.testing import SESSIONS_FIXTURE
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from zope.configuration import xmlconfig


class GenwebOrgansLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE, SESSIONS_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import genweb.upc
        xmlconfig.file('configure.zcml',
                       genweb.upc,
                       context=configurationContext)

        import genweb.organs
        xmlconfig.file('configure.zcml',
                       genweb.organs,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Needed for PAC not complain about not having one... T_T
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")

        # Install into Plone site using portal_setup
        applyProfile(portal, 'genweb.upc:default')
        applyProfile(portal, 'genweb.organs:default')

        # # If you need to create site users...
        # portal.acl_users.userFolderAddUser('usuari.manager', 'secret', ['Manager'], [])
        # portal.acl_users.userFolderAddUser('usuari.secretari', 'secret', ['OG1-Secretari'], [])
        # portal.acl_users.userFolderAddUser('usuari.editor', 'secret', ['OG2-Editor'], [])
        # portal.acl_users.userFolderAddUser('usuari.membre', 'secret', ['OG3-Membre'], [])
        # portal.acl_users.userFolderAddUser('usuari.afectat', 'secret', ['OG4-Afectat'], [])

    def tearDownZope(self, app):
        """Tear down Zope."""
        pass


GENWEB_ORGANS_FIXTURE = GenwebOrgansLayer()


GENWEB_ORGANS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GENWEB_ORGANS_FIXTURE,),
    name="GenwebOrgansLayer:Integration",
)

GENWEB_ORGANS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GENWEB_ORGANS_FIXTURE,),
    name="GenwebOrgansLayer:Functional",
)

GENWEB_ORGANS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        GENWEB_ORGANS_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="GenwebOrgansLayer:AcceptanceTesting",
)
