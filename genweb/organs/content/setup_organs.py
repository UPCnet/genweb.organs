# -*- coding: utf-8 -*-
from plone import api
from five import grok
from plone.directives import form
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from Products.CMFCore.utils import getToolByName
from genweb.organs import utils
from Products.CMFPlone.interfaces import IPloneSiteRoot
from five import grok
from plone import api
from cgi import parse_qs
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.dexterity.utils import createContentInContainer
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.app.controlpanel.mail import IMailSchema
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import ITranslationManager

from plone.namedfile.file import NamedBlobImage

from genweb.core.interfaces import IHomePage
from genweb.core.interfaces import INewsFolder
from genweb.core.interfaces import IEventFolder
from genweb.core.interfaces import IProtectedContent
from genweb.core.browser.plantilles import get_plantilles
from genweb.core import utils

from plone.app.event.base import localized_now
from datetime import timedelta
import pkg_resources
import logging
from plone import api

grok.templatedir("templates")


class setup(grok.View):
    grok.name('setup_organs')
    grok.template('setup_organs')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    def update(self):
            base_url = "%s/@@setup_organs" % str(self.context.absolute_url_path())
            qs = self.request.get('QUERY_STRING', None)

            if qs is not None:
                query = parse_qs(qs)
                gwtype = ''
                if 'create' in query:
                    self.createContent(gwtype)
                    self.request.response.redirect(base_url)

    def contentStatus(self):
        objects = [(u'ORGANS', [('organs', 'ca'), ('organos', 'es'), ('government', 'en')]),
                   ]

        result = []
        portal = api.portal.get()

        for o in objects:
            tr = [o[0]]
            for td, lang in o[1]:
                if lang == 'root':
                    tr.append(getattr(portal, td, False) and 'Creat' or 'No existeix')
                else:
                    if getattr(portal, lang, False):
                        tr.append(getattr(portal[lang], td, False) and 'Creat' or 'No existeix')
                    else:
                        tr.append('No existeix')
            result.append(tr)
        return result

    def createContent(self, gwtype):
        """ Method that creates all the default content """
        portal = api.portal.get()
        portal_ca = portal['ca']
        portal_en = portal['en']
        portal_es = portal['es']
