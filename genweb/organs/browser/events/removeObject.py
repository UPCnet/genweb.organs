# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from genweb.organs.content.punt import IPunt
from genweb.organs.content.subpunt import ISubpunt
from five import grok
from zope.globalrequest import getRequest
from genweb.organs.utils import addEntryLog
from genweb.organs import _


def deletion_confirmed():
    """Check if we are in the context of a delete confirmation event.
    We need to be sure we're in the righ event to process it, as
    `IObjectRemovedEvent` is raised up to three times: the first one
    when the delete confirmation window is shown; the second when we
    select the 'Delete' button; and the last, as part of the
    redirection request to the parent container. Why? I have absolutely
    no idea. If we select 'Cancel' after the first event, then no more
    events are fired.
    """
    request = getRequest()
    is_delete_confirmation = 'delete_confirmation' in request.URL
    is_post = request.REQUEST_METHOD == 'POST'
    form_being_submitted = 'form.submitted' in request.form
    form_cancelled = 'form.button.Cancel' in request.form
    form_delete = 'form.button.Delete' in request.form
    return is_delete_confirmation and is_post and form_being_submitted and not form_cancelled or form_delete


@grok.subscribe(IPunt, IObjectRemovedEvent)
def removePunt(alias, event):
    """ When the alias is created,
        TODO make reorder obects fully functional!
    """
    if deletion_confirmed():
        portal_catalog = getToolByName(alias, 'portal_catalog')
        folder_path = '/'.join(alias.__parent__.getPhysicalPath())
        addEntryLog(alias.aq_parent, None, _(u'Deleted punt'), alias.absolute_url_path())  # add log
        # agafo items ordenats!

        puntsOrdered = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        # hi ha items PUNT per esborrar
        if puntsOrdered:
            index = 1
            for item in puntsOrdered:
                objecte = item.getObject()
                objecte.proposalPoint = unicode(str(index))
                objecte.reindexObject()
                if len(objecte.items()) > 0:
                    search_path = '/'.join(objecte.getPhysicalPath())
                    subpunts = portal_catalog.searchResults(
                        portal_type=['genweb.organs.subpunt'],
                        sort_on='getObjPositionInParent',
                        path={'query': search_path, 'depth': 1})

                    subvalue = 1
                    for value in subpunts:
                        newobjecte = value.getObject()
                        newobjecte.proposalPoint = unicode(str(index) + str('.') + str(subvalue))
                        newobjecte.reindexObject()
                        subvalue = subvalue + 1
                index = index + 1


@grok.subscribe(ISubpunt, IObjectRemovedEvent)
def removeSubpunt(alias, event):
    """When the alias is created,
       TODO make reorder obects fully functional!
    """
    if deletion_confirmed():
        portal_catalog = getToolByName(alias, 'portal_catalog')
        folder_path = '/'.join(alias.__parent__.getPhysicalPath())
        addEntryLog(alias, None, _(u'Deleted subpunt'), '')  # add log
        # agafo items ordenats!
        subpuntsOrdered = portal_catalog.searchResults(
            portal_type=['genweb.organs.subpunt'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        # hi ha items SUBPUNT per esborrar
        if subpuntsOrdered:
            index = 1
            sufix = str(subpuntsOrdered[0].proposalPoint).split('.')[0]
            for item in subpuntsOrdered:
                item.getObject().proposalPoint = unicode(str(sufix) + str('.') + str(index))
                # item.reindexObject()
                index = index + 1
