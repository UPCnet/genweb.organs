# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from genweb.organs.content.punt import IPunt
from genweb.organs.content.subpunt import ISubpunt
from five import grok
from zope.globalrequest import getRequest
from zope.component import queryUtility
from Products.CMFCore.interfaces import IPropertiesTool
import transaction


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
    print request.form
    print  is_delete_confirmation and is_post and form_being_submitted and not form_cancelled or form_delete
    return is_delete_confirmation and is_post and form_being_submitted and not form_cancelled or form_delete


@grok.subscribe(IPunt, IObjectRemovedEvent)
def removePunt(alias, event):
    """ When the alias is created,
        TODO make reorder obects fully functional!
    """
    if deletion_confirmed():
        print '___________deleting punt'
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
            print(str(objecte.Title) + ' - ' + str(objecte.proposalPoint))
            objecte.proposalPoint = index
            objecte.reindexObject()
            print(str(objecte.Title) + ' - ' + str(objecte.proposalPoint))
            if len(objecte.items()) > 0:
                search_path = '/'.join(objecte.getPhysicalPath())
                subpunts = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt'],
                    sort_on='getObjPositionInParent',
                    path={'query': search_path, 'depth': 1})

                subvalue = 1
                for value in subpunts:
                    newobjecte = value.getObject()
                    print(str(newobjecte.Title) + ' - ' + str(newobjecte.proposalPoint))
                    newobjecte.proposalPoint = unicode(str(index) + str('.') + str(subvalue))
                    newobjecte.reindexObject()
                    subvalue = subvalue + 1
                    print(str(newobjecte.Title) + ' - ' + str(newobjecte.proposalPoint))
            index = index + 1
        print "----punt"


@grok.subscribe(ISubpunt, IObjectRemovedEvent)
def removeSubpunt(alias, event):
    """When the alias is created,
    """
    if deletion_confirmed():
        print '___________deleting SUB punt'
        portal_catalog = getToolByName(alias, 'portal_catalog')
        folder_path = '/'.join(alias.__parent__.getPhysicalPath())
        # addEntryLog(alias, 'Reload proposalPoints manually', '')  # add log
        # agafo items ordenats!
        subpuntsOrdered = portal_catalog.searchResults(
            portal_type=['genweb.organs.subpunt'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        index = 1

        # ptool = queryUtility(IPropertiesTool)
        # props = getattr(ptool, 'site_properties', None)
        # old_check = props.getProperty('enable_link_integrity_checks', False)
        # props.enable_link_integrity_checks = False

        for item in subpuntsOrdered:
            print(str(item.Title) + ' - ' + str(item.proposalPoint))
            objecte = item.getObject()
            print(str(item.Title) + ' - ' + str(objecte.proposalPoint))
            objecte.proposalPoint = unicode(str(item.proposalPoint) + str('.') + str(index))
            objecte.reindexObject()

            print(str(item.Title) + ' - ' + str(objecte.proposalPoint))
            print "-----"

            index = index + 1

        # transaction.commit()
        # props.enable_link_integrity_checks = old_check


    transaction.commit()
