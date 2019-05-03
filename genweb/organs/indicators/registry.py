"""
Registry containing the indicators that will be updated on the Indicators WS.
"""

import os
import logging

from genweb.core.indicators import Registry, RegistryException


logger = logging.getLogger(name='genweb.organs')

registry = None
registry_is_initialized = False


def initialize(context):
    global registry_is_initialized
    if not registry_is_initialized:
        register(context)
        registry_is_initialized = True


def get_registry(context):
    initialize(context)
    return registry


def register(context):
    global registry

    definitions_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'definitions')
    registry = Registry(context)
    registry.load_from_path(definitions_path)
    logger.info(
        "Indicators successfully loaded from {0}".format(definitions_path))

