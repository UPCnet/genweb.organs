# -*- coding: utf-8 -*-
"""Test runner configuration for genweb.organs."""
import unittest
import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))


def test_suite():
    """Create test suite for all tests."""
    suite = unittest.TestSuite()

    # Add all test modules
    test_modules = [
        'test_config',
        'test_base',
        'test_sessions',
        'test_file_permissions',
        'test_acta_permissions',
        'test_organs_functionality',
        'test_session_functionality',
        'test_content_functionality',
    ]

    for module_name in test_modules:
        try:
            module = __import__(module_name, globals(), locals(), [])
            suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(module))
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")

    return suite


if __name__ == '__main__':
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite())

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
