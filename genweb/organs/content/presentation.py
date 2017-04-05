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
from genweb.organs import _


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

            if obj.portal_type == 'genweb.organs.punt' or obj.portal_type == 'genweb.organs.acord':
                if self.Anonim():
                    item = obj._unrestrictedGetObject()
                    if len(item.objectIds()) > 0:
                        inside = True
                    else:
                        inside = False
                    if obj.portal_type == 'genweb.organs.acord':
                        if item.agreement:
                            agreement = _(u'[Acord ') + item.agreement + ']'
                        else:
                            agreement = _(u'[ACORD]')
                    else:
                        agreement = False
                    results.append(dict(title=obj.Title,
                                        absolute_url=item.absolute_url(),
                                        proposalPoint=item.proposalPoint,
                                        state=item.estatsLlista,
                                        item_path=item.absolute_url_path(),
                                        portal_type=obj.portal_type,
                                        agreement=agreement,
                                        id=obj.id,
                                        items_inside=inside))
                else:
                    item = obj.getObject()
                    if len(item.objectIds()) > 0:
                        inside = True
                    else:
                        inside = False
                    if obj.portal_type == 'genweb.organs.acord':
                        if item.agreement:
                            agreement = _(u'[Acord ') + item.agreement + ']'
                        else:
                            agreement = _(u'[ACORD]')
                    else:
                        agreement = False
                    results.append(dict(title=obj.Title,
                                        absolute_url=item.absolute_url(),
                                        proposalPoint=item.proposalPoint,
                                        state=item.estatsLlista,
                                        item_path=item.absolute_url_path(),
                                        estats=self.estatsCanvi(obj),
                                        css=self.getColor(obj),
                                        portal_type=obj.portal_type,
                                        agreement=agreement,
                                        id=obj.id,
                                        items_inside=inside))
        return results

    def SubpuntsInside(self, data):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + data['id']
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            if self.Anonim():
                item = obj._unrestrictedGetObject()
                if obj.portal_type == 'genweb.organs.acord':
                    if item.agreement:
                        agreement = _(u'[Acord ') + item.agreement + ']'
                    else:
                        agreement = _(u'[ACORD]')
                else:
                    agreement = False
                results.append(dict(title=obj.Title,
                                    absolute_url=item.absolute_url(),
                                    proposalPoint=item.proposalPoint,
                                    state=item.estatsLlista,
                                    portal_type=obj.portal_type,
                                    item_path=item.absolute_url_path(),
                                    agreement=agreement,
                                    id='/'.join(item.absolute_url_path().split('/')[-2:])))
            else:
                item = obj.getObject()
                item = obj._unrestrictedGetObject()
                if obj.portal_type == 'genweb.organs.acord':
                    if item.agreement:
                        agreement = _(u'[Acord ') + item.agreement + ']'
                    else:
                        agreement = _(u'[ACORD]')
                else:
                    agreement = False
                results.append(dict(title=obj.Title,
                                    absolute_url=item.absolute_url(),
                                    proposalPoint=item.proposalPoint,
                                    state=item.estatsLlista,
                                    portal_type=obj.portal_type,
                                    item_path=item.absolute_url_path(),
                                    estats=self.estatsCanvi(obj),
                                    css=self.getColor(obj),
                                    agreement=agreement,
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
            visibleUrl = ''
            hiddenUrl = ''
            isFile = hasPublic = hasPrivate = isGODocument = isGOFile = file = publicRAW = privateRAW = False
            visibleUrl = obj.getObject().absolute_url()
            if obj.portal_type == 'genweb.organs.file':
                isFile = True
                isGOFile = True
                tipus = 'fa fa-file-pdf-o'
                file = obj.getObject()
                publicRAW = None
                privateRAW = None
                if file.visiblefile:
                    hasPublic = True
                    visibleUrl = file.absolute_url() + '/@@display-file/visiblefile/'
                if file.hiddenfile:
                    hasPrivate = True
                    hiddenUrl = file.absolute_url() + '/@@display-file/hiddenfile/'
            else:
                # Its a document
                isGODocument = True
                tipus = 'fa fa-file-text-o'
                hasPublic = True
                visibleUrl = obj.getObject().defaultContent
                publicRAW = obj.getObject().defaultContent
                privateRAW = obj.getObject().alternateContent

            if file:
                abs_path = file.absolute_url_path()
            else:
                abs_path = None
            results.append(dict(title=obj.Title,
                                path=abs_path,
                                absolute_url=obj.getURL(),
                                isFile=isFile,
                                hasPublic=hasPublic,
                                hasPrivate=hasPrivate,
                                classCSS=tipus,
                                publicURL=visibleUrl,
                                reservedURL=hiddenUrl,
                                isGOFile=isGOFile,
                                isGODocument=isGODocument,
                                publicRAW=publicRAW,
                                privateRAW=privateRAW,
                                id=obj.id))
        return results

    def getSessionTitle(self):
        return self.context.Title()

    def getColor(self, data):
        # assign custom colors on organ states
        return utils.getColor(data)

    def estatsCanvi(self, data):
        return utils.estatsCanvi(data)

    def Anonim(self):
        username = api.user.get_current().id
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
                    return self.context.absolute_url() + '/capcalera@2x.jpg'
            except:
                return self.context.absolute_url() + '/capcalera@2x.jpg'
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
                            return obj.absolute_url() + '/capcalera@2x.jpg'
                    except:
                        return obj.absolute_url() + '/capcalera@2x.jpg'

    def hasPermission(self):
        username = api.user.get_current().id
        if username is None:
            return False
        else:
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG2-Membre' in roles:
                return True
            else:
                return False
        return False

    def wf_state(self):
        state = api.content.get_state(self.context)
        return state

    def showFile(self, item):
        username = api.user.get_current().id
        if username is None:
            if item['hasPublic'] is True:
                return True
        else:
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles:
                return True
        return False

    def showBarra(self, item):
        username = api.user.get_current().id
        if username is None:
            if item['hasPublic'] is True and item['hasPrivate'] is True:
                return True
            else:
                return False
        return False

    def changeEstat(self):
        username = api.user.get_current().id
        if username is None:
            return False
        else:
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles:
                if self.wf_state() in ['planificada', 'convocada', 'realitzada']:
                    return True
            if 'OG1-Secretari' in roles or 'Manager' in roles:
                if self.wf_state() == 'en_correccio':
                    return True
            else:
                return False
