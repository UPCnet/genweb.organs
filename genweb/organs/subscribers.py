from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from Products.CMFCore.interfaces import IActionSucceededEvent

from genweb.organs.utils import get_settings_property
from genweb.organs.content.organgovern import IOrgangovern
from genweb.organs.content.sessio import ISessio
from genweb.organs.content.acord import IAcord
from genweb.organs.indicators.updating import (
    update_indicators,
    update_indicators_if_state)


def update_indicators_on_organ_deletion(obj, event):
    update_indicators_if_state(
        obj, ('intranet', 'published'),
        service=get_settings_property('service_id'), indicator='organ-n')


def update_indicators_on_organ_review_state_change(obj, event):
    update_indicators(
        obj, service=get_settings_property('service_id'), indicator='organ-n')


def update_indicators_on_sessio_deletion(obj, event):
    update_indicators_if_state(
        obj, ('convocada',),
        service=get_settings_property('service_id'), indicator='sessio-n')


def update_indicators_on_sessio_review_state_change(obj, event):
    update_indicators(
        obj, service=get_settings_property('service_id'), indicator='sessio-n')


def update_indicators_on_acord_deletion(obj, event):
    update_indicators_if_state(
        obj, ('intranet', 'published'),
        service=get_settings_property('service_id'), indicator='acord-n')


def update_indicators_on_acord_review_state_change(obj, event):
    update_indicators(
        obj, service=get_settings_property('service_id'), indicator='acord-n')
