# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from operator import attrgetter
from operator import itemgetter
from plone import api
from plone.event.interfaces import IEventAccessor
from plone.folder.interfaces import IExplicitOrdering
from zope.interface import alsoProvides

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.utils import addEntryLog

import datetime
import DateTime
import json
import unicodedata

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
        if action == 'delete':

            if '/' in itemid:
                # Es tracta de subpunt i inclou punt/subpunt a itemid (segon nivell)
                folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + str('/'.join(itemid.split('/')[:-1]))
                itemid = str(''.join(itemid.split('/')[-1:]))
            else:
                # L'objecte a esborrar es a primer nivell
                folder_path = '/'.join(self.context.getPhysicalPath())

            element = portal_catalog.searchResults(
                portal_type=portal_type,
                path={'query': folder_path, 'depth': 1},
                id=itemid)

            if element:
                deleteItem = element[0].getObject()
                with api.env.adopt_roles(['OG1-Secretari']):
                    api.content.delete(deleteItem)
                portal_catalog = getToolByName(self, 'portal_catalog')
                addEntryLog(self.context, None, _(u'Deleted via javascript'), deleteItem.Title() + ' - (' + self.request.form.get('item') + ')')
                folder_path = '/'.join(self.context.getPhysicalPath())
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
                            portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                            sort_on='getObjPositionInParent',
                            path={'query': search_path, 'depth': 1})
                        subvalue = 1
                        for value in subpunts:
                            newobjecte = value.getObject()
                            newobjecte.proposalPoint = str(index) + str('.') + str(subvalue)
                            newobjecte.reindexObject()
                            subvalue = subvalue + 1
                    index = index + 1


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
        organ_tipus = self.context.organType

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


class allSessions(BrowserView):
    __call__ = ViewPageTemplateFile('views/allsessions.pt')

    def year(self):
        year = datetime.datetime.now().strftime('%Y')
        return year

    def sessions(self):
        """ Returns sessions from organs marked as public fields,
            bypassing security permissions """

        username = api.user.get_current().id
        today = DateTime.DateTime()   # Today
        date_previous_events = {'query': (today), 'range': 'max'}
        date_future_events = {'query': (today), 'range': 'min'}

        portal_catalog = getToolByName(self.context, 'portal_catalog')

        previous_sessions = portal_catalog.unrestrictedSearchResults(
            portal_type='genweb.organs.sessio',
            sort_on='start',
            sort_order='reverse',
            end=date_previous_events
        )

        future_sessions = portal_catalog.unrestrictedSearchResults(
            portal_type='genweb.organs.sessio',
            sort_on='start',
            sort_order='reverse',
            end=date_future_events
        )
        past = []
        current_year = datetime.datetime.now().strftime('%Y')
        for session in previous_sessions:
            obj = session._unrestrictedGetObject()
            roles = []
            if not api.user.is_anonymous():
                roles = api.user.get_roles(username=username, obj=obj)
            if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles or 'Manager' in roles or obj.aq_parent.visiblefields:
                event = IEventAccessor(obj)
                if obj.start.strftime('%Y') == current_year:
                    past.append(dict(
                        title=obj.aq_parent.title,
                        start=event.start.strftime('%d/%m/%Y %H:%M'),
                        end=event.end.strftime('%d/%m/%Y %H:%M'),
                        dateiso=event.start.strftime('%Y%m%d'),
                        url=session.getPath()))

        future = []
        current_year = datetime.datetime.now().strftime('%Y')
        for session in future_sessions:
            obj = session._unrestrictedGetObject()
            roles = []
            if not api.user.is_anonymous():
                roles = api.user.get_roles(username=username, obj=obj)
            if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles or 'Manager' in roles or obj.aq_parent.visiblefields:
                event = IEventAccessor(obj)
                if obj.start.strftime('%Y') == current_year:
                    future.append(dict(
                        title=obj.aq_parent.title,
                        start=event.start.strftime('%d/%m/%Y %H:%M'),
                        end=event.end.strftime('%d/%m/%Y %H:%M'),
                        dateiso=event.start.strftime('%Y%m%d'),
                        url=session.getPath()))
        return dict(
            future=sorted(future, key=itemgetter('dateiso'), reverse=False),
            past=sorted(past, key=itemgetter('dateiso'), reverse=False))


class showMembersOrgan(BrowserView):
    """ View that list all members of the organ de govern"""
    __call__ = ViewPageTemplateFile('views/members.pt')

    def getMembers(self):
        if self.context.portal_type == 'genweb.organs.organgovern':
            return self.context.membresOrgan

    def getTitle(self):
        if self.context.portal_type == 'genweb.organs.organgovern':
            return self.context.Title()
        else:
            return self.request.response.redirect(api.portal.get().absolute_url())


class findFileProperties(BrowserView):

    def __call__(self):
        # Return type properties
        #
        acta = api.content.find(portal_type='genweb.organs.acta')
        audio = api.content.find(portal_type='genweb.organs.audio')
        document = api.content.find(portal_type='genweb.organs.document')
        file = api.content.find(portal_type='genweb.organs.file')
        organgovern = api.content.find(portal_type='genweb.organs.organgovern')
        acord = api.content.find(portal_type='genweb.organs.acord')
        punt = api.content.find(portal_type='genweb.organs.punt')
        sessio = api.content.find(portal_type='genweb.organs.sessio')
        subpunt = api.content.find(portal_type='genweb.organs.subpunt')

        actas = []
        audios = []
        documents = []
        files = []
        organs = []
        acords = []
        punts = []
        sessions = []
        subpunts = []

        for item in acta:
            actas.append(dict(
                organType=item.organType,
                path=item.getPath(),
                id=item.id))
        for item in audio:
            audios.append(dict(
                organType=item.organType,
                path=item.getPath(),
                id=item.id))
        for item in document:
            documents.append(dict(
                organType=item.organType,
                path=item.getPath(),
                id=item.id))
        for item in file:
            files.append(dict(
                organType=item.organType,
                path=item.getPath(),
                id=item.id))
        for item in organgovern:
            organs.append(dict(
                organType=item.organType,
                path=item.getPath(),
                id=item.id))
        for item in acord:
            acords.append(dict(
                organType=item.organType,
                path=item.getPath(),
                id=item.id))
        for item in punt:
            punts.append(dict(
                organType=item.organType,
                path=item.getPath(),
                id=item.id))
        for item in sessio:
            sessions.append(dict(
                organType=item.organType,
                path=item.getPath(),
                id=item.id))
        for item in subpunt:
            subpunts.append(dict(
                organType=item.organType,
                path=item.getPath(),
                id=item.id))
        results = dict(
            actas=actas,
            audios=audios,
            documents=documents,
            files=files,
            organs=organs,
            acords=acords,
            punts=punts,
            sessions=sessions,
            subpunts=subpunts
        )
        return json.dumps(results)

class allOrgans(BrowserView):
    __call__ = ViewPageTemplateFile('views/allorgans.pt')

    def organsTable(self):

        all_brains = api.content.find(portal_type='genweb.organs.organgovern')
        results = []
        for brain in all_brains:
            obj = brain.getObject()
            pa = obj.getParentNode()
            roles = obj.get_local_roles()
            parent_roles = pa.get_local_roles()
            secretaris = ""
            editors = ""
            membres = ""
            afectats = ""
            if roles:
                for (username, role) in roles:
                    if 'OG1-Secretari' in role:
                        secretaris += username+ ", "
                    if 'OG2-Editor' in role:
                        editors += username+ ", "
                    if 'OG3-Membre' in role:
                        membres += username+ ", "
                    if 'OG4-Afectat' in role:
                        afectats += username+ ", "

            if parent_roles:
                for (username, role) in parent_roles:
                    if 'OG1-Secretari' in role and username not in secretaris:
                        secretaris += username+ ", "
                    if 'OG2-Editor' in role and username not in editors:
                        editors += username+ ", "
                    if 'OG3-Membre' in role and username not in secretaris:
                        membres += username+ ", "
                    if 'OG4-Afectat' in role and username not in editors:
                        afectats += username+ ", "

            if secretaris == "":
                secretaris = "-"
            else:
                secretaris = secretaris[:-2]

            if editors == "":
                editors = "-"
            else:
                editors = editors[:-2]

            if membres == "":
                membres = "-"
            else:
                membres = membres[:-2]

            if afectats == "":
                afectats = "-"
            else:
                afectats = afectats[:-2]

            elements = dict(title = obj.Title(),
                        path = obj.absolute_url(),
                        organType = obj.organType,
                        acronim= obj.acronim,
                        secretaris = secretaris,
                        editors = editors,
                        membres = membres,
                        afectats = afectats,
                        parent = pa.Title())

            if pa.getParentNode().id != "ca":
                elements['grandparent'] = pa.getParentNode().Title()
                elements['to_sort'] = elements['grandparent']
            else:
                elements['to_sort'] = elements['parent']

            results.append(elements)

            results = sorted(results, key=itemgetter('parent'))

        return sorted(results, key=itemgetter('to_sort'))


class ReorderSessions(BrowserView):
    """ Reordena sessions de la vista d'organ"""
    def __call__(self):
        """ This call reassign the correct sessions for an organ
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.searchResults(portal_type="genweb.organs.sessio")
        sessions_to_reorder = []
        acords_to_update = []
        year = datetime.datetime.now().year

        for brain in brains:
            obj = brain.getObject()
            if obj.getParentNode().id == self.context.id:
                if obj.start.year == year:
                    sessions_to_reorder.append(obj)

        sessions = sorted(sessions_to_reorder, key=attrgetter('start'))
        num_sessio = "01"
        for ses in sessions:
            if api.content.get_state(obj=ses) == 'planificada':
                ses.numSessio = num_sessio
                # then, update acords from the session with the same num
                for acord in ses.getChildNodes():
                    if acord.getPortalTypeName() == 'genweb.organs.acord':
                        if acord.agreement:
                            aux = acord.agreement.split('/')
                            aux[2] = num_sessio
                            acord.agreement = '/'.join(aux)
            else:
                num_sessio = ses.numSessio

            num_sessio = str(int(num_sessio) + 1)
            if len(num_sessio) == 1:
                num_sessio = '0' + num_sessio

        self.request.response.redirect(self.context.absolute_url())
