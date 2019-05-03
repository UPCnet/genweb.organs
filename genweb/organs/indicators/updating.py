import logging

import transaction
from Products.CMFCore.utils import getToolByName

from genweb.core.indicators import RegistryException
from genweb.core.indicators import WebServiceReporter, ReporterException
from genweb.organs.utils import get_settings_property
from genweb.organs.indicators.registry import get_registry

logger = logging.getLogger(name='genweb.organs')


def update_indicators_if_state(content, state, service=None, indicator=None):
    if is_updating_enabled():
        workflow_tool = getToolByName(content, 'portal_workflow')
        if workflow_tool.getInfoFor(content, 'review_state') in state:
            update_indicators(content, service, indicator)


def update_indicators(context, service=None, indicator=None):
    if is_updating_enabled():
        transaction.get().addAfterCommitHook(
            update_after_commit_hook,
            kws=dict(context=context, service=service, indicator=indicator))


def is_updating_enabled():
    return (
        get_settings_property('service_id')
        and get_settings_property('ws_endpoint')
        and get_settings_property('ws_key'))


def update_after_commit_hook(
        is_commit_successful, context, service, indicator):
    if not is_commit_successful:
        return
    try:
        ws_url = get_settings_property('ws_endpoint')
        ws_key = get_settings_property('ws_key')
        registry = get_registry(context)

        reporter = WebServiceReporter(ws_url, ws_key)
        reporter.report(get_data_to_report(registry, service, indicator))
        logger.info("Indicators were successfully reported")
    except RegistryException as e:
        logger.warning(
            "Error while loading indicator registry ({0})".format(e))
    except ReporterException as e:
        logger.warning("Error while reporting indicators ({0})".format(e))


def get_data_to_report(registry, service, indicator):
    if not service:
        return registry
    if not indicator:
        return registry[service]
    return registry[service][indicator]
