# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from plone import api
import json


@implementer(IPublishTraverse)
class Webservice(BrowserView):
    """ Default Site webservice style """

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
        if len(request.path) == 4:
            self.acord = '/'.join(path_ordered)

    def __call__(self):
        # And we have the full path in self.acord
        if not self.acord:
            return 'THIS IS THE API TO GET DIRECTLY THE ACORDS FROM ORGANS DE GOVERN'
        else:
            # results = []
            # [organ, year, month, acord] = self.acord.split('/')
            # Example : CG/2017/05/01
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
