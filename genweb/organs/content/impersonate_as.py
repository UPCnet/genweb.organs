# -*- coding: utf-8 -*-
from plone import api
from z3c.form import form
from plone.event.interfaces import IEventAccessor
from zope.i18n import translate

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.content.sessio import ISessio
from genweb.organs.interfaces import IGenwebOrgansLayer


class IImpersonate(form.Schema):
    """ Mode veure com: /view_as_role?id=OG2-Editor
    """


class ShowSessionAs(form.SchemaForm):
    def getUserRole(self):
        # Només els rols Reponsable, Editor i Manager poden veure aquesta vista
        role = self.request.form.get('id', '')
        username = api.user.get_current().id
        if username:
            roles = api.user.get_roles(username=username, obj=self.context)
            if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles):
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
        elif role == 'Other':
            return _(u'Altres')
        elif role == 'Member':
            return _(u'Membre')
        elif role == 'Affected':
            return _(u'Afectat')
        else:
            return self.request.response.redirect(self.context.absolute_url())

    def isAfectat(self):
        role = _(u'Afectat')
        if self.simulation() == role:
            review_state = api.content.get_state(self.context)
            if review_state in ['planificada', 'convocada']:
                return False
            if review_state in ['realitzada', 'tancada', 'en_correccio']:
                return True
        else:
            return False

    def isMembre(self):
        role = _(u'Membre')
        if self.simulation() == role:
            review_state = api.content.get_state(self.context)
            if review_state in ['planificada']:
                return False
            if review_state in ['convocada', 'realitzada', 'tancada', 'en_correccio']:
                return True
        else:
            return False

    def isPublic(self):
        role = _(u'Altres')
        if self.simulation() == role:
            review_state = api.content.get_state(self.context)
            if review_state in ['planificada', 'convocada', 'realitzada']:
                return False
            if review_state in ['tancada', 'en_correccio']:
                return True
        else:
            return False

    def canModify(self):
        review_state = api.content.get_state(self.context)
        value = False
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and 'OG1-Secretari' in roles:
            value = True
        if review_state in ['planificada', 'convocada', 'realitzada'] and 'OG2-Editor' in roles:
            value = True
        return value or 'Manager' in roles

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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
                        agreement = _(u"sense numeracio") if not getattr(item, 'omitAgreement', False) else ''
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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
                        agreement = _(u"sense numeracio") if not getattr(item, 'omitAgreement', False) else ''
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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.acta',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        acc = IEventAccessor(self.context)
        for obj in values:
            if acc. start:
                dataSessio = acc.start.strftime('%d/%m/%Y')
            else:
                dataSessio = ''
            results.append(dict(title=obj.Title,
                                absolute_url=obj.getURL(),
                                date=dataSessio))
        return results

    def valuesTable(self):
        acc = IEventAccessor(self.context)
        if acc.start:
            horaInici = acc.start.strftime('%d/%m/%Y %H:%M')
            year = acc.start.strftime('%Y') + '/'
        else:
            horaInici = ''
            year = ''
        if acc.end:
            horaFi = acc.end.strftime('%d/%m/%Y %H:%M')
        else:
            horaFi = ''
        if self.context.llocConvocatoria is None:
            llocConvocatoria = ''
        else:
            llocConvocatoria = self.context.llocConvocatoria

        session = self.context.numSessio
        organ = self.context.aq_parent.acronim
        sessionNumber = str(organ) + '/' + str(year) + str(session)

        value = api.content.get_state(obj=self.context)
        lang = self.context.language
        status = translate(msgid=value, domain='genweb', target_language=lang)

        values = dict(horaInici=horaInici,
                      horaFi=horaFi,
                      llocConvocatoria=llocConvocatoria,
                      organTitle=self.OrganTitle(),
                      sessionNumber=sessionNumber,
                      status=status,
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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        role = self.request.form.get('id', '')

        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file', 'genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': session_path,
                  'depth': 1})
        results = []
        for obj in values:
            if obj.portal_type == 'genweb.organs.file':
                tipus = 'fa fa-file-pdf-o'
            else:
                tipus = 'fa fa-file-text-o'
            if role == 'Other' or role == 'Affected':
                if obj.portal_type == 'genweb.organs.document':
                    # Es un document, mostrem part publica si la té
                    if obj.getObject().defaultContent:
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL(),
                                            classCSS=tipus,
                                            id=str(item['id']) + '/' + obj.id))
                if obj.portal_type == 'genweb.organs.file':
                    # Es un file, mostrem part publica si la té
                    if obj.getObject().visiblefile:
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL(),
                                            classCSS=tipus,
                                            id=str(item['id']) + '/' + obj.id))

            if role == 'Member':
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=obj.getURL(),
                                    classCSS=tipus,
                                    id=str(item['id']) + '/' + obj.id))
        return results
