# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_inner

from plone import api
from plone.app.layout.navigation.root import getNavigationRootObject
from z3c.form import form
from plone.supermodel import model

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.content.sessio.sessio import ISessio
from genweb.organs.interfaces import IGenwebOrgansLayer


class IPresentation(model.Schema):
    """ Plantilla del mode presentacio: /presentation
    """


class Presentation(form.Form):
    def status(self):
        return api.content.get_state(obj=self.context)

    def PuntsInside(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
                            agreement = _(u'[Acord sense numeracio]') if not getattr(item, 'omitAgreement', False) else False
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
                            agreement = _(u'[Acord sense numeracio]') if not getattr(item, 'omitAgreement', False) else False
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
        """ Retorna les sessions i el seu contingut
        """
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
                        agreement = _(u'[Acord sense numeracio]') if not getattr(item, 'omitAgreement', False) else False
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
                        agreement = _(u'[Acord sense numeracio]') if not getattr(item, 'omitAgreement', False) else False
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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        session_path = '/'.join(self.context.getPhysicalPath()) + '/' + item['id']
        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file', 'genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': session_path,
                  'depth': 1})
        results = []
        for obj in values:
            visibleUrl = ''
            hiddenUrl = ''
            hasPublic = hasPrivate = isGODocument = isGOFile = file = raw_content = listFile = False
            visibleUrl = obj.getObject().absolute_url()
            anonymous = api.user.is_anonymous()
            file = obj.getObject()
            if anonymous:
                if obj.portal_type == 'genweb.organs.file':
                    classCSS = 'bi bi-file-earmark-pdf'
                    abs_path = file.absolute_url_path()
                    isGOFile = True
                    if file.visiblefile and file.hiddenfile:
                        hasPublic = True
                        hasPrivate = False
                        visibleUrl = file.absolute_url() + '/@@display-file/visiblefile/' + file.visiblefile.filename
                        hiddenUrl = ''
                        listFile = True
                    elif file.visiblefile:
                        hasPublic = True
                        hasPrivate = False
                        visibleUrl = file.absolute_url() + '/@@display-file/visiblefile/' + file.visiblefile.filename
                        listFile = True
                        hiddenUrl = ''
                if obj.portal_type == 'genweb.organs.document':
                    classCSS = 'bi bi-file-earmark-text'
                    abs_path = None
                    isGODocument = True
                    if file.alternateContent and file.defaultContent:
                        hasPublic = True
                        hasPrivate = False
                        listFile = True
                        raw_content = file.defaultContent
                    elif file.defaultContent:
                        hasPublic = True
                        hasPrivate = False
                        listFile = True
                        raw_content = file.defaultContent

                if listFile:
                    results.append(dict(title=obj.Title,
                                        path=abs_path,
                                        absolute_url=obj.getURL(),
                                        hasPublic=hasPublic,
                                        hasPrivate=hasPrivate,
                                        classCSS=classCSS,
                                        publicURL=visibleUrl,
                                        reservedURL=hiddenUrl,
                                        isGOFile=isGOFile,
                                        isGODocument=isGODocument,
                                        raw_content=raw_content,
                                        id=obj.id))
            else:
                # user is validated
                username = api.user.get_current().id
                if obj.portal_type == 'genweb.organs.file':
                    # Tractem els files i fiquem colors...
                    isGOFile = True
                    raw_content = None
                    abs_path = file.absolute_url_path()
                    roles = api.user.get_roles(username=username, obj=self.context)
                    classCSS = 'bi bi-file-earmark-pdf'
                    if file.visiblefile and file.hiddenfile:
                        if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                            hasPublic = False
                            hasPrivate = True
                            visibleUrl = ''
                            hiddenUrl = file.absolute_url() + '/@@display-file/hiddenfile/' + file.hiddenfile.filename
                            classCSS = 'bi bi-file-earmark-pdf text-success double-icon'
                        elif 'OG4-Afectat' in roles:
                            hasPublic = True
                            hasPrivate = False
                            visibleUrl = file.absolute_url() + '/@@display-file/visiblefile/' + file.visiblefile.filename
                            hiddenUrl = ''
                            classCSS = 'bi bi-file-earmark-pdf text-success'
                    elif file.hiddenfile:
                        if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                            hasPublic = False
                            hasPrivate = True
                            visibleUrl = ''
                            hiddenUrl = file.absolute_url() + '/@@display-file/hiddenfile/' + file.hiddenfile.filename
                            classCSS = 'bi bi-file-earmark-pdf text-danger'
                    elif file.visiblefile:
                        hasPublic = True
                        hasPrivate = False
                        visibleUrl = file.absolute_url() + '/@@display-file/visiblefile/' + file.visiblefile.filename
                        hiddenUrl = ''
                        classCSS = 'bi bi-file-earmark-pdf text-success'

                if obj.portal_type == 'genweb.organs.document':
                    isGODocument = True
                    abs_path = None
                    roles = api.user.get_roles(username=username, obj=self.context)
                    classCSS = 'bi bi-file-earmark-text'
                    if file.alternateContent and file.defaultContent:
                        if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                            hasPublic = False
                            hasPrivate = True
                            raw_content = file.alternateContent
                            classCSS = 'bi bi-file-earmark-text text-success double-icon'
                        elif 'OG4-Afectat' in roles:
                            hasPublic = True
                            hasPrivate = False
                            raw_content = file.defaultContent
                            classCSS = 'bi bi-file-earmark-text text-success'
                    elif file.defaultContent:
                        if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                            hasPublic = False
                            hasPrivate = True
                            raw_content = file.defaultContent
                            classCSS = 'bi bi-file-earmark-text text-success'
                    elif file.alternateContent:
                        if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                            hasPublic = False
                            hasPrivate = True
                            raw_content = file.alternateContent
                            classCSS = 'bi bi-file-earmark-text text-danger'

                results.append(dict(title=obj.Title,
                                    path=abs_path,
                                    absolute_url=obj.getURL(),
                                    hasPublic=hasPublic,
                                    hasPrivate=hasPrivate,
                                    classCSS=classCSS,
                                    publicURL=visibleUrl,
                                    reservedURL=hiddenUrl,
                                    isGOFile=isGOFile,
                                    isGODocument=isGODocument,
                                    raw_content=raw_content,
                                    id=obj.id))
        return results

    def getSessionTitle(self):
        # obtenir titlo de la session
        return self.context.Title()

    def getColor(self, data):
        # assign custom colors on organ states
        return utils.getColor(data)

    def estatsCanvi(self, data):
        return utils.estatsCanvi(data)

    def Anonim(self):
        try:
            username = api.user.get_current().id
            if username is None:
                return True
            else:
                return False

        except:
            return False

    def getTitle(self):
        from genweb.organs.content.organsfolder.organsfolder import IOrgansfolder
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
        from genweb.organs.content.organsfolder.organsfolder import IOrgansfolder
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
        if api.user.is_anonymous():
            return False
        else:
            username = api.user.get_current().id
            if username is None:
                return False
            else:
                roles = api.user.get_roles(username=username, obj=self.context)
                if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                    return True
                else:
                    return False
            return False

    def wf_state(self):
        state = api.content.get_state(self.context)
        return state

    def showBarra(self, item):
        username = api.user.get_current().id
        if username is None:
            if item['hasPublic'] is True and item['hasPrivate'] is True:
                return True
            else:
                return False
        return False

    def changeEstat(self):
        if api.user.is_anonymous():
            return False
        else:
            username = api.user.get_current().id
            if username is None:
                return False
            else:
                roles = api.user.get_roles(username=username, obj=self.context)
                if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles):
                    if self.wf_state() in ['planificada', 'convocada', 'realitzada']:
                        return True
                if utils.checkhasRol(['Manager', 'OG1-Secretari'], roles):
                    if self.wf_state() == 'en_correccio':
                        return True
                else:
                    return False

    def canView(self):
        # Permissions to view acords based on ODT definition file
        # TODO: add if is obert /restricted to ...
        estatSessio = utils.session_wf_state(self)
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True
        elif estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
            return True
        elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        else:
            raise Unauthorized
