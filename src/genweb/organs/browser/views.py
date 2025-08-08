# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from io import StringIO

from operator import attrgetter
from operator import itemgetter
from plone import api
from plone.event.interfaces import IEventAccessor
from plone.folder.interfaces import IExplicitOrdering
from zope.interface import alsoProvides
from zope.i18n import translate

from genweb6.core.utils import json_response
from genweb.organs import _
from genweb.organs import utils
from genweb.organs.indicators.updating import update_indicators
from genweb.organs.utils import addEntryLog
from genweb.organs.utils import get_settings_property
from genweb.organs.utils import getLdapUserData

import ast
import csv
import datetime
import DateTime
import json
import transaction
import unicodedata
import time

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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        action = self.request.form.get('action')
        itemid = self.request.form.get('name')

        if not itemid:
            return

        # Get default state (Plone 6 compatible) and path
        default_estat = None
        path = '/'.join(self.context.getPhysicalPath())
        try:
            organ = utils.get_organ(self.context)
            estatsLlista = organ.estatsLlista
            if estatsLlista:
                if hasattr(estatsLlista, 'raw'):
                    valor_cru = estatsLlista.raw
                else:
                    valor_cru = estatsLlista
                estat_tag = valor_cru.split('</p>')[0]
                estat_text = unicodedata.normalize("NFKD", estat_tag).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\\r\\n', '')
                default_estat = ' '.join(estat_text.split()[:-1]).lstrip()
        except Exception:
            # If anything fails, default_estat remains None, which is fine.
            pass

        # Calculate proposalPoint based on existing items, respecting permissions
        items = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            path={'query': path, 'depth': 1})
        proposal_point_number = str(len(items) + 1)

        if action == 'createPunt':
            with api.env.adopt_roles(['OG1-Secretari', 'Manager']):
                new_obj = api.content.create(
                    type='genweb.organs.punt',
                    title=itemid,
                    container=self.context,
                    safe_id=True,
                    proposalPoint=proposal_point_number
                )
            if default_estat:
                new_obj.estatsLlista = default_estat

        elif action == 'createAcord':
            acords_p = portal_catalog.searchResults(
                portal_type=['genweb.organs.acord'],
                path={'query': path, 'depth': 1})
            agreement_count = str(len(acords_p) + 1)
            year = str(datetime.date.today().year)
            agreement_number = f"{agreement_count}/{year}"

            with api.env.adopt_roles(['OG1-Secretari', 'Manager']):
                new_obj = api.content.create(
                    type='genweb.organs.acord',
                    title=itemid,
                    container=self.context,
                    safe_id=True,
                    agreement=agreement_number,
                    proposalPoint=proposal_point_number
                )
            if default_estat:
                new_obj.estatsLlista = default_estat
        else:
            return

        new_obj.reindexObject()

        # Return JSON response for AJAX calls
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps({'status': 'success', 'id': new_obj.id})


class Delete(BrowserView):

    def __call__(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        action = self.request.form.get('action')
        itemid = self.request.form.get('id')  # Changed from 'item' to 'id' to match JavaScript
        portal_type = self.request.form.get('type')  # Changed from 'portal_type' to 'type' to match JavaScript

        if action == 'delete' and itemid and portal_type:
            try:
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
                    portal_catalog = api.portal.get_tool(name='portal_catalog')
                    addEntryLog(self.context, None, _(u'Deleted via javascript'), deleteItem.Title() + ' - (' + itemid + ')')
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

                    # Return JSON response for AJAX calls
                    self.request.response.setHeader('Content-Type', 'application/json')
                    return json.dumps({'status': 'success'})
                else:
                    self.request.response.setHeader('Content-Type', 'application/json')
                    return json.dumps({'status': 'error', 'message': 'Element not found'})
            except Exception as e:
                self.request.response.setHeader('Content-Type', 'application/json')
                return json.dumps({'status': 'error', 'message': str(e)})
        else:
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps({'status': 'error', 'message': 'Invalid parameters'})


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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
                objecte.proposalPoint = str(index)
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
                        newobjecte.proposalPoint = str(index) + str('.') + str(subvalue)
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
                    objecteSubPunt.proposalPoint = str(puntnumber) + '.' + str(subvalue)
                    addEntryLog(self.context, None, _(u'Moved subpunt by drag&drop'), str(objecteSubPunt.id) + ' → ' + str(objecteSubPunt.proposalPoint))
                    objecteSubPunt.reindexObject()
                    subvalue = subvalue + 1

        # This line is only to bypass the CSRF WARNING
        # WARNING plone.protect error parsing dom, failure to add csrf token to response for url ...
        return "Moved element"


class ActaPrintView(BrowserView):

    __call__ = ViewPageTemplateFile('views/acta_print.pt')

    # Helpers seguros para navegar la jerarquía sin depender de aq_* en la vista
    def _sessio(self):
        """Devuelve el objeto sesión (parent inmediato del acta)."""
        return getattr(self.context, 'aq_parent', None)

    def _organgovern(self):
        """Devuelve el órgano de govern (dos niveles arriba)."""
        sessio = self._sessio()
        return getattr(sessio, 'aq_parent', None)

    def _unitat(self):
        """Devuelve la unitat contenedora (tres/cuatro niveles arriba)."""
        organ = self._organgovern()
        return getattr(organ, 'aq_parent', None)

    def unitatTitle(self):
        """Título de la unitat para impresión del acta."""
        unitat = self._unitat()
        return unitat.Title() if unitat is not None else ''

    def organGovernTitle(self):
        organ = self._organgovern()
        return organ.Title() if organ is not None else ''

    def sessionTitle(self):
        sessio = self._sessio()
        return sessio.Title() if sessio is not None else ''

    def sessionModality(self):
        sessio = self._sessio()
        return getattr(sessio, 'modality', None)

    def getActaLogo(self):
        """Devuelve la URL del logo del òrgan si existe."""
        organ = self._organgovern()
        if organ is not None and getattr(organ, 'logoOrgan', None):
            try:
                organ.logoOrgan.filename  # Asegura que hay imagen
                return organ.absolute_url() + '/@@images/logoOrgan'
            except Exception:
                return None
        return None

    def signatura(self):
        return self.context.aq_parent.aq_parent.footer

    def getActaContent(self):
        """ Retorna els punt en format text per mostrar a l'ordre
            del dia de les actes
        """
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
                    agreement = _(u"[Acord sense numerar]") if not getattr(value, 'omitAgreement', False) else ''
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
                        agreement = ' [Acord ' + str(subpunt.agreement) + ']'
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
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
            return True
        elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif organ_tipus == 'open_organ' and estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
            return True
        elif organ_tipus != 'open_organ' and estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
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

        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
                objecte.omitAgreement = False
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
                        newobjecte.omitAgreement = False
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

        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
            objecte.proposalPoint = str(index)
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

        return self.request.response.redirect(self.context.absolute_url())


class changeActualState(BrowserView):
    """ Es fa servir a la vista sessio i presentacio. No cal fer reload perque
        es mostra el nou valor per JS
    """
    def __call__(self):
        # Disable CSRF
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)

        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
                transaction.commit()
                addEntryLog(self.context, None, _(u'Changed punt color state'), itemid + ' → ' + estat)  # add log
            else:
                # És un acord. Només es canvia aquest ja que dintre no conté elements
                currentitem.estatsLlista = estat
                transaction.commit()
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

        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
            transaction.commit()
            if currentitem[0].portal_type == 'genweb.organs.subpunt':
                addEntryLog(self.context, None, _(u'Changed subpunt intern state color'), currentitem[0].getPath() + ' → ' + estat)  # add log
            else:
                addEntryLog(self.context, None, _(u'Changed acord intern state color'), currentitem[0].getPath() + ' → ' + estat)  # add log

        return


class allSessions(BrowserView):
    __call__ = ViewPageTemplateFile('views/allsessions.pt')

    def year(self):
        year = datetime.datetime.now().strftime('%Y')
        return year

    def sessions(self):
        """ Returns sessions from organs marked as public fields,
            bypassing security permissions """

        today = DateTime.DateTime()   # Today
        date_previous_events = {'query': (today), 'range': 'max'}
        date_future_events = {'query': (today), 'range': 'min'}

        portal_catalog = api.portal.get_tool(name='portal_catalog')

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
            roles = utils.getUserRoles(self, obj, api.user.get_current().id)
            if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles) or obj.aq_parent.visiblefields:
                event = IEventAccessor(obj)
                if obj.start.strftime('%Y') == current_year:
                    startDate = event.start.strftime('%d/%m/%Y')
                    endDate = event.end.strftime('%d/%m/%Y')
                    past.append(dict(
                        id=obj.aq_parent.id,
                        title=obj.aq_parent.title,
                        date=startDate if startDate == endDate else startDate + " " + endDate,
                        start=event.start.strftime('%H:%M'),
                        end=event.end.strftime('%H:%M'),
                        dateiso=event.start.strftime('%Y%m%d'),
                        url=session.getPath(),
                        breakline=obj.aq_parent.id=='ple-del-consell-social'))

        future = []
        current_year = datetime.datetime.now().strftime('%Y')
        for session in future_sessions:
            obj = session._unrestrictedGetObject()
            roles = utils.getUserRoles(self, obj, api.user.get_current().id)
            if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles) or obj.aq_parent.visiblefields:
                event = IEventAccessor(obj)
                if obj.start.strftime('%Y') == current_year:
                    startDate = event.start.strftime('%d/%m/%Y')
                    endDate = event.end.strftime('%d/%m/%Y')
                    future.append(dict(
                        id=obj.aq_parent.id,
                        title=obj.aq_parent.title,
                        date=startDate if startDate == endDate else startDate + " " + endDate,
                        start=event.start.strftime('%H:%M'),
                        end=event.end.strftime('%H:%M'),
                        dateiso=event.start.strftime('%Y%m%d'),
                        url=session.getPath(),
                        breakline=obj.aq_parent.id=='ple-del-consell-social'))
        return dict(
            future=sorted(future, key=itemgetter('dateiso'), reverse=False),
            past=sorted(past, key=itemgetter('dateiso'), reverse=False))


class showMembersOrgan(BrowserView):
    """ View that list all members of the organ de govern"""
    __call__ = ViewPageTemplateFile('views/members.pt')

    def getMembers(self):
        if self.context.portal_type == 'genweb.organs.organgovern':
            if self.context.membresOrgan is not None:
                return self.context.membresOrgan.output
            else:
                return '<p class="text-muted">No hi ha membres definits.</p>'

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
        for item in acords:
            acords.append(dict(
                organType=item.organType,
                path=item.getPath(),
                id=item.id))
        for item in punts:
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


def getAllOrgans():
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
                    secretaris += username + ", "
                if 'OG2-Editor' in role:
                    editors += username + ", "
                if 'OG3-Membre' in role:
                    membres += username + ", "
                if 'OG4-Afectat' in role:
                    afectats += username + ", "

        if parent_roles:
            for (username, role) in parent_roles:
                if 'OG1-Secretari' in role and username not in secretaris:
                    secretaris += username + ", "
                if 'OG2-Editor' in role and username not in editors:
                    editors += username + ", "
                if 'OG3-Membre' in role and username not in secretaris:
                    membres += username + ", "
                if 'OG4-Afectat' in role and username not in afectats:
                    afectats += username + ", "

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

        sessions_open_last_year = api.content.find(
            portal_type='genweb.organs.sessio',
            path='/'.join(obj.getPhysicalPath()),
            start={'query': datetime.datetime.now() - datetime.timedelta(days=365), 'range': 'min'})

        elements = dict(
            title=obj.Title(),
            path=obj.absolute_url(),
            organType=obj.organType,
            acronim=obj.acronim,
            secretaris=secretaris,
            editors=editors,
            membres=membres,
            afectats=afectats,
            sessions_open_last_year=len(sessions_open_last_year),
            parent=pa.Title())

        if pa.getParentNode().id != "ca":
            elements['grandparent'] = pa.getParentNode().Title()
            elements['to_sort'] = elements['grandparent']
        else:
            elements['to_sort'] = elements['parent']

        results.append(elements)

        results = sorted(results, key=itemgetter('parent'))

    return sorted(results, key=itemgetter('to_sort'))


class allOrgans(BrowserView):
    __call__ = ViewPageTemplateFile('views/allorgans.pt')

    def organsTable(self):
        return getAllOrgans()


class exportAllOrgans(BrowserView):

    data_header_columns = [
        "Tipus d'unitat",
        "Unitat",
        "Nom de l'òrgan",
        "Tipus d'òrgan de govern",
        "Secretaris",
        "Editors",
        "Membres",
        "Afectats",
        "Sessions obertes l'últim any"]

    def __call__(self):
        output_file = StringIO()
        # Write the BOM of the text stream to make its charset explicit
        output_file.write(u'\ufeff')
        self.write_data(output_file)

        header_content_type = 'text/csv'
        header_filename = 'llista_organs' + '.csv'
        self.request.response.setHeader('Content-Type', header_content_type)
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="{0}"'.format(header_filename))
        return output_file.getvalue().encode('utf-8')

    def write_data(self, output_file):
        writer = csv.writer(output_file, dialect='excel', delimiter=',')
        writer.writerow(self.data_header_columns)

        for organ in getAllOrgans():
            title = organ['title']
            if organ['acronim']:
                title += ' [' + organ['acronim'] + ']'

            writer.writerow([organ['grandparent'] if 'grandparent' in organ else '',
                             organ['parent'],
                             title,
                             translate(msgid=organ['organType'], domain='genweb.organs', target_language='ca'),
                             organ['secretaris'],
                             organ['editors'],
                             organ['membres'],
                             organ['afectats'],
                             organ['sessions_open_last_year'],
            ])


class ReorderSessions(BrowserView):
    """ Reordena sessions de la vista d'organ"""
    def __call__(self):
        """ This call reassign the correct sessions for an organ
        """
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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


class ReloadVoteStats(BrowserView):
    """ Retorna el valor necessaris per refrescar les dades d'una votació"""

    @json_response
    def __call__(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        results = portal_catalog.unrestrictedSearchResults(
            UID=self.request.UID,
            portal_type=['genweb.organs.votacioacord', 'genweb.organs.acord', 'genweb.organs.punt'])

        if results:
            votacio = results[0].getObject()
            roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
            viewList = utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)
            lang = self.context.language

            infoVotacio = votacio.infoVotacio
            if isinstance(infoVotacio, str):
                infoVotacio = ast.literal_eval(infoVotacio)

            if votacio.estatVotacio == 'open':
                data = {'open': True,
                        'state': translate(msgid='open', domain='genweb.organs', target_language=lang),
                        'hourOpen': votacio.horaIniciVotacio,
                        'totalVote': 0,
                        'totalVoteListHTML': ''}

                for key, value in infoVotacio.items():
                    data['totalVote'] += 1
                    if viewList:
                        data['totalVoteListHTML'] += '<p>' + key + '</p>'
            else:
                data = {'open': False,
                        'state': translate(msgid='close', domain='genweb.organs', target_language=lang),
                        'hourOpen': votacio.horaIniciVotacio,
                        'hourClose': votacio.horaFiVotacio,
                        'favorVote': 0,
                        'favorVoteListHTML': '',
                        'againstVote': 0,
                        'againstVoteListHTML': '',
                        'whiteVote': 0,
                        'whiteVoteListHTML': '',
                        'totalVote': 0,
                        'totalVoteListHTML': ''}

                for key, value in infoVotacio.items():
                    data['totalVote'] += 1
                    if value == 'favor':
                        data['favorVote'] += 1
                        if viewList:
                            data['favorVoteListHTML'] += '<p>' + key + '</p>'
                    elif value == 'against':
                        data['againstVote'] += 1
                        if viewList:
                            data['againstVoteListHTML'] += '<p>' + key + '</p>'
                    elif value == 'white':
                        data['whiteVote'] += 1
                        if viewList:
                            data['whiteVoteListHTML'] += '<p>' + key + '</p>'

            return data

        return False


class migracioAnnexosActes(BrowserView):

    def __call__(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        values = portal_catalog.searchResults(portal_type='genweb.organs.acta')
        for value in values:
            try:
                acta = value.getObject()
                if acta.file:
                    api.content.create(
                        title=acta.file.filename,
                        file=acta.file,
                        type='genweb.organs.annex',
                        container=acta)

                    acta.file = None
            except:
                pass

        transaction.commit()
        return 'OK'


class getAcordsOrgangovern(BrowserView):

    def __call__(self):
        """ La llista d'acords i el tab el veu tothom.
            Després s'aplica el permís per cada rol a la vista de l'acord """
        results = []

        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())

        # Només veu els acords de les sessions que pot veure
        sessions = portal_catalog.unrestrictedSearchResults(
            portal_type='genweb.organs.sessio',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        paths = []
        if api.user.is_anonymous():
            username = None
        else:
            username = api.user.get_current().id

        organ_type = self.context.organType
        for session in sessions:
            paths.append(session.getPath())

        for path in paths:
            values = portal_catalog.unrestrictedSearchResults(
                portal_type=['genweb.organs.acord'],
                sort_on='modified',
                path={'query': path,
                      'depth': 3})

            for obj in values:
                value = obj.getObject()
                if value.agreement:
                    if len(value.agreement.split('/')) > 2:
                        try:
                            num = value.agreement.split('/')[1].zfill(3) + value.agreement.split('/')[2].zfill(3) + value.agreement.split('/')[3].zfill(3)
                        except:
                            num = value.agreement.split('/')[1].zfill(3) + value.agreement.split('/')[2].zfill(3)
                        any = value.agreement.split('/')[0]
                    else:
                        num = value.agreement.split('/')[0].zfill(3)
                        any = value.agreement.split('/')[1]
                else:
                    num = ''
                    any = ''
                if value.aq_parent.aq_parent.portal_type == 'genweb.organs.sessio':
                    wf_state = api.content.get_state(obj=value.aq_parent.aq_parent)
                    if username:
                        roles = api.user.get_roles(username=username, obj=value.aq_parent.aq_parent)
                    else:
                        roles = []
                else:
                    wf_state = api.content.get_state(obj=value.aq_parent)
                    if username:
                        roles = api.user.get_roles(username=username, obj=value.aq_parent)
                    else:
                        roles = []
                # Oculta acords from table depending on role and state
                add_acord = False
                if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles:
                    add_acord = True
                elif 'OG3-Membre' in roles:
                    if 'planificada' not in wf_state:
                        add_acord = True
                elif 'OG4-Afectat' in roles:
                    if organ_type == 'open_organ' or organ_type == 'restricted_to_affected_organ':
                        if 'realitzada' in wf_state or 'tancada' in wf_state or 'en_correccio' in wf_state:
                            add_acord = True
                else:
                    if 'tancada' in wf_state or 'en_correccio' in wf_state:
                        add_acord = True

                if add_acord:
                    results.append(dict(title=value.title,
                                        absolute_url=value.absolute_url(),
                                        agreement=value.agreement,
                                        hiddenOrder=any + num,
                                        estatsLlista=value.estatsLlista,
                                        color=utils.getColor(obj)))

        return json.dumps(sorted(results, key=itemgetter('hiddenOrder'), reverse=True))


class getActesOrgangovern(BrowserView):

    def __call__(self):
        """ Si es Manager/Secretari/Editor/Membre show actas
            Affectat i altres NO veuen MAI les ACTES """
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            results = []
            portal_catalog = api.portal.get_tool(name='portal_catalog')
            folder_path = '/'.join(self.context.getPhysicalPath())

            sessions = portal_catalog.searchResults(
                portal_type='genweb.organs.sessio',
                sort_on='getObjPositionInParent',
                path={'query': folder_path,
                      'depth': 1})

            paths = []
            for session in sessions:
                paths.append(session.getPath())

            for path in paths:
                values = portal_catalog.searchResults(
                    portal_type=['genweb.organs.acta'],
                    sort_on='modified',
                    path={'query': path,
                          'depth': 3})

                for obj in values:
                    value = obj.getObject()
                    results.append(dict(title=value.title,
                                        absolute_url=value.absolute_url(),
                                        data=value.horaInici.strftime('%d/%m/%Y'),
                                        hiddenOrder=value.horaInici.strftime('%Y%m%d')))
            return json.dumps(sorted(results, key=itemgetter('hiddenOrder'), reverse=True))
        else:
            return json.dumps([])


class updateIndicadors(BrowserView):

    def __call__(self):
        update_indicators(
            self, service=get_settings_property('service_id'), indicator='organ-n')

        update_indicators(
            self, service=get_settings_property('service_id'), indicator='sessio-n')

        update_indicators(
            self, service=get_settings_property('service_id'), indicator='acord-n')


class allOrgansEstatsLlista(BrowserView):

    @json_response
    def __call__(self):
        all_brains = api.content.find(portal_type='genweb.organs.organgovern')

        results = []
        for brain in all_brains:
            results.append({
                'id': brain.id,
                'title': brain.Title,
                'url': brain.getURL(),
                'estats': getattr(brain.getObject().estatsLlista, 'raw', '').replace('<p>', '').replace('</p>', '').split('\r\n') if brain.getObject().estatsLlista else []
            })

        return results


class getUsers(BrowserView):

    def __call__(self):
        users = getLdapUserData(self.request.form['user'])
        if users and len(users) > 0:
            listUsers = []
            for user in users:
                try:
                    listUsers.append({
                        'user': user['id'],
                        'email': user['mail'],
                        'fullname': user['sn'],
                    })
                except:
                    pass
            return json.dumps(listUsers)
        else:
            return None