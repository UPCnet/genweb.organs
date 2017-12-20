# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class webservice(BrowserView):
    # TODO: Enable it and make fully functional...
    def __call__(self):
        # Execute on -- Organsfolder (genweb.organs.organsfolder) --
        # http://localhost:8080/organs/ca/eetac/consell-de-govern/ws?id=CDG/2017/01/01
        # CG/2017/01/01
        # http://localhost:8080/organs/ca/eetac/consell-de-govern/session1/informe-del-rector
        # Maybe better... http://localhost:8080/organs/api/CDG/2017/01/01

        return None

        itemid = self.request.form.get('id')
        if itemid == '':
            pass
        else:
            item = itemid.split('/')
            acronim = item[0]
            # year = item[1]
            num_session = item[2]
            # acord = item[3]

            portal_catalog = getToolByName(self, 'portal_catalog')
            organs = portal_catalog.searchResults(
                portal_type=['genweb.organs.organgovern'])

            for org in organs:
                if org.getObject().acronim == acronim:
                    organPath = org.getPath()

            sessions = portal_catalog.searchResults(
                portal_type=['genweb.organs.sessio'],
                path={'query': organPath,
                      'depth': 1})
            for sess in sessions:
                if sess.getObject().numSession == num_session:
                    sessionPath = sess.getPath()

            punt = portal_catalog.searchResults(
                portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
                path={'query': sessionPath,
                      'depth': 1})[0]

            self.request.response.redirect(punt.getURL())
