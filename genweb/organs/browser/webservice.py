# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
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
        #if len(request.path) == 4:
        self.acord = '/'.join(path_ordered)

    def __call__(self):
        # And we have the full path in self.acord
        if not self.acord:
            # Empty query returns default template
            return self.index()
        else:
            # results = []
            # [organ, year, month, acord] = self.acord.split('/')
            # Example : /acord/CG/2017/05/01
            items = api.content.find(portal_type='genweb.organs.acord',
                                     index_agreement=self.acord)

            # for value in items:
            #     item = value.getObject()

            #     results.append(dict(title=item.Title(),
            #                         path=value.getPath(),
            #                         agreement=item.agreement,
            #                         url=item.absolute_url(),
            #                         proposalPoint=item.proposalPoint))
            # return json.dumps(results)
            if items:
                return self.request.response.redirect(items[0].getObject().absolute_url())
            else:
                return self.request.response.redirect(api.portal.get().absolute_url())

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
            if element.aq_parent.portal_type == 'genweb.organs.organgovern':
                if username:
                    roles = api.user.get_roles(obj=element.aq_parent, username=username)
                else:
                    roles = []
                organType = element.aq_parent.organType
                if 'Manager' in roles or (organType == 'open_organ'):
                    print "1"
                    results2.append(value)
                elif organType == 'restricted_to_members_organ':
                    if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles:
                        print "2"
                        results2.append(value)
                elif organType == 'restricted_to_affected_organ':
                    if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles:
                        print "3"
                        results2.append(value)
                else:
                    # remove element
                    continue
            elif element.aq_parent.aq_parent.portal_type == 'genweb.organs.organgovern':
                if username:
                    roles = api.user.get_roles(obj=element.aq_parent.aq_parent, username=username)
                else:
                    roles = []
                organType = element.aq_parent.aq_parent.organType
                if 'Manager' in roles or (organType == 'open_organ'):
                    print "4"
                    results2.append(value)
                elif organType == 'restricted_to_members_organ':
                    if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles:
                        print "5"
                        results2.append(value)
                elif organType == 'restricted_to_affected_organ':
                    if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles:
                        print "6"
                        results2.append(value)
                else:
                    # remove element
                    continue
            else:
                continue
        for value in results2:
            item = value.getObject()
            results3.append(dict(id=item.agreement,
                                 path=item.absolute_url(),
                                 state=item.estatsLlista,
                                 title=item.Title(),
                                 proposal=item.proposalPoint))
        return results3
