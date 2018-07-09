# -*- coding: utf-8 -*-
# All the add / delete / modiified events
# The related to DELETE punt / subpunt / acord  are in other block
#    browser/events/removeObject.py
# Because they need to reorder elements
# and assign new proposalpoint values

from five import grok
from zope.app.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from genweb.organs.content.acta import IActa
from genweb.organs.content.acord import IAcord
from genweb.organs.content.punt import IPunt
from genweb.organs.content.subpunt import ISubpunt
from genweb.organs.utils import addEntryLog
from genweb.organs import _


@grok.subscribe(IAcord, IObjectAddedEvent)
def acordAdded(content, event):
    """ Acord added handler """
    addEntryLog(content.__parent__, None, _(u'Created acord'), str(content.Title()))


@grok.subscribe(IActa, IObjectAddedEvent)
def actaAdded(content, event):
    """ Acta added handler """
    addEntryLog(content.__parent__, None, _(u'Created acta'), str(content.Title()))


@grok.subscribe(IPunt, IObjectAddedEvent)
def puntAdded(content, event):
    """ Punt added handler """
    addEntryLog(content.__parent__, None, _(u'Created punt'), str(content.Title()))


@grok.subscribe(ISubpunt, IObjectAddedEvent)
def subpuntAdded(content, event):
    """ Punt added handler """
    addEntryLog(content.aq_parent.aq_parent, None, _(u'Created subpunt'), str(content.Title()))


# @grok.subscribe(IAcord, IObjectRemovedEvent)
# def acordDeleted(content, event):
#     """ Acord delete handler
#     """
#     folder_path = '/'.join(content.getPhysicalPath())
#     addEntryLog(content.__parent__, None, _(u'Deleted acord'), folder_path)


@grok.subscribe(IActa, IObjectRemovedEvent)
def actaDeleted(content, event):
    """ Acta delete handler
    """
    addEntryLog(content.__parent__, None, _(u'Deleted acta'), content.absolute_url())


# @grok.subscribe(IPunt, IObjectRemovedEvent)
# def puntDeleted(content, event):
#     """ Punt delete handler
#     """
#     folder_path = '/'.join(content.getPhysicalPath())
#     addEntryLog(content.__parent__, None, _(u'Deleted punt'), folder_path)


# @grok.subscribe(ISubpunt, IObjectRemovedEvent)
# def subpuntDeleted(content, event):
#     """ Subpunt delete handler
#     """
#     folder_path = '/'.join(content.getPhysicalPath())
#     addEntryLog(content.__parent__, None, _(u'Deleted subpunt'), folder_path)


@grok.subscribe(IAcord, IObjectModifiedEvent)
def acordModified(content, event):
    """ Acord modify handler"""
    addEntryLog(content.__parent__, None, _(u'Modified acord'), content.absolute_url())


@grok.subscribe(IActa, IObjectModifiedEvent)
def actaModified(content, event):
    """ Acta modify handler """
    addEntryLog(content.__parent__, None, _(u'Modified acta'), content.absolute_url())


@grok.subscribe(IPunt, IObjectModifiedEvent)
def puntModified(content, event):
    """ Punt modify handler """
    addEntryLog(content.__parent__, None, _(u'Modified punt'), content.absolute_url())


@grok.subscribe(ISubpunt, IObjectModifiedEvent)
def subpuntModified(content, event):
    """ Subpunt modify handler """
    addEntryLog(content.aq_parent.aq_parent, None, _(u'Modified subpunt'), content.absolute_url())
