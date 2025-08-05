# -*- coding: utf-8 -*-
from plone import api
from zope.globalrequest import getRequest
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

from genweb.organs import _
from genweb.organs.content.acord.acord import IAcord
from genweb.organs.content.punt.punt import IPunt
from genweb.organs.content.punt.subpunt import ISubpunt
from genweb.organs.utils import addEntryLog

import transaction


def remove_punt_acord(trans, obj=None, parent=None):
    """ Removing punt i subpunt is the same """
    portal_catalog = api.portal.get_tool(name='portal_catalog')
    items = portal_catalog.searchResults(
        portal_type=['genweb.organs.punt', 'genweb.organs.acord', 'genweb.organs.subpunt'],
        sort_on='getObjPositionInParent',
        path={'query': parent.absolute_url_path(),
              'depth': 1})
    index = 1
    sufix = None
    # check if second level to assign index value
    if obj.aq_parent.portal_type == 'genweb.organs.punt' or obj.aq_parent.portal_type == 'genweb.organs.acord':
        sufix = obj.aq_parent.proposalPoint

    for item in items:
        objecte = item.getObject()
        if sufix:
            objecte.proposalPoint = str(sufix) + str('.') + str(index)
        else:
            objecte.proposalPoint = index
        if len(objecte.items()) > 0:
            search_path = '/'.join(objecte.getPhysicalPath())
            values = portal_catalog.searchResults(
                portal_type=['genweb.organs.punt', 'genweb.organs.subpunt', 'genweb.organs.acord'],
                sort_on='getObjPositionInParent',
                path={'query': search_path, 'depth': 1})
            subvalue = 1
            for value in values:
                newobjecte = value.getObject()
                if sufix:
                    newobjecte.proposalPoint = str(sufix) + str('.') + str(subvalue)
                else:
                    newobjecte.proposalPoint = str(index) + str('.') + str(subvalue)
                subvalue = subvalue + 1
        index = index + 1

    if obj.aq_parent.portal_type == 'genweb.organs.punt':
        if obj.portal_type == 'genweb.organs.acord':
            addEntryLog(obj.aq_parent.aq_parent, None, _(u'Deleted acord'), str(obj.Title()))
    else:
        if obj.portal_type == 'genweb.organs.acord':
            addEntryLog(obj.aq_parent, None, _(u'Deleted acord'), str(obj.Title()))
        else:
            addEntryLog(obj.aq_parent, None, _(u'Deleted punt'), str(obj.Title()))
    transaction.commit()


def remove_subpunt(trans, obj=None, parent=None):
    portal_catalog = api.portal.get_tool(name='portal_catalog')
    items = portal_catalog.searchResults(
        portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
        sort_on='getObjPositionInParent',
        path={'query': parent.absolute_url_path(),
              'depth': 1})
    index = 1
    # Assign proposalPoints to acord and subpunts
    if items:
        # Get the real object, not the catalog brain
        first_item = items[0].getObject()
        sufix = str(first_item.proposalPoint).split('.')[0]
        for item in items:
            newobjecte = item.getObject()
            newobjecte.proposalPoint = str(sufix) + str('.') + str(index)
            index = index + 1
        addEntryLog(obj.aq_parent.aq_parent, None, _(u'Deleted subpunt'), str(obj.Title()))
        transaction.commit()

def deletion_confirmed():
    """
    Check if the current request is a confirmed deletion en Plone 6.
    """
    request = getRequest()
    # Detecta URLs de borrado modernas y legacy
    is_delete_confirmation = (
        'delete_confirmation' in request.URL or
        'deleteElement' in request.URL or
        'delete' in request.URL
    )
    is_post = request.REQUEST_METHOD == 'POST'

    # Plone 6: el form puede tener solo 'action': 'delete' y no 'form.submitted' ni 'form.button.Delete'
    form_being_submitted = (
        request.form.get('action') == 'delete'
    )
    form_cancelled = 'form.button.Cancel' in request.form
    # En Plone 6, no siempre hay 'form.button.Delete', así que lo quitamos del check

    # Solo es true si es un borrado confirmado y no cancelado
    return (
        is_delete_confirmation and
        is_post and
        form_being_submitted and
        not form_cancelled
    )


def removePunt(obj, event):
    """ When the Punt is deleted, reorder proposalPoint field """
    if deletion_confirmed():
        remove_punt_acord(None, obj=obj, parent=event.oldParent)


def removeSubpunt(obj, event):
    """ When the Subpunt is deleted, reorder proposalPoint field """
    if deletion_confirmed():
        # kwargs = dict(obj=obj, parent=event.oldParent)
        # transaction.get().addAfterCommitHook(remove_subpunt, kws=kwargs)
        remove_subpunt(None, obj=obj, parent=event.oldParent)


def removeAcord(obj, event):
    """ When the Acord is deleted, reorder proposalPoint field """
    if deletion_confirmed():
        remove_punt_acord(None, obj=obj, parent=event.oldParent)
