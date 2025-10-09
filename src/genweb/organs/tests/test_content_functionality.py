# -*- coding: utf-8 -*-
"""Functional tests for content functionality (points, agreements, etc.)."""
import unittest
from plone import api
from genweb.organs.tests.base import FunctionalTestCase


class TestPointFunctionality(FunctionalTestCase):
    """Test point functionality."""

    def test_point_creation(self):
        """Test that points can be created properly."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create a new point
        point = self.assertCanCreate(
            'genweb.organs.punt',
            session,
            id='test_point',
            title='Test Point'
        )

        # Verify point properties
        self.assertEqual(point.id, 'test_point')
        self.assertEqual(point.title, 'Test Point')

        self.logout()

    def test_point_workflow(self):
        """Test point workflow functionality."""
        point = self.portal.ca.testingfolder.obert.planificada.punt

        self.login_as_manager()

        # Check initial state
        initial_state = api.content.get_state(point)
        self.assertIsNotNone(initial_state)

        # Test workflow transitions
        api.content.transition(obj=point, transition='publish')
        published_state = api.content.get_state(point)
        self.assertEqual(published_state, 'published')

        self.logout()

    def test_point_subpoint_creation(self):
        """Test that subpoints can be created within points."""
        self.login_as_manager()

        point = self.portal.ca.testingfolder.obert.planificada.punt

        # Create a subpoint
        subpoint = self.assertCanCreate(
            'genweb.organs.subpunt',
            point,
            id='test_subpoint',
            title='Test Subpoint'
        )

        # Verify subpoint properties
        self.assertEqual(subpoint.id, 'test_subpoint')
        self.assertEqual(subpoint.title, 'Test Subpoint')

        self.logout()

    def test_point_permissions(self):
        """Test point permissions for different roles."""
        point = self.portal.ca.testingfolder.obert.planificada.punt

        # Test that all roles can view the point
        for role_method in [self.login_as_secretari, self.login_as_editor,
                            self.login_as_membre, self.login_as_afectat,
                            self.login_as_convidat]:
            role_method()

            # Should be able to access the point
            self.assertTrue(api.content.get_state(point))

            self.logout()


class TestAgreementFunctionality(FunctionalTestCase):
    """Test agreement functionality."""

    def test_agreement_creation(self):
        """Test that agreements can be created properly."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create a new agreement
        agreement = self.assertCanCreate(
            'genweb.organs.acord',
            session,
            id='test_agreement',
            title='Test Agreement'
        )

        # Verify agreement properties
        self.assertEqual(agreement.id, 'test_agreement')
        self.assertEqual(agreement.title, 'Test Agreement')

        self.logout()

    def test_agreement_workflow(self):
        """Test agreement workflow functionality."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create an agreement
        agreement = self.assertCanCreate(
            'genweb.organs.acord',
            session,
            id='test_agreement_workflow',
            title='Test Agreement Workflow'
        )

        # Check initial state
        initial_state = api.content.get_state(agreement)
        self.assertIsNotNone(initial_state)

        # Test workflow transitions
        api.content.transition(obj=agreement, transition='publish')
        published_state = api.content.get_state(agreement)
        self.assertEqual(published_state, 'published')

        self.logout()

    def test_agreement_permissions(self):
        """Test agreement permissions for different roles."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create an agreement
        agreement = self.assertCanCreate(
            'genweb.organs.acord',
            session,
            id='test_agreement_permissions',
            title='Test Agreement Permissions'
        )

        self.logout()

        # Test that all roles can view the agreement
        for role_method in [self.login_as_secretari, self.login_as_editor,
                            self.login_as_membre, self.login_as_afectat,
                            self.login_as_convidat]:
            role_method()

            # Should be able to access the agreement
            self.assertTrue(api.content.get_state(agreement))

            self.logout()


class TestActaFunctionality(FunctionalTestCase):
    """Test acta functionality."""

    def test_acta_creation(self):
        """Test that actas can be created properly."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create a new acta
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            session,
            id='test_acta',
            title='Test Acta'
        )

        # Verify acta properties
        self.assertEqual(acta.id, 'test_acta')
        self.assertEqual(acta.title, 'Test Acta')

        self.logout()

    def test_acta_workflow(self):
        """Test acta workflow functionality."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create an acta
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            session,
            id='test_acta_workflow',
            title='Test Acta Workflow'
        )

        # Check initial state
        initial_state = api.content.get_state(acta)
        self.assertIsNotNone(initial_state)

        # Test workflow transitions
        api.content.transition(obj=acta, transition='publish')
        published_state = api.content.get_state(acta)
        self.assertEqual(published_state, 'published')

        self.logout()

    def test_acta_permissions(self):
        """Test acta permissions for different roles."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create an acta
        acta = self.assertCanCreate(
            'genweb.organs.acta',
            session,
            id='test_acta_permissions',
            title='Test Acta Permissions'
        )

        self.logout()

        # Test that all roles can view the acta
        for role_method in [self.login_as_secretari, self.login_as_editor,
                            self.login_as_membre, self.login_as_afectat,
                            self.login_as_convidat]:
            role_method()

            # Should be able to access the acta
            self.assertTrue(api.content.get_state(acta))

            self.logout()


class TestFileFunctionality(FunctionalTestCase):
    """Test file functionality."""

    def test_file_creation(self):
        """Test that files can be created properly."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create a new file
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            session,
            id='test_file',
            title='Test File'
        )

        # Verify file properties
        self.assertEqual(file_obj.id, 'test_file')
        self.assertEqual(file_obj.title, 'Test File')

        self.logout()

    def test_file_workflow(self):
        """Test file workflow functionality."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create a file
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            session,
            id='test_file_workflow',
            title='Test File Workflow'
        )

        # Check initial state
        initial_state = api.content.get_state(file_obj)
        self.assertIsNotNone(initial_state)

        # Test workflow transitions
        api.content.transition(obj=file_obj, transition='publish')
        published_state = api.content.get_state(file_obj)
        self.assertEqual(published_state, 'published')

        self.logout()

    def test_file_permissions(self):
        """Test file permissions for different roles."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create a file
        file_obj = self.assertCanCreate(
            'genweb.organs.file',
            session,
            id='test_file_permissions',
            title='Test File Permissions'
        )

        self.logout()

        # Test that all roles can view the file
        for role_method in [self.login_as_secretari, self.login_as_editor,
                            self.login_as_membre, self.login_as_afectat,
                            self.login_as_convidat]:
            role_method()

            # Should be able to access the file
            self.assertTrue(api.content.get_state(file_obj))

            self.logout()


class TestDocumentFunctionality(FunctionalTestCase):
    """Test document functionality."""

    def test_document_creation(self):
        """Test that documents can be created properly."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create a new document
        document = self.assertCanCreate(
            'genweb.organs.document',
            session,
            id='test_document',
            title='Test Document'
        )

        # Verify document properties
        self.assertEqual(document.id, 'test_document')
        self.assertEqual(document.title, 'Test Document')

        self.logout()

    def test_document_workflow(self):
        """Test document workflow functionality."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create a document
        document = self.assertCanCreate(
            'genweb.organs.document',
            session,
            id='test_document_workflow',
            title='Test Document Workflow'
        )

        # Check initial state
        initial_state = api.content.get_state(document)
        self.assertIsNotNone(initial_state)

        # Test workflow transitions
        api.content.transition(obj=document, transition='publish')
        published_state = api.content.get_state(document)
        self.assertEqual(published_state, 'published')

        self.logout()

    def test_document_permissions(self):
        """Test document permissions for different roles."""
        self.login_as_manager()

        session = self.portal.ca.testingfolder.obert.planificada

        # Create a document
        document = self.assertCanCreate(
            'genweb.organs.document',
            session,
            id='test_document_permissions',
            title='Test Document Permissions'
        )

        self.logout()

        # Test that all roles can view the document
        for role_method in [self.login_as_secretari, self.login_as_editor,
                            self.login_as_membre, self.login_as_afectat,
                            self.login_as_convidat]:
            role_method()

            # Should be able to access the document
            self.assertTrue(api.content.get_state(document))

            self.logout()
