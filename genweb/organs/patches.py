# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFPlone import utils
from Products.CMFPlone.browser.navigation import get_view_url
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

from plone.app.layout.navigation.root import getNavigationRoot
from zope.component import getMultiAdapter

from genweb.theme.browser.viewlets import packages_installed

from plone.app.multilingual.interfaces import ITranslationManager
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.memoize import ram
from time import time


def breadcrumbs(self):
    context = aq_inner(self.context)
    request = self.request
    container = utils.parent(context)

    name, item_url = get_view_url(context)

    if container is None:
        return ({'absolute_url': item_url,
                 'Title': utils.pretty_title_or_id(context, context), },)

    view = getMultiAdapter((container, request), name='breadcrumbs_view')
    base = tuple(view.breadcrumbs())

    # Some things want to be hidden from the breadcrumbs
    if IHideFromBreadcrumbs.providedBy(context):
        return base

    if base:
        item_url = '%s/%s' % (base[-1]['absolute_url'], name)

    rootPath = getNavigationRoot(context)
    itemPath = '/'.join(context.getPhysicalPath())

    # don't show default pages in breadcrumbs or pages above the navigation
    # root

    installed = packages_installed()
    if 'genweb.organs' in installed:
        if (not utils.isDefaultPage(context, request) or context.portal_type == 'genweb.organs.organsfolder') \
                and not rootPath.startswith(itemPath):
            base += ({'absolute_url': item_url,
                      'Title': utils.pretty_title_or_id(context, context), },)
    else:
        if not utils.isDefaultPage(context, request) and not rootPath.startswith(itemPath):
            base += ({'absolute_url': item_url,
                      'Title': utils.pretty_title_or_id(context, context), },)

    return base


@ram.cache(lambda *args: time() // (480 * 60))
def get_alternate_languages(self):
    """Cache relative urls only. If we have multilingual sites
        and multi domain site caching absolute urls will result in
        very inefficient caching. Build absolute url in template.
    """
    tm = ITranslationManager(self.context)
    catalog = getToolByName(self.context, 'portal_catalog')
    results = catalog(TranslationGroup=tm.query_canonical())

    plone_site = getUtility(IPloneSiteRoot)
    portal_path = '/'.join(plone_site.getPhysicalPath())
    portal_path_len = len(portal_path)
    alternates = []
    for item in results:
        path_len = portal_path_len + len('{0:s}/'.format(item.Language))
        url = item.getURL(relative=1)[path_len:]
        alternates.append({
            'lang': item.Language,
            'url': url.strip('/'),
        })

    return alternates