# -*- coding: utf-8 -*-
from plone import api
from five import grok
from plone.directives import form
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import _
from genweb.organs.content.sessio import ISessio
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
        username = api.user.get_current().id
        if username:
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles:
                return role
            else:
                return False
        else:
            return False

    def simulation(self):
        # Obtenim rol usuari que cal veure i fer la simulació
        role = str(self.getUserRole())
        if role is 'False':
            return self.request.response.redirect(self.context.absolute_url())
        elif role == 'Public':
            return 'Public'
        elif role == 'OG3-Membre':
            return 'Membre'
        elif role == 'OG4-Afectat':
            return 'Afectat'
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

    def isPublic(self):
        if self.simulation() is 'Public':
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
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and utils.isSecretari(self):
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
        values = api.content.find(
            context=self.context,
            depth=1,
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'])
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
                if item.portal_type == 'genweb.organs.acord':
                    if item.agreement:
                        agreement = item.agreement
                    else:
                        agreement = _(u"ACORD")
                else:
                    agreement = ''
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=item.absolute_url(),
                                    item_path=item.absolute_url_path(),
                                    proposalPoint=item.proposalPoint,
                                    agreement=agreement,
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
            portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        if values:
            for obj in values:
                item = obj.getObject()
                if item.portal_type == 'genweb.organs.acord':
                    if item.agreement:
                        agreement = item.agreement
                    else:
                        agreement = _(u"ACORD")
                else:
                    agreement = ''
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=item.absolute_url(),
                                    proposalPoint=item.proposalPoint,
                                    item_path=item.absolute_url_path(),
                                    state=item.estatsLlista,
                                    agreement=agreement,
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
                                date=obj.start))
        return results

    def valuesTable(self):
        start = getattr(self.context, 'start', None)
        end = getattr(self.context, 'end', None)
        if start:
            dataSessio = self.context.start.strftime('%d/%m/%Y')
            horaInici = self.context.start.strftime('%H:%M')
        else:
            dataSessio = ''
            horaInici = ''
        if end:
            horaFi = self.context.end.strftime('%H:%M')
        else:
            horaFi = ''

        values = dict(dataSessio=dataSessio,
                      horaInici=horaInici,
                      horaFi=horaFi,
                      llocConvocatoria=self.context.llocConvocatoria,
                      organTitle=self.OrganTitle(),
                      )
        return values

    def OrganTitle(self):
        """ Retorna el títol de l'òrgan """
        return self.context.aq_parent.Title()

    def hihaPersones(self):
        if self.context.membresConvocats or self.context.membresConvidats or self.context.llistaExcusats:
            return True
        else:
            return False

    def showActaTab(self):
        if self.ActesInside() and self.isMembre():
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
                if obj.getObject().hiddenfile:
                    if self.isAfectat():
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
                                labelClass=labelClass,
                                content=document,
                                id=str(item['id']) + '/' + obj.id))
        return results
