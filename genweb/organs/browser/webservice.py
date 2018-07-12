# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import unicodedata
from operator import itemgetter
import json


@implementer(IPublishTraverse)
class Webservice(BrowserView):
    """ Default Site webservice style """

    index = ViewPageTemplateFile("views/webservice.pt")

    def publishTraverse(self, request, name):
        # Stop traversing, we have arrived
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self

    def __init__(self, context, request):
        """Once we get to __call__, the path is lost so we
           capture it here on initialization
        """
        super(Webservice, self).__init__(context, request)
        self.acord = None
        path_ordered = request.path[::-1]
        self.acord = '/'.join(path_ordered)

    def __call__(self):
        # And we have the full path in self.acord
        if not self.acord:
            # Empty query returns default template
            return self.index()
        else:
            results = []
            # [organ, year, month, acord] = self.acord.split('/')
            # Example : /acord/CG/2017/05/01
            results = api.content.find(portal_type='genweb.organs.acord',
                                       index_agreement=self.acord)

            # Uncomment this to show item properties in json format
            # items = []
            # for value in results:
            #     item = value.getObject()
            #     items.append(dict(title=item.Title(),
            #                       path=value.getPath(),
            #                       agreement=item.agreement,
            #                       url=item.absolute_url(),
            #                       proposalPoint=item.proposalPoint))
            # return json.dumps(items)

            if results:
                return self.request.response.redirect(results[0].getObject().absolute_url())
            else:
                return self.request.response.redirect(api.portal.get().absolute_url())

    def getColor(self, value):
        # Get custom colors on passed organ states
        estat = value.estatsLlista
        values = value.aq_parent.aq_parent.estatsLlista
        color = '#777777'
        for value in values.split('</p>'):
            if value != '':
                item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
                if estat.decode('utf-8') == ' '.join(item_net.split()[:-1]).lstrip():
                    return item_net.split(' ')[-1:][0].rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' ')
        return color

    def allAcords(self):
        results = api.content.find(portal_type='genweb.organs.acord')
        results2 = []
        results3 = []

        if api.user.is_anonymous():
            username = None
        else:
            username = api.user.get_current().id
        for value in results:
            element = value.getObject()
            if element.aq_parent.aq_parent.portal_type == 'genweb.organs.organgovern':
                if username:
                    roles = api.user.get_roles(obj=element.aq_parent.aq_parent, username=username)
                else:
                    roles = []
                organ_tipus = element.aq_parent.aq_parent.organType
                estatSessio = api.content.get_state(obj=element.aq_parent)
                if organ_tipus == 'open_organ':
                    if estatSessio == 'planificada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles):
                        results2.append(value)
                    elif estatSessio == 'convocada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    elif estatSessio == 'realitzada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles):
                        results2.append(value)
                    elif estatSessio == 'tancada':
                        results2.append(value)
                    elif estatSessio == 'en_correccio':
                        results2.append(value)
                    else:
                        continue
                if organ_tipus == 'restricted_to_members_organ':
                    if estatSessio == 'planificada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles):
                        results2.append(value)
                    elif estatSessio == 'convocada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    elif estatSessio == 'realitzada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    elif estatSessio == 'tancada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    elif estatSessio == 'en_correccio' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    else:
                        continue
                if organ_tipus == 'restricted_to_affected_organ':
                    if estatSessio == 'planificada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles):
                        results2.append(value)
                    elif estatSessio == 'convocada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    elif estatSessio == 'realitzada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles):
                        results2.append(value)
                    elif estatSessio == 'tancada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles):
                        results2.append(value)
                    elif estatSessio == 'en_correccio' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles):
                        results2.append(value)
                    else:
                        continue
                else:
                    # remove element
                    continue
            elif element.aq_parent.aq_parent.aq_parent.portal_type == 'genweb.organs.organgovern':
                if username:
                    roles = api.user.get_roles(obj=element.aq_parent.aq_parent.aq_parent, username=username)
                else:
                    roles = []
                organ_tipus = element.aq_parent.aq_parent.aq_parent.organType
                estatSessio = api.content.get_state(obj=element.aq_parent.aq_parent)
                if organ_tipus == 'open_organ':
                    if estatSessio == 'planificada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles):
                        results2.append(value)
                    elif estatSessio == 'convocada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    elif estatSessio == 'realitzada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles):
                        results2.append(value)
                    elif estatSessio == 'tancada':
                        results2.append(value)
                    elif estatSessio == 'en_correccio':
                        results2.append(value)
                    else:
                        continue
                if organ_tipus == 'restricted_to_members_organ':
                    if estatSessio == 'planificada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles):
                        results2.append(value)
                    elif estatSessio == 'convocada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    elif estatSessio == 'realitzada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    elif estatSessio == 'tancada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    elif estatSessio == 'en_correccio' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    else:
                        continue
                if organ_tipus == 'restricted_to_affected_organ':
                    if estatSessio == 'planificada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles):
                        results2.append(value)
                    elif estatSessio == 'convocada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles):
                        results2.append(value)
                    elif estatSessio == 'realitzada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles):
                        results2.append(value)
                    elif estatSessio == 'tancada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles):
                        results2.append(value)
                    elif estatSessio == 'en_correccio' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles):
                        results2.append(value)
                    else:
                        continue
                else:
                    # remove element
                    continue
            else:
                continue
        for value in results2:
            item = value.getObject()

            results3.append(dict(id=item.agreement,
                                 path=item.absolute_url(),
                                 estatsLlista=item.estatsLlista,
                                 color=self.getColor(item),
                                 title=item.Title(),
                                 ))
        return sorted(results3, key=itemgetter('id'), reverse=True)
