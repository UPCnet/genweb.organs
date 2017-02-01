# -*- coding: utf-8 -*-
from plone import api
from five import grok
from plone.directives import form
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs.content.sessio import ISessio
from Products.CMFCore.utils import getToolByName
from plone.app.layout.navigation.root import getNavigationRootObject
from Acquisition import aq_inner
from genweb.organs import utils

grok.templatedir("templates")


class IPresentation(form.Schema):
    """ Define the fields of this form
    """


class Presentation(form.SchemaForm):
    grok.name('presentation')
    grok.context(ISessio)
    grok.template("presentation")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    def PuntsInside(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            if obj.portal_type == 'genweb.organs.punt':
                if self.Anonim():
                    item = obj._unrestrictedGetObject()
                    results.append(dict(title=obj.Title,
                                        absolute_url=item.absolute_url(),
                                        proposalPoint=item.proposalPoint,
                                        state=item.estatsLlista,
                                        agreement=item.agreement,
                                        item_path=item.absolute_url_path(),
                                        portal_type=obj.portal_type,
                                        id=obj.id))
                else:
                    item = obj.getObject()
                    results.append(dict(title=obj.Title,
                                        absolute_url=item.absolute_url(),
                                        proposalPoint=item.proposalPoint,
                                        state=item.estatsLlista,
                                        agreement=item.agreement,
                                        item_path=item.absolute_url_path(),
                                        estats=self.estatsCanvi(obj),
                                        css=self.getColor(obj),
                                        portal_type=obj.portal_type,
                                        id=obj.id))
        return results

    def SubpuntsInside(self, data):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + data['id']
        values = portal_catalog.unrestrictedSearchResults(
            portal_type='genweb.organs.subpunt',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            if self.Anonim():
                item = obj._unrestrictedGetObject()
                results.append(dict(title=obj.Title,
                                    absolute_url=item.absolute_url(),
                                    proposalPoint=item.proposalPoint,
                                    state=item.estatsLlista,
                                    agreement=item.agreement,
                                    portal_type=obj.portal_type,
                                    item_path=item.absolute_url_path(),
                                    id='/'.join(item.absolute_url_path().split('/')[-2:])))
            else:
                item = obj.getObject()
                results.append(dict(title=obj.Title,
                                    absolute_url=item.absolute_url(),
                                    proposalPoint=item.proposalPoint,
                                    state=item.estatsLlista,
                                    agreement=item.agreement,
                                    portal_type=obj.portal_type,
                                    item_path=item.absolute_url_path(),
                                    estats=self.estatsCanvi(obj),
                                    css=self.getColor(obj),
                                    id='/'.join(item.absolute_url_path().split('/')[-2:])))
        return results

    def filesinside(self, item):
        portal_catalog = getToolByName(self, 'portal_catalog')
        session_path = '/'.join(self.context.getPhysicalPath()) + '/' + item['id']

        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.file', 'genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': session_path,
                  'depth': 1})
        results = []
        for obj in values:
            if obj.hiddenfile is True:
                continue
            else:
                if obj.portal_type == 'genweb.organs.file':
                    tipus = 'fa fa-file-pdf-o'
                else:
                    tipus = 'fa fa-file-text-o'

                results.append(dict(title=obj.Title,
                                    absolute_url=obj.getURL(),
                                    classCSS=tipus))
        return results

    def getSessionTitle(self):
        return self.context.Title()

    def getColor(self, data):
        # assign custom colors on organ states
        return utils.getColor(data)

    def estatsCanvi(self, data):
        return utils.estatsCanvi(data)

    def Anonim(self):
        username = api.user.get_current().getProperty('id')
        if username is None:
            return True
        else:
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles:
                return False
            else:
                return True

    def getTitle(self):
        from genweb.organs.content.organsfolder import IOrgansfolder
        if IOrgansfolder.providedBy(self.context):
            if self.context.customImage:
                return 'Govern UPC - ' + str(self.context.title)
            else:
                return 'Govern UPC'
        else:
            portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
            root = getNavigationRootObject(self.context, portal_state.portal())
            physical_path = aq_inner(self.context).getPhysicalPath()
            relative = physical_path[len(root.getPhysicalPath()):]
            for i in range(len(relative)):
                now = relative[:i + 1]
                try:
                    # Some objects in path are in pending state
                    obj = aq_inner(root.restrictedTraverse(now))
                except:
                    # return default image
                    return None
                if IOrgansfolder.providedBy(obj):
                    if self.context.customImage:
                        return 'Govern UPC - ' + str(obj.title)
                    else:
                        return 'Govern UPC'

    def getLogo(self):
        from genweb.organs.content.organsfolder import IOrgansfolder
        if IOrgansfolder.providedBy(self.context):
            try:
                if self.context.customImage:
                    self.context.logoOrganFolder.filename
                    return self.context.absolute_url() + '/@@images/logoOrganFolder'
                else:
                    return None
            except:
                return None
        else:
            portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
            root = getNavigationRootObject(self.context, portal_state.portal())
            physical_path = aq_inner(self.context).getPhysicalPath()
            relative = physical_path[len(root.getPhysicalPath()):]
            for i in range(len(relative)):
                now = relative[:i + 1]
                try:
                    # Some objects in path are in pending state
                    obj = aq_inner(root.restrictedTraverse(now))
                except:
                    # return default image
                    return None
                if IOrgansfolder.providedBy(obj):
                    try:
                        if self.context.customImage:
                            obj.logoOrganFolder.filename
                            return obj.absolute_url() + '/@@images/logoOrganFolder'
                        else:
                            return None
                    except:
                        return None  # loads default image
