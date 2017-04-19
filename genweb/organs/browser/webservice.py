# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class webservice(BrowserView):

    def __call__(self):
        # http://localhost:8080/organs/ca/eetac/consell-de-govern/ws?id=CDG/2017/01/01
        # CDG/2017/01/01
        # http://localhost:8080/organs/ca/eetac/consell-de-govern/session1/informe-del-rector
        itemid = self.request.form.get('id')
        if itemid == '':
            pass
        else:
            item = itemid.split('/')
            organ = item[0]
            year = item[1]
            session = item[2]
            acord = item[3]

            portal_catalog = getToolByName(self, 'portal_catalog')
            organPath = portal_catalog.searchResults(
                portal_type=['genweb.organs.organgovern'],
                acronim=organ)[0].getPath()

            sessionPath = portal_catalog.searchResults(
                portal_type=['genweb.organs.sessio'],
                path={'query': organPath,
                      'depth': 1})[0].getPath()

            punt = portal_catalog.searchResults(
                portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
                path={'query': sessionPath,
                      'depth': 1})[0]
                    #   .getPath()
            self.request.response.redirect(punt.getURL())
