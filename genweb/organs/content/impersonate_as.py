# -*- coding: utf-8 -*-
from plone import api
from five import grok
from zope.schema import TextLine
from z3c.form import button
from plone.directives import form
from Products.statusmessages.interfaces import IStatusMessage
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from AccessControl import Unauthorized
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from zope import schema
from time import strftime
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from genweb.organs.utils import addEntryLog
from Products.CMFCore.utils import getToolByName
from genweb.organs import utils

grok.templatedir("templates")


class IImpersonate(form.Schema):
    """ Define the fields of this form
    """


class ShowSessionAs(form.SchemaForm):
    grok.name('view_as_role')
    grok.context(ISessio)
    grok.template("impersonate_as")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    def getUserRole(self):
        # Només els rols Reponsable, Editor i Manager poden veure aquesta vista
        role = self.request.form.get('id', '')
        username = api.user.get_current().getProperty('id')
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'Manager' in roles or 'OG1-Responsable' in roles or 'OG2-Editor' in roles:
            return role
        else:
            return False

    def simulation(self):
        # Obtenim rol usuari que cal veure i fer la simulació
        role = str(self.getUserRole())
        if role is 'False':
            return self.request.response.redirect(self.context.absolute_url())
        elif role == 'OG1-Responsable':
            return 'Responsable'
        elif role == 'OG2-Editor':
            return 'Editor'
        elif role == 'OG3-Membre':
            return 'Membre'
        elif role == 'OG4-Afectat':
            return 'Afectat'
        elif role == 'OG5-Anonim':
            return 'Anonim'
        else:
            return self.request.response.redirect(self.context.absolute_url())

    def isAfectat(self):
        if self.simulation() is 'Afectat':
            review_state = api.content.get_state(self.context)
            if review_state in ['planificada', 'convocada']:
                return False
            if review_state in ['realitzada', 'tancada', 'en_correccio']:
                return True
        else:
            return False

    def isMembre(self):
        if self.simulation() is 'Membre':
            review_state = api.content.get_state(self.context)
            if review_state in ['planificada']:
                return False
            if review_state in ['convocada', 'realitzada', 'tancada', 'en_correccio']:
                return True
        else:
            return False

    def isAnonim(self):
        # if user is anonim and
        if self.simulation() is 'Anonim':
            review_state = api.content.get_state(self.context)
            if review_state in ['planificada', 'convocada', 'realitzada']:
                return False
            if review_state in ['tancada', 'en_correccio']:
                return True
        else:
            return False

    def isManager(self):
        return utils.isManager(self)

    def canModify(self):
        review_state = api.content.get_state(self.context)
        value = False
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and utils.isResponsable(self):
            value = True
        if review_state in ['planificada', 'convocada', 'realitzada'] and utils.isEditor(self):
            value = True
        return value or self.isManager()

    def getColor(self, data):
        # assign custom colors on organ states
        return utils.getColor(data)

    def estatsCanvi(self, data):
        return utils.estatsCanvi(data)

    def hihaPunts(self):
        values = api.content.find(context=self.context, depth=1, portal_type='genweb.organs.punt')
        if values:
            return True
        else:
            return False

    def PuntsInside(self):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            if obj.portal_type == 'genweb.organs.acta' or obj.portal_type == 'genweb.organs.audio':
                # add actas to template for oredering but dont show
                item = obj.getObject()
                results.append(dict(id=obj.id,
                                    classe='hidden',
                                    show=False,
                                    agreement=None))
            else:
                item = obj.getObject()
                if len(item.objectIds()) > 0:
                    inside = True
                else:
                    inside = False
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=item.absolute_url(),
                                    item_path=obj.getPath(),
                                    proposalPoint=item.proposalPoint,
                                    agreement=item.agreement,
                                    state=item.estatsLlista,
                                    css=self.getColor(obj),
                                    estats=self.estatsCanvi(obj),
                                    id=obj.id,
                                    show=True,
                                    classe="ui-state-grey-impersonate",
                                    items_inside=inside))
        return results

    def SubpuntsInside(self, data):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + data['id']
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.subpunt',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        if values:
            for obj in values:
                item = obj.getObject()
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=item.absolute_url(),
                                    proposalPoint=item.proposalPoint,
                                    item_path=obj.getPath(),
                                    state=item.estatsLlista,
                                    agreement=item.agreement,
                                    estats=self.estatsCanvi(obj),
                                    css=self.getColor(obj),
                                    id='/'.join(item.absolute_url_path().split('/')[-2:])))
            return results
        else:
            return False

    def AudioInside(self):
        """ Retorna els fitxers d'audio creats aquí dintre (sense tenir compte estat)
        """
        folder_path = '/'.join(self.context.getPhysicalPath())
        portal_catalog = getToolByName(self, 'portal_catalog')
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.audio',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        if values:
            results = []
            for obj in values:
                results.append(dict(title=obj.Title,
                                    absolute_url=obj.getURL()))
            return results
        else:
            return False

    def ActesInside(self):
        """ Retorna les actes creades aquí dintre (sense tenir compte estat)
        """
        folder_path = '/'.join(self.context.getPhysicalPath())
        portal_catalog = getToolByName(self, 'portal_catalog')
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.acta',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            results.append(dict(title=obj.Title,
                                absolute_url=obj.getURL(),
                                date=obj.getObject().dataSessio.strftime('%d/%m/%Y')))
        return results

    def valuesTable(self):
        values = dict(dataSessio=self.context.dataSessio.strftime('%d/%m/%Y'),
                      horaInici=self.context.horaInici.strftime('%H:%M'),
                      horaFi=self.context.horaFi.strftime('%H:%M'),
                      llocConvocatoria=self.context.llocConvocatoria,
                      organTitle=self.OrganTitle(),
                      )
        return values

    def OrganTitle(self):
        """ Retorna el títol de l'òrgan """
        title = self.context.aq_parent.Title()
        return title

    def hihaMultimedia(self):
        if self.context.enllacVideo or self.context.enllacAudio:
            return True
        else:
            return False

    def hihaPersones(self):
        if self.context.membresConvocats or self.context.membresConvidats or self.context.llistaExcusats:
            return True
        else:
            return False

    def showActaTab(self):
        if self.hihaMultimedia() or self.ActesInside():
            return True
        else:
            return False

    def filesinsidePunt(self, item):
        session_path = '/'.join(self.context.getPhysicalPath()) + '/' + item['id']
        portal_catalog = getToolByName(self, 'portal_catalog')

        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file', 'genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': session_path,
                  'depth': 1})
        results = []
        for obj in values:
            if obj.portal_type == 'genweb.organs.file':
                if obj.hiddenfile is True:
                    if self.isAnonim() or self.isAfectat():
                        continue
                    else:
                        tipus = 'fa fa-file-pdf-o'
                        document = _(u'Fitxer públic')
                        labelClass = 'label label-default'
                else:
                    tipus = 'fa fa-file-pdf-o'
                    document = _(u'Fitxer públic')
                    labelClass = 'label label-default'
            else:
                tipus = 'fa fa-file-text-o'
                document = _(u'Document')
                labelClass = 'label label-default'
            results.append(dict(title=obj.Title,
                                portal_type=obj.portal_type,
                                absolute_url=obj.getURL(),
                                classCSS=tipus,
                                hidden=obj.hiddenfile,
                                labelClass=labelClass,
                                content=document,
                                id=str(item['id']) + '/' + obj.id))
        return results
