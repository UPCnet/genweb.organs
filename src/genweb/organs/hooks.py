# -*- coding: utf-8 -*-
# All the add / delete / modiified events
# The related to DELETE punt / subpunt / acord  are in other block
#    browser/events/removeObject.py
# Because they need to reorder elements
# and assign new proposalpoint values

from zope.container.interfaces import IObjectAddedEvent
from zope.container.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from genweb.organs import _
from genweb.organs.content.acord import IAcord
from genweb.organs.content.acta import IActa
from genweb.organs.content.punt import IPunt
from genweb.organs.content.subpunt import ISubpunt
from genweb.organs.utils import addEntryLog


def acordAdded(content, event):
    """ Acord added handler """
    addEntryLog(content.__parent__, None, _(u'Created acord'), str(content.Title()))


def actaAdded(content, event):
    """ Acta added handler """
    addEntryLog(content.__parent__, None, _(u'Created acta'), str(content.Title()))


def puntAdded(content, event):
    """ Punt added handler """
    addEntryLog(content.__parent__, None, _(u'Created punt'), str(content.Title()))


def subpuntAdded(content, event):
    """ Punt added handler """
    addEntryLog(content.aq_parent.aq_parent, None, _(u'Created subpunt'), str(content.Title()))


def actaDeleted(content, event):
    """ Acta delete handler
    """
    addEntryLog(content.__parent__, None, _(u'Deleted acta'), content.absolute_url())


def acordModified(content, event):
    """ Acord modify handler"""
    addEntryLog(content.__parent__, None, _(u'Modified acord'), content.absolute_url())


def actaModified(content, event):
    """ Acta modify handler """
    addEntryLog(content.__parent__, None, _(u'Modified acta'), content.absolute_url())


def puntModified(content, event):
    """ Punt modify handler """
    if event.descriptions != ():
        addEntryLog(content.__parent__, None, _(u'Modified punt'), content.absolute_url())


def subpuntModified(content, event):
    """ Subpunt modify handler """
    if event.descriptions != ():
        addEntryLog(content.aq_parent.aq_parent, None, _(u'Modified subpunt'), content.absolute_url())
