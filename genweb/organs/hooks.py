# -*- coding: utf-8 -*-
from five import grok
from zope.app.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from genweb.organs.content.acta import IActa
from genweb.organs.content.acord import IAcord
from genweb.organs.content.punt import IPunt
from genweb.organs.utils import addEntryLog
from genweb.organs import _


@grok.subscribe(IAcord, IObjectAddedEvent)
def acordAdded(content, event):
    """ Acord added handler
    """
    addEntryLog(content.__parent__, None, _(u'Created acord'), str(content.Title()))


@grok.subscribe(IActa, IObjectAddedEvent)
def actaAdded(content, event):
    """ Acta added handler
    """
    addEntryLog(content.__parent__, None, _(u'Created acta'), str(content.Title()))


@grok.subscribe(IPunt, IObjectAddedEvent)
def puntAdded(content, event):
    """ Punt added handler
    """
    addEntryLog(content.__parent__, None, _(u'Created punt'), str(content.Title()))


@grok.subscribe(IAcord, IObjectRemovedEvent)
def acordDeleted(content, event):
    """ Acord delete handler
    """
    folder_path = '/'.join(content.getPhysicalPath())
    addEntryLog(content.__parent__, None, _(u'Deleted element'), 'acord → ' + folder_path)


@grok.subscribe(IActa, IObjectRemovedEvent)
def actaDeleted(content, event):
    """ Acta delete handler
    """
    folder_path = '/'.join(content.getPhysicalPath())
    addEntryLog(content.__parent__, None, _(u'Deleted element'), 'acta → ' + folder_path)


@grok.subscribe(IPunt, IObjectRemovedEvent)
def puntDeleted(content, event):
    """ Punt delete handler
    """
    folder_path = '/'.join(content.getPhysicalPath())
    addEntryLog(content.__parent__, None, _(u'Deleted element'), 'punt → ' + folder_path)


@grok.subscribe(IAcord, IObjectModifiedEvent)
def acordModified(content, event):
    """ Acord delete handler
    """
    folder_path = '/'.join(content.getPhysicalPath())
    addEntryLog(content.__parent__, None, _(u'Modified acord'), 'acord → ' + folder_path)


@grok.subscribe(IActa, IObjectModifiedEvent)
def actaModified(content, event):
    """ Acta delete handler
    """
    folder_path = '/'.join(content.getPhysicalPath())
    addEntryLog(content.__parent__, None, _(u'Modified acta'), 'acta → ' + folder_path)


@grok.subscribe(IPunt, IObjectModifiedEvent)
def puntModified(content, event):
    """ Punt delete handler
    """
    folder_path = '/'.join(content.getPhysicalPath())
    addEntryLog(content.__parent__, None, _(u'Modified punt'), 'punt → ' + folder_path)
