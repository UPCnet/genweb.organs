# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from genweb.organs.content.punt import IPunt
from genweb.organs.content.subpunt import ISubpunt
from five import grok
from zope.globalrequest import getRequest


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
        print "------ Deleting..."
        print alias.__parent__.objectIds()

        portal_catalog = getToolByName(alias, 'portal_catalog')
        folder_path = '/'.join(alias.__parent__.getPhysicalPath())
        # addEntryLog(alias, 'Reload proposalPoints manually', '')  # add log
        # agafo items ordenats!

        puntsOrdered = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        index = 1
        for item in puntsOrdered:
            objecte = item.getObject()
            objecte.proposalPoint = unicode(str(index))
            print "title: " +str(item.Title) + ' -- point:  ' + str(objecte.proposalPoint)
            objecte.reindexObject()

            if len(objecte.items()) > 0:
                search_path = '/'.join(objecte.getPhysicalPath())
                subpunts = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt'],
                    sort_on='getObjPositionInParent',
                    path={'query': search_path, 'depth': 1})

                subvalue = 1
                rootnumber = objecte.proposalPoint
                for value in subpunts:
                    newobjecte = value.getObject()
                    newobjecte.proposalPoint = unicode(str(rootnumber) + str('.') + str(subvalue))
                    subvalue = subvalue+1

            index = index + 1

        print alias.__parent__.objectIds()
        for a in puntsOrdered:
            print (a.getObject().proposalPoint)


@grok.subscribe(ISubpunt, IObjectRemovedEvent)
def removeSubpunt(alias, event):
    """When the alias is created,
    """
    if deletion_confirmed():
        print "XXXXX Deleting... TODO: copy functional PUNT code!"
