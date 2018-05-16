# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class searchHome(BrowserView):
    """ Busca elements """
    __call__ = ViewPageTemplateFile('views/search_home.pt')

    def getPage(self):
        """ Retorna la pagina benvingut """
        portal_catalog = getToolByName(self, 'portal_catalog')
        item = portal_catalog.searchResults(
            portal_type=['Document'], id='benvingut')
        if item:
            return item[0].getObject().text.output
        else:
            return None

    def getLatest(self):
        """ Retorna la pagina benvingut """
        portal_catalog = getToolByName(self, 'portal_catalog')
        item = portal_catalog.searchResults(
            portal_type=['genweb.organs.sessio'])
        if item:
            return item[0].getObject().title
        else:
            return None
