# -*- coding: utf-8 -*-
"""Base module for unittesting (Plone 6 / Python 3)."""
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from zope.configuration import xmlconfig
import os
from plone import api
from Products.CMFCore.utils import getToolByName


class GenwebOrgansLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.restapi
        xmlconfig.file("configure.zcml", plone.restapi, context=configurationContext)

        import genweb6.core
        xmlconfig.file("configure.zcml", genweb6.core, context=configurationContext)

        import genweb6.theme
        xmlconfig.file("configure.zcml", genweb6.theme, context=configurationContext)

        import genweb6.upc
        xmlconfig.file("configure.zcml", genweb6.upc, context=configurationContext)

        import genweb.organs
        xmlconfig.file("configure.zcml", genweb.organs, context=configurationContext)

        # 🔹 Cargar ZCML de la dependencia que da problemas
        import collective.z3cform.datagridfield
        xmlconfig.file(
            "configure.zcml", collective.z3cform.datagridfield,
            context=configurationContext)

        import collective.easyform
        xmlconfig.file("configure.zcml", collective.easyform,
                       context=configurationContext)

        import plone.app.mosaic
        xmlconfig.file("configure.zcml", plone.app.mosaic, context=configurationContext)

        import Products.PloneKeywordManager
        xmlconfig.file(
            "configure.zcml", Products.PloneKeywordManager,
            context=configurationContext)

    def setUpPloneSite(self, portal):
        # Workflow per defecte
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")

        # Aplicar perfils
        applyProfile(portal, "genweb6.upc:default")
        applyProfile(portal, "genweb.organs:default")

        # Asegurarte que el usuario de testing existe y tenga rol Manager
        setRoles(portal, TEST_USER_ID, ['Manager'])

        # Usuarios adicionales para otros tests (no necesarios para test_create_sessions.py)
        # users = [
        #     ('usuari.manager', 'Secret123', ['Manager'], 'Usuari Manager', 'manager@example.com'),
        #     ('usuari.secretari', 'Secret123', ['OG1-Secretari'], 'Usuari Secretari', 'secretari@example.com'),
        #     ('usuari.editor', 'Secret123', ['OG2-Editor'], 'Usuari Editor', 'editor@example.com'),
        #     ('usuari.membre', 'Secret123', ['OG3-Membre'], 'Usuari Membre', 'membre@example.com'),
        #     ('usuari.afectat', 'Secret123', ['OG4-Afectat'], 'Usuari Afectat', 'afectat@example.com'),
        #     ('usuari.convidat', 'Secret123', ['OG5-Convidat'], 'Usuari Convidat', 'convidat@example.com'),
        # ]

        # for username, password, roles, fullname, email in users:
        #     api.user.create(
        #         username=username,
        #         password=password,
        #         roles=['Member'],  # rol base necessari
        #         properties={'fullname': fullname, 'email': email}
        #     )
        #     # Assigna rols globals per a testing
        #     setRoles(portal, username, roles)

        # Marcar que estem en mode testing
        os.environ["PLONE_TESTING"] = "1"


GENWEB_ORGANS_FIXTURE = GenwebOrgansLayer()

GENWEB_ORGANS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GENWEB_ORGANS_FIXTURE,),
    name="GenwebOrgansLayer:Integration",
)

GENWEB_ORGANS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GENWEB_ORGANS_FIXTURE,),
    name="GenwebOrgansLayer:Functional",
)
