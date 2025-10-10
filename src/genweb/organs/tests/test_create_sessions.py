# -*- coding: utf-8 -*-
import unittest
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login, logout, setRoles
from plone import api
from AccessControl import Unauthorized
from zope.component import getMultiAdapter
from plone.api.env import adopt_roles
import datetime

from genweb.organs.testing import GENWEB_ORGANS_FUNCTIONAL_TESTING


class OrgansFunctionalTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = GENWEB_ORGANS_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # Create default GW directories
        setupview = getMultiAdapter(
            (self.portal, self.request),
            name='setup-view'
        )
        setupview.apply_default_language_settings()
        setupview.setup_multilingual()
        setupview.createContent()

        # Enable the possibility to add Organs folder
        from Products.CMFPlone.interfaces import ISelectableConstrainTypes
        behavior = ISelectableConstrainTypes(self.portal['ca'])
        behavior.setConstrainTypesMode(1)
        behavior.setLocallyAllowedTypes(['genweb.organs.organsfolder'])
        behavior.setImmediatelyAddableTypes(['genweb.organs.organsfolder'])

        # Create Base folder to create base test folders
        try:
            api.content.delete(
                obj=self.portal['ca']['testingfolder'],
                check_linkintegrity=False
            )
        except Exception:
            pass

        # Create default Organs Test Folder
        og_unit = api.content.create(
            type='genweb.organs.organsfolder',
            id='testingfolder',
            title='Organ Tests',
            container=self.portal['ca']
        )

        # Create test organs
        self.roots = {}
        for organ_type, organ_id, organ_title in [
            ('obert', 'open_organ', 'Organ TEST Obert'),
            ('afectats', 'restricted_to_affected_organ',
             'Organ TEST restringit a AFECTATS'),
            ('membres', 'restricted_to_members_organ',
             'Organ TEST restringit a MEMBRES')
        ]:
            organ = api.content.create(
                type='genweb.organs.organgovern',
                id=organ_id,
                title=organ_title,
                container=og_unit,
                safe_id=True
            )
            organ.acronim = f'OG.{organ_type.upper()}'
            organ.organType = organ_type
            self.roots[organ_type] = organ

        # Verify organs were created
        for organ_type in self.roots:
            self.assertIsNotNone(
                self.roots[organ_type],
                f"El órgano {organ_type} no se creó correctamente"
            )
            self.assertEqual(
                self.roots[organ_type].portal_type,
                'genweb.organs.organgovern',
                f"El órgano {organ_type} no es del tipo correcto"
            )

        logout()

    def test_create_sessions_in_organs(self):
        """Test users who can create sessions"""

        # Roles que pueden crear sesiones
        roles_tests = [
            ('Manager', True),
            ('OG1-Secretari', True),
            ('OG2-Editor', True),
            ('OG3-Membre', False),
            ('OG4-Afectat', False),
            ('OG5-Convidat', False),
            ('Anonim', False)
        ]

        for organ_name, organ in self.roots.items():
            for role, can_create in roles_tests:
                session_id = f'session_{role}_{organ_name}'

                if can_create:
                    # For roles that can create, use setRoles + login
                    setRoles(self.portal, TEST_USER_ID, [role])
                    login(self.portal, TEST_USER_NAME)
                    now = datetime.datetime.now()
                    session = api.content.create(
                        type='genweb.organs.sessio',
                        id=session_id,
                        title=f'Session {role} {organ_name}',
                        container=organ,
                        start=now,
                        end=now + datetime.timedelta(hours=1),
                        modality='attended',
                        numSessioShowOnly='01',
                        numSessio='01'
                    )
                    self.assertIsNotNone(session)
                    print(
                        f"\n✅ El rol {role} ha podido crear sesión en el órgano {organ_name} correctamente")
                    logout()
                else:
                    # For roles that cannot create, use adopt_roles
                    print(
                        f"\n❌ Verificando que el rol {role} NO puede crear sesión en el órgano {organ_name}")
                    with self.assertRaises(Unauthorized):
                        with adopt_roles(role):
                            now = datetime.datetime.now()
                            api.content.create(
                                type='genweb.organs.sessio',
                                id=session_id,
                                title=f'Session {role} {organ_name}',
                                container=organ,
                                start=now,
                                end=now + datetime.timedelta(hours=1),
                                modality='attended',
                                numSessioShowOnly='01',
                                numSessio='01'
                            )
