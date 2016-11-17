# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone import api
from time import strftime
from zope.annotation.interfaces import IAnnotations
from datetime import datetime
from genweb.organs import _
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from genweb.organs.content.punt import IPunt
from genweb.organs.content.subpunt import ISubpunt
from five import grok


@grok.subscribe(IPunt, IObjectRemovedEvent)
@grok.subscribe(ISubpunt, IObjectRemovedEvent)
def removeObject(content, event):
    """ If organs.session change WF to convoque, sends email and
        shows the info in the template
    """
    # si passem estat a convocat cal enviar mail de convocatoria...
    import ipdb;ipdb.set_trace()
