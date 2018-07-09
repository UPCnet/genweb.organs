# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone import api
from zope.interface import alsoProvides
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from plone.folder.interfaces import IExplicitOrdering
from genweb.organs.utils import addEntryLog
from genweb.organs import _
from plone.event.interfaces import IEventAccessor
import unicodedata
from genweb.organs import utils
from AccessControl import Unauthorized

# Disable CSRF
try:
    import pkg_resources
    pkg_resources.get_distribution('plone4.csrffixes')
except pkg_resources.DistributionNotFound:
    CSRF = False
else:
    from plone.protect.interfaces import IDisableCSRFProtection
    CSRF = True


def getOrdering(context):
    if IPloneSiteRoot.providedBy(context):
        return context
    else:
        ordering = context.getOrdering()
        if not IExplicitOrdering.providedBy(ordering):
            return None
        return ordering


class createElement(BrowserView):
    """ This code is executed when pressing the two buttons in session view,
        to create an acord or a point at first level of the session """
    def __call__(self):
        # TODO: Al anadir el estado con espacio y acento lo pone mal
        # En crear el objeto no hace falta poner el log, porque
        # ya salta el HOOK y lo hace
        portal_catalog = getToolByName(self, 'portal_catalog')
        action = self.request.form.get('action')
        itemid = self.request.form.get('name')
        if itemid == '':
            pass
        else:
            try:
                value = ' '.join(self.context.estatsLlista.split('</p>')[0].rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '').split(' ')[:-1])
                estat = unicodedata.normalize("NFKD", value).encode('utf-8')
                path = '/'.join(self.context.getPhysicalPath())
            except:
                estat = ''
            if action == 'createPunt':
                items = portal_catalog.searchResults(
                    portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
                    path={'query': path,
                          'depth': 1})
                index = len(items)
                with api.env.adopt_roles(['OG1-Secretari']):
                    obj = api.content.create(
                        title=itemid,
                        type='genweb.organs.punt',
                        container=self.context)
                obj.estatsLlista = estat
                obj.proposalPoint = index + 1
            elif action == 'createAcord':
                items = portal_catalog.searchResults(
                    portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
                    path={'query': path,
                          'depth': 1})
                index = len(items)
                with api.env.adopt_roles(['OG1-Secretari']):
                    obj = api.content.create(
                        title=itemid,
                        type='genweb.organs.acord',
                        container=self.context)
                obj.estatsLlista = estat
                obj.proposalPoint = index + 1
            else:
                pass


class Delete(BrowserView):

    def __call__(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        action = self.request.form.get('action')
        itemid = self.request.form.get('item')
        portal_type = self.request.form.get('portal_type')
        try:
            if action == 'delete':
                if '/' in itemid:
                    # Es tracta de subpunt i inclou punt/subpunt a itemid (segon nivell)
                    folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + str('/'.join(itemid.split('/')[:-1]))
                    itemid = str(''.join(itemid.split('/')[-1:]))
                else:
                    # L'objecte a esborrar es a primer nivell
                    folder_path = '/'.join(self.context.getPhysicalPath())

                deleteItem = portal_catalog.searchResults(
                    portal_type=portal_type,
                    path={'query': folder_path, 'depth': 1},
                    id=itemid)[0].getObject()
                with api.env.adopt_roles(['OG1-Secretari']):
                    api.content.delete(deleteItem)
                portal_catalog = getToolByName(self, 'portal_catalog')
                folder_path = '/'.join(self.context.getPhysicalPath())
                addEntryLog(self.context, None, _(u'Deleted via javascript'), self.request.form.get('item'))

                # agafo items ordenats
                puntsOrdered = portal_catalog.searchResults(
                    portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': folder_path,
                          'depth': 1})
                index = 1
                for item in puntsOrdered:
                    objecte = item.getObject()
                    objecte.proposalPoint = index
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
                # This line is only to bypass the CSRF WARNING
                # WARNING plone.protect error parsing dom, failure to add csrf token to response for url ...
                self.request.response.redirect(self.context.absolute_url())
        except:
            self.request.response.redirect(self.context.absolute_url())


class Move(BrowserView):

    def __call__(self):
        migrated_property = hasattr(self.context, 'migrated')
        if migrated_property:
            if self.context.migrated is True:
                return

        # Disable CSRF
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)

        ordering = getOrdering(self.context)
        # authenticator = getMultiAdapter((self.context, self.request),
        #                                 name=u"authenticator")
        # if not authenticator.verify() or \
        #         self.request['REQUEST_METHOD'] != 'POST':
        #     raise Unauthorized

        #  ./wildcard.foldercontents-1.2.7-py2.7.egg/wildcard/foldercontents/
        portal_catalog = getToolByName(self, 'portal_catalog')
        action = self.request.form.get('action')
        itemid = self.request.form.get('itemid')

        if action == 'movepunt':
            # move contents through the table
            ordering = getOrdering(self.context)
            folder_path = '/'.join(self.context.getPhysicalPath())
            delta = int(self.request.form['delta'])
            ordering.moveObjectsByDelta(itemid, delta)
            # Els ids es troben ordenats, cal canviar el proposalPoint
            # agafo items ordenats!
            puntsOrdered = portal_catalog.searchResults(
                portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
                sort_on='getObjPositionInParent',
                path={'query': folder_path,
                      'depth': 1})
            index = 1
            for item in puntsOrdered:
                objecte = item.getObject()
                objecte.proposalPoint = unicode(str(index))
                addEntryLog(self.context, None, _(u'Changed punt number with drag&drop'), str(objecte.id) + ' → ' + str(objecte.proposalPoint))
                objecte.reindexObject()

                if len(objecte.items()) > 0:
                    search_path = '/'.join(objecte.getPhysicalPath())
                    subpunts = portal_catalog.searchResults(
                        portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                        sort_on='getObjPositionInParent',
                        path={'query': search_path, 'depth': 1})
                    subvalue = 1
                    for value in subpunts:
                        newobjecte = value.getObject()
                        newobjecte.proposalPoint = unicode(str(index) + str('.') + str(subvalue))
                        newobjecte.reindexObject()
                        subvalue = subvalue + 1
                index = index + 1

        # Volem moure un subpunt
        if action == 'movesubpunt':
            # move subpunts contents through the table
            # Esbrino id del pare (punt)
            search_path = '/'.join(self.context.getPhysicalPath())
            punt = portal_catalog.searchResults(
                id=str(itemid.split('/')[0]),
                portal_type='genweb.organs.punt',
                path={'query': search_path, 'depth': 1})[0].getObject()
            ordering = getOrdering(punt)
            itemid = str(itemid.split('/')[1])
            folder_path = '/'.join(punt.getPhysicalPath())

            delta = int(self.request.form['delta'])
            ordering.moveObjectsByDelta(itemid, delta)
            # Els ids ja s'han mogut, cal afegir el proposalPoint pertinent.
            subpuntsOrdered = portal_catalog.searchResults(
                portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                sort_on='getObjPositionInParent',
                path={'query': folder_path,
                      'depth': 1})

            subvalue = 1
            puntnumber = punt.proposalPoint
            # Change proposalpoints dels subpunts ordenats
            for item in subpuntsOrdered:
                if item.portal_type == 'genweb.organs.subpunt' or item.portal_type == 'genweb.organs.acord':
                    objecteSubPunt = item.getObject()
                    objecteSubPunt.proposalPoint = unicode(str(puntnumber) + '.' + str(subvalue))
                    addEntryLog(self.context, None, _(u'Moved subpunt by drag&drop'), str(objecteSubPunt.id) + ' → ' + str(objecteSubPunt.proposalPoint))
                    objecteSubPunt.reindexObject()
                    subvalue = subvalue + 1

        # This line is only to bypass the CSRF WARNING
        # WARNING plone.protect error parsing dom, failure to add csrf token to response for url ...
        return "Moved element"


class ActaPrintView(BrowserView):

    __call__ = ViewPageTemplateFile('views/acta_print.pt')

    def unitatTitle(self):
        """ Get organGovern Title used for printing the acta """
        return self.aq_parent.aq_parent.aq_parent.aq_parent.Title()

    def organGovernTitle(self):
        """ Get organGovern Title used for printing the acta """
        return self.aq_parent.aq_parent.aq_parent.Title()

    def sessionTitle(self):
        """ Get organGovern Title used for printing the acta """
        return self.aq_parent.aq_parent.Title()

    def getActaLogo(self):
        """ Getlogo to use in print """
        try:
            self.context.aq_parent.aq_parent.logoOrgan.filename
            return self.context.aq_parent.aq_parent.absolute_url() + '/@@images/logoOrgan'
        except:
            return None

    def signatura(self):
        return self.context.aq_parent.aq_parent.footer

    def getActaContent(self):
        """ Retorna els punt en format text per mostrar a l'ordre
            del dia de les actes
        """
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        folder_path = '/'.join(self.context.aq_parent.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        results.append('<div class="num_acta"> <ol>')
        for obj in values:
            # value = obj.getObject()
            value = obj._unrestrictedGetObject()
            if value.portal_type == 'genweb.organs.acord':
                if value.agreement:
                    agreement = ' [Acord ' + str(value.agreement) + ']'
                else:
                    agreement = _(u"[Acord sense numerar]")
            else:
                agreement = ''
            results.append('<li>' + str(obj.Title) + ' ' + str(agreement))

            if len(value.objectIds()) > 0:
                valuesInside = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': obj.getPath(),
                          'depth': 1})

                results.append('<ol>')
                for item in valuesInside:
                    subpunt = item.getObject()
                    if subpunt.portal_type == 'genweb.organs.acord':
                        if subpunt.agreement:
                            agreement = ' [Acord ' + str(subpunt.agreement) + ']'
                        else:
                            agreement = _("[Acord sense numerar]")
                    else:
                        agreement = ''
                    results.append('<li>' + str(item.Title) + ' ' + str(agreement) + '</li>')
                results.append('</ol></li>')
            else:
                results.append('</li>')

        results.append('</ol> </div>')

        return ''.join(results)

    def canView(self):
        # Permissions to GENERATE PRINT acta view
        if utils.isManager(self):
            return True
        estatSessio = utils.session_wf_state(self)

        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        else:
            raise Unauthorized


class ActaPreviewView(ActaPrintView):

    __call__ = ViewPageTemplateFile('views/acta_preview.pt')


class ReloadAcords(BrowserView):
    """ Numera acords de la vista de la sessio """
    def __call__(self):
        """ This call reassign the correct proposalPoints to the contents in this folder
        """
        migrated_property = hasattr(self.context, 'migrated')
        if migrated_property:
            if self.context.migrated is True:
                return

        # Disable CSRF
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)

        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        acro_parent = getattr(self.context.aq_parent, 'acronim', None)

        if acro_parent:
            acronim = str(self.context.aq_parent.acronim) + '/'
        else:
            acronim = ''
        acc = IEventAccessor(self.context)
        if acc.start:
            any = str(acc.start.strftime('%Y')) + '/'
        else:
            any = ''

        numero = getattr(self.context, 'numSessio', None)
        if numero:
            numsessio = str(self.context.numSessio) + '/'
        else:
            numsessio = ''

        addEntryLog(self.context, None, _(u'Reload proposalPoints manually'), '')  # add log
        # agafo items ordenats!
        puntsOrdered = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        idacord = 1
        index = 1
        for item in puntsOrdered:
            objecte = item.getObject()
            if item.portal_type == 'genweb.organs.acord':
                printid = '{0}'.format(str(idacord).zfill(2))
                objecte.agreement = acronim + any + numsessio + printid
                idacord = idacord + 1

            if len(objecte.items()) > 0:
                search_path = '/'.join(objecte.getPhysicalPath())
                subpunts = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': search_path, 'depth': 1})

                subvalue = 1
                for value in subpunts:
                    newobjecte = value.getObject()
                    subvalue = subvalue + 1
                    if value.portal_type == 'genweb.organs.acord':
                        printid = '{0}'.format(str(idacord).zfill(2))
                        newobjecte.agreement = acronim + any + numsessio + printid
                        idacord = idacord + 1

            index = index + 1

        return self.request.response.redirect(self.context.absolute_url())


class ReloadPoints(BrowserView):
    """ Renumera els punts manualment """
    def __call__(self):
        """ This call reassign the correct Point number to the contents in this folder
        """
        migrated_property = hasattr(self.context, 'migrated')
        if migrated_property:
            if self.context.migrated is True:
                return

        # Disable CSRF
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)

        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())

        addEntryLog(self.context, None, _(u'Reload points manually'), '')  # add log
        # agafo items ordenats!
        puntsOrdered = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        index = 1
        for item in puntsOrdered:
            objecte = item.getObject()
            objecte.proposalPoint = unicode(str(index))
            objecte.reindexObject()

            if len(objecte.items()) > 0:
                search_path = '/'.join(objecte.getPhysicalPath())
                subpunts = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': search_path, 'depth': 1})
                subvalue = 1
                for value in subpunts:
                    newobjecte = value.getObject()
                    newobjecte.proposalPoint = unicode(str(index) + str('.') + str(subvalue))
                    newobjecte.reindexObject()
                    subvalue = subvalue + 1

            index = index + 1

        return self.request.response.redirect(self.context.absolute_url())


class changeActualState(BrowserView):
    """ Es fa servir a la vista sessio i presentacio. No cal fer reload perque
        es mostra el nou valor per JS
    """
    def __call__(self):
        # Disable CSRF
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)

        portal_catalog = getToolByName(self, 'portal_catalog')
        estat = self.request.form.get('estat')
        itemid = self.request.form.get('id')

        try:
            object_path = '/'.join(self.context.getPhysicalPath())
            item = str(itemid.split('/')[-1:][0])
            currentitem = portal_catalog.searchResults(
                portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
                id=item,
                path={'query': object_path,
                      'depth': 1})[0].getObject()
            if currentitem.portal_type == 'genweb.organs.punt':
                # es un punt i cal mirar a tots els de dintre...
                id = itemid.split('/')[-1:][0]
                items_inside = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    path={'query': object_path + '/' + id,
                          'depth': 1})
                for subpunt in items_inside:
                    objecte = subpunt.getObject()
                    objecte.estatsLlista = estat
                    if objecte.portal_type == 'genweb.organs.subpunt':
                        addEntryLog(self.context, None, _(u'Changed recursive color state of subpunt inside punt'), objecte.absolute_url_path() + ' -> ' + estat)  # add log
                    else:
                        addEntryLog(self.context, None, _(u'Changed recursive color state of acord inside punt'), objecte.absolute_url_path() + ' -> ' + estat)  # add log
                currentitem.estatsLlista = estat
                addEntryLog(self.context, None, _(u'Changed punt color state'), itemid + ' → ' + estat)  # add log
            else:
                # És un acord. Només es canvia aquest ja que dintre no conté elements
                currentitem.estatsLlista = estat
                addEntryLog(self.context, None, _(u'Changed acord color state'), itemid + ' → ' + estat)  # add log
        except:
            pass
        return


class changeSubpuntState(BrowserView):
    """ Es fa servir a la vista sessio i presentacio. No cal fer reload perque
        es mostra el nou valor per JS. Només canvia el subpunt actual, no recursiu.
    """
    def __call__(self):
        # Disable CSRF
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)

        portal_catalog = getToolByName(self, 'portal_catalog')
        estat = self.request.form.get('estat')
        itemid = self.request.form.get('id')
        object_path = '/'.join(self.context.getPhysicalPath()) + '/' + str(itemid.split('/')[0])
        item = str(itemid.split('/')[-1:][0])
        currentitem = portal_catalog.searchResults(
            portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
            id=item,
            path={'query': object_path,
                  'depth': 1})
        if currentitem:
            currentitem[0].getObject().estatsLlista = estat
            if currentitem[0].portal_type == 'genweb.organs.subpunt':
                addEntryLog(self.context, None, _(u'Changed subpunt intern state color'), currentitem[0].getPath() + ' → ' + estat)  # add log
            else:
                addEntryLog(self.context, None, _(u'Changed acord intern state color'), currentitem[0].getPath() + ' → ' + estat)  # add log

        return


class Butlleti(BrowserView):
    __call__ = ViewPageTemplateFile('views/butlleti.pt')

    def status(self):
        return api.content.get_state(obj=self.context)

    def PuntsOrdreDelDia(self):
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            # value = obj.getObject()
            value = obj._unrestrictedGetObject()
            if value.portal_type == 'genweb.organs.acord':
                if value.agreement:
                    agreement = value.agreement
                else:
                    agreement = _(u"sense numeracio")
            else:
                agreement = False
            results.append(dict(Title=obj.Title,
                                url=value.absolute_url_path(),
                                punt=value.proposalPoint,
                                acord=agreement))
            if len(value.objectIds()) > 0:
                # valuesInside = portal_catalog.searchResults(
                valuesInside = portal_catalog.unrestrictedSearchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': obj.getPath(),
                          'depth': 1})
                for item in valuesInside:
                    # subpunt = item.getObject()
                    subpunt = item._unrestrictedGetObject()
                    if subpunt.portal_type == 'genweb.organs.acord':
                        if subpunt.agreement:
                            agreement = subpunt.agreement
                        else:
                            agreement = _(u"sense numeracio")
                    else:
                        agreement = False
                    results.append(dict(Title=item.Title,
                                        url=subpunt.absolute_url_path(),
                                        punt=subpunt.proposalPoint,
                                        acord=agreement))
        return results

    def getTitle(self):
        return self.context.Title()

    def getOrganTitle(self):
        return self.context.aq_parent.Title()

    def getUnitat(self):
        return self.context.aq_parent.aq_parent.Title()

    def canView(self):
        # Permissions to GENERATE BUTLLETI
        if utils.isManager(self):
            return True
        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.aq_parent.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'tancada':
                return True
            elif estatSessio == 'en_correccio':
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_members_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_affected_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            else:
                raise Unauthorized
