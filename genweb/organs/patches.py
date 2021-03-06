# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFPlone import utils
from Products.CMFPlone.browser.navigation import get_view_url
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

from plone.app.layout.navigation.root import getNavigationRoot
from zope.component import getMultiAdapter

from genweb.theme.browser.viewlets import packages_installed


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
