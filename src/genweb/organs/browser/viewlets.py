# -*- coding: utf-8 -*-
from plone import api
from Acquisition import aq_inner
from zope.interface import Interface
from zope.component import getMultiAdapter
from plone.memoize.view import memoize_contextless
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.interfaces import IPortalHeader
from genweb6.core import HAS_PAM
# from genweb6.core.utils import genweb_config
from genweb.organs.interfaces import IGenwebOrgansLayer
from plone.app.layout.navigation.root import getNavigationRootObject
from genweb.organs.content.organsfolder.organsfolder import IOrgansfolder
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.view import memoize_contextless



class viewletBase(ViewletBase):

    @memoize_contextless
    def root_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return api.portal.get()

    # def genweb_config(self):
    #     return genweb_config()

    @memoize_contextless
    def pref_lang(self):
        lt = api.portal.get_tool(name='portal_languages')
        lang = lt.getPreferredLanguage()
        if lang not in ['ca', 'es', 'en']:
            lang = 'ca'
        return lang


class gwHeader(BrowserView):
    index = ViewPageTemplateFile("../viewlets_templates/header.pt")

    def __call__(self):
        return self.index()

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
            return "https://directori.upc.edu/directori/dadesUE.jsp?id=%s" % codi
        else:
            return "https://directori.upc.edu"

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
                "enable": self.genweb_config().cl_enable_ca},
            "es": {
                "cl_title": self.genweb_config().cl_title_es,
                "url": self.genweb_config().cl_url_es,
                "image": self.genweb_config().cl_img_es,
                "oinw": self.genweb_config().cl_open_new_window_es,
                "enable": self.genweb_config().cl_enable_es},
            "en": {
                "cl_title": self.genweb_config().cl_title_en,
                "url": self.genweb_config().cl_url_en,
                "image": self.genweb_config().cl_img_en,
                "oinw": self.genweb_config().cl_open_new_window_en,
                "enable": self.genweb_config().cl_enable_en},
        }
        return custom_links[lang]

    def getTitle(self):
        if IOrgansfolder.providedBy(self.context):
            return dict(title='Govern UPC - ' + str(self.context.title),
                        url=self.context.absolute_url())
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
                    return dict(title='Govern UPC - ' + str(obj.title),
                                url=obj.absolute_url())
                except:
                    # return default text if problems...
                    return dict(title='Govern UPC',
                                url=self.context.absolute_url())
            # By default returns Site Title
            return dict(title='Govern UPC',
                        url=self.context.absolute_url())

    def getLogo(self):
        if IOrgansfolder.providedBy(self.context):
            if self.context.customImage:
                if hasattr(self.context.logoOrganFolder, 'filename'):
                    return self.context.absolute_url() + '/@@images/logoOrganFolder'
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
                    if IOrgansfolder.providedBy(obj):
                        if obj.customImage:
                            if hasattr(obj.logoOrganFolder, 'filename'):
                                return obj.absolute_url() + '/@@images/logoOrganFolder'
                except:
                    # return default Logo
                    return None

        return None
