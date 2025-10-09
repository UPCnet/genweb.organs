# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
<<<<<<< Updated upstream
from plone.testing import zope
# SESSIONS_FIXTURE no existe en Plone 6, se usa PLONE_FIXTURE directamente
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
=======
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
>>>>>>> Stashed changes
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.testing import zope
from zope.configuration import xmlconfig


class GenwebOrgansLayer(PloneSandboxLayer):
    """Layer para testing de genweb.organs."""

<<<<<<< Updated upstream
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
=======
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML - IMPORTANTE: cargar genweb6.core ANTES que genweb6.upc
        # para que los permisos estén disponibles

        try:
            import genweb6.core
            xmlconfig.file('configure.zcml',
                           genweb6.core,
                           context=configurationContext)
        except ImportError:
            # genweb6.core no está disponible, continuar sin él
            print("Warning: genweb6.core not available")
            pass

        try:
            import genweb6.upc
            xmlconfig.file('configure.zcml',
                           genweb6.upc,
                           context=configurationContext)
        except ImportError:
            # genweb6.upc no está disponible, continuar sin él
            print("Warning: genweb6.upc not available")
            pass

>>>>>>> Stashed changes
        import genweb.organs
        xmlconfig.file('configure.zcml',
                       genweb.organs,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Set up the test user with Manager role
        login(portal, TEST_USER_NAME)
        setRoles(portal, TEST_USER_ID, ['Manager'])

        # Needed for PAC not complain about not having one... T_T
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")

<<<<<<< Updated upstream
        # Install into Plone site using portal_setup
        try:
            applyProfile(portal, 'genweb6.upc:default')
        except Exception:
            # genweb6.upc no está disponible, continuar sin él
            pass

        try:
            applyProfile(portal, 'genweb6.theme:default')
        except Exception:
            # genweb6.theme no está disponible, continuar sin él
            pass

        applyProfile(portal, 'genweb.organs:default')

        # Ensure required Organs roles exist
        try:
            acl = portal.acl_users
            role_manager = getattr(acl, 'portal_role_manager', None)
            if role_manager is not None:
                for role_id in (
                    'OG1-Secretari',
                    'OG2-Editor',
                    'OG3-Membre',
                    'OG4-Afectat',
                    'OG5-Convidat',
                ):
                    try:
                        if role_id not in role_manager.listRoleIds():
                            role_manager.addRole(role_id)
                            print(f"Added role: {role_id}")
                    except Exception as e:
                        print(f"Warning: Could not add role {role_id}: {e}")
        except Exception as e:
            print(f"Warning: Could not ensure OGx roles exist: {e}")

        # Create 'ca' language folder if it doesn't exist
        try:
            if 'ca' not in portal:
                from plone.api import content
                content.create(
                    type='Folder',
                    id='ca',
                    title='Catalan',
                    container=portal
                )
                print("Created 'ca' language folder")
        except Exception as e:
            print(f"Warning: Could not create 'ca' folder: {e}")

        # # If you need to create site users...
        # portal.acl_users.userFolderAddUser('usuari.manager', 'secret', ['Manager'], [])
        # portal.acl_users.userFolderAddUser('usuari.secretari', 'secret', ['OG1-Secretari'], [])
        # portal.acl_users.userFolderAddUser('usuari.editor', 'secret', ['OG2-Editor'], [])
        # portal.acl_users.userFolderAddUser('usuari.membre', 'secret', ['OG3-Membre'], [])
        # portal.acl_users.userFolderAddUser('usuari.afectat', 'secret', ['OG4-Afectat'], [])
=======
        # Install plone.app.multilingual first
        try:
            applyProfile(portal, 'plone.app.multilingual:default')
            print("Successfully applied plone.app.multilingual profile")
        except Exception as e:
            print(f"Warning: Could not apply plone.app.multilingual "
                  f"profile: {e}")

        # Install genweb workflows first
        try:
            applyProfile(portal, 'genweb6.core:workflows')
            print("Successfully applied genweb6.core workflows")
        except Exception as e:
            print(f"Warning: Could not apply genweb6.core workflows: {e}")

        # Install into Plone site using portal_setup
        try:
            applyProfile(portal, 'genweb6.core:default')
            print("Successfully applied genweb6.core profile")
        except Exception as e:
            # genweb6.core no está disponible, continuar sin él
            print(f"Warning: Could not apply genweb6.core profile: {e}")
            pass

        try:
            applyProfile(portal, 'genweb6.upc:default')
            print("Successfully applied genweb6.upc profile")
        except Exception as e:
            # genweb6.upc no está disponible, continuar sin él
            print(f"Warning: Could not apply genweb6.upc profile: {e}")
            pass

        try:
            applyProfile(portal, 'genweb6.theme:default')
            print("Successfully applied genweb6.theme profile")
        except Exception as e:
            # genweb6.theme no está disponible, continuar sin él
            print(f"Warning: Could not apply genweb6.theme profile: {e}")
            pass

        applyProfile(portal, 'genweb.organs:default')
        print("Successfully applied genweb.organs profile")

        # Create test users for different roles
        self._create_test_users(portal)

    def _create_test_users(self, portal):
        """Create test users with different roles."""
        try:
            from plone.app.testing import TEST_USER_ID, setRoles

            # Ensure the default test user has Manager role
            setRoles(portal, TEST_USER_ID, ['Manager'])

            # Create users with genweb.organs specific roles
            # that are defined in rolemap.xml
            portal.acl_users.userFolderAddUser(
                'usuari.manager', 'secret', ['Manager'], [])
            portal.acl_users.userFolderAddUser(
                'usuari.secretari', 'secret', ['OG1-Secretari'], [])
            portal.acl_users.userFolderAddUser(
                'usuari.editor', 'secret', ['OG2-Editor'], [])
            portal.acl_users.userFolderAddUser(
                'usuari.membre', 'secret', ['OG3-Membre'], [])
            portal.acl_users.userFolderAddUser(
                'usuari.afectat', 'secret', ['OG4-Afectat'], [])
            portal.acl_users.userFolderAddUser(
                'usuari.convidat', 'secret', ['OG5-Convidat'], [])
            print("Successfully created test users")
        except Exception as e:
            print(f"Warning: Could not create test users: {e}")
>>>>>>> Stashed changes

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
        zope.WSGI_SERVER_FIXTURE,
    ),
    name="GenwebOrgansLayer:AcceptanceTesting",
)
