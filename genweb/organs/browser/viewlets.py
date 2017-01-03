# -*- coding: utf-8 -*-
import requests
import socket
from five import grok
from plone import api
from time import time
from Acquisition import aq_inner
from AccessControl import getSecurityManager
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.security import checkPermission

from plone.memoize import ram
from plone.memoize.view import memoize_contextless

# from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile as ZopeViewPageTemplateFile
from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.layout.viewlets.common import PersonalBarViewlet, GlobalSectionsViewlet, PathBarViewlet
from plone.app.layout.viewlets.common import SearchBoxViewlet, ManagePortletsFallbackViewlet
from plone.app.layout.viewlets.interfaces import IPortalTop, IPortalHeader, IBelowContent
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.app.layout.navigation.interfaces import INavigationRoot

from genweb.core import HAS_CAS
from genweb.core import HAS_PAM
from genweb.core.interfaces import IHomePage
from genweb.theme.browser.interfaces import IHomePageView
from genweb.core.utils import genweb_config
from genweb.core.utils import havePermissionAtRoot
from genweb.core.utils import pref_lang
from genweb.theme.browser.interfaces import IGenwebTheme
from genweb.core.browser.viewlets import gwCSSViewletManager
from genweb.core.browser.viewlets import baseResourcesViewlet
from genweb.organs.interfaces import IGenwebOrgansLayer
from plone.app.layout.navigation.root import getNavigationRootObject


grok.context(Interface)


class viewletBase(grok.Viewlet):
    grok.baseclass()

    @memoize_contextless
    def root_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return api.portal.get()

    def genweb_config(self):
        return genweb_config()

    def pref_lang(self):
        """ Extracts the current language for the current user """
        lt = getToolByName(self.portal(), 'portal_languages')
        return lt.getPreferredLanguage()


class gwHeader(viewletBase):
    grok.name('genweb.header')
    grok.template('header')
    grok.viewletmanager(IPortalHeader)
    grok.layer(IGenwebOrgansLayer)


    def get_image_class(self):
        if self.genweb_config().treu_menu_horitzontal:
            # Is a L2 type
            return 'l2-image'
        else:
            return 'l3-image'

    def show_login(self):
        isAnon = getMultiAdapter((self.context, self.request), name='plone_portal_state').anonymous()
        return not self.genweb_config().amaga_identificacio and isAnon

    # def show_directory(self):
    #     return self.genweb_config().directori_upc

    def show_directory(self):
        show_general = self.genweb_config().directori_upc
        return show_general

    def show_directory_filtered(self):
        show_filtered = self.genweb_config().directori_filtrat
        return show_filtered

    def getURLDirectori(self, codi):
        if codi:
            return "http://directori.upc.edu/directori/dadesUE.jsp?id=%s" % codi
        else:
            return "http://directori.upc.edu"

    def get_title(self):
        title = getattr(self.genweb_config(), 'html_title_{}'.format(self.pref_lang()))
        if title:
            return title
        else:
            return u''

    def is_logo_enabled(self):
        return self.genweb_config().right_logo_enabled

    def get_right_logo_alt(self):
        return self.genweb_config().right_logo_alt

    def is_pam_installed(self):
        return HAS_PAM

    def getCustomLink(self):
        """ Custom links """
        lang = self.pref_lang()
        custom_links = {
            "ca": {
                "cl_title": self.genweb_config().cl_title_ca,
                "url": self.genweb_config().cl_url_ca,
                "image": self.genweb_config().cl_img_ca,
                "oinw": self.genweb_config().cl_open_new_window_ca,
                "enable": self.genweb_config().cl_enable_ca,
                },
            "es": {
                "cl_title": self.genweb_config().cl_title_es,
                "url": self.genweb_config().cl_url_es,
                "image": self.genweb_config().cl_img_es,
                "oinw": self.genweb_config().cl_open_new_window_es,
                "enable": self.genweb_config().cl_enable_es,
                },
            "en": {
                "cl_title": self.genweb_config().cl_title_en,
                "url": self.genweb_config().cl_url_en,
                "image": self.genweb_config().cl_img_en,
                "oinw": self.genweb_config().cl_open_new_window_en,
                "enable": self.genweb_config().cl_enable_en,
                },
            }
        return custom_links[lang]

    def getTitle(self):
        from genweb.organs.content.organsfolder import IOrgansfolder
        if IOrgansfolder.providedBy(self.context):
            if self.context.customImage:
                return 'Govern UPC - ' + str(self.context.title)
            else:
                return 'Govern UPC'
        else:
            portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
            root = getNavigationRootObject(self.context, portal_state.portal())
            physical_path = aq_inner(self.context).getPhysicalPath()
            relative = physical_path[len(root.getPhysicalPath()):]
            for i in range(len(relative)):
                now = relative[:i + 1]
                try:
                    # Some objects in path are in pending state
                    obj = aq_inner(root.restrictedTraverse(now))
                except:
                    # return default image
                    return None
                if IOrgansfolder.providedBy(obj):
                    if self.context.customImage:
                        return 'Govern UPC - ' + str(obj.title)
                    else:
                        return 'Govern UPC'

    def getLogo(self):
        from genweb.organs.content.organsfolder import IOrgansfolder
        if IOrgansfolder.providedBy(self.context):
            try:
                if self.context.customImage:
                    self.context.logoOrganFolder.filename
                    return self.context.absolute_url() + '/@@images/logoOrganFolder'
                else:
                    return None
            except:
                return None
        else:
            portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
            root = getNavigationRootObject(self.context, portal_state.portal())
            physical_path = aq_inner(self.context).getPhysicalPath()
            relative = physical_path[len(root.getPhysicalPath()):]
            for i in range(len(relative)):
                now = relative[:i + 1]
                try:
                    # Some objects in path are in pending state
                    obj = aq_inner(root.restrictedTraverse(now))
                except:
                    # return default image
                    return None
                if IOrgansfolder.providedBy(obj):
                    try:
                        if self.context.customImage:
                            obj.logoOrganFolder.filename
                            return obj.absolute_url() + '/@@images/logoOrganFolder'
                        else:
                            return None
                    except:
                        return None  # loads default image
