# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implements, implementer

from genweb.organs import _
from genweb.organs import utils


class ILaMevaVinculacioOrgansPortlet(IPortletDataProvider):
  """A portlet displaying a organs linked with me
  """


@implementer(ILaMevaVinculacioOrgansPortlet)
class Assignment(base.Assignment):
  title = _(u'Organs La Meva Vinculació')


class Renderer(base.Renderer):
  render = ViewPageTemplateFile('lamevavinculacio.pt')

  def getOwnOrgans(self):
    if not api.user.is_anonymous():
      results = []
      portal_catalog = api.portal.get_tool(name='portal_catalog')
      root_path = '/'.join(api.portal.get().getPhysicalPath())
      lt = getToolByName(self, 'portal_languages')
      lang = lt.getPreferredLanguage()
      values = portal_catalog.searchResults(
        portal_type=['genweb.organs.organgovern'],
        path=root_path + '/' + lang)
      username = api.user.get_current().id

      for obj in values:
        organ = obj.getObject()
        all_roles = api.user.get_roles(username=username, obj=organ)
        roles = [o for o in all_roles if o in ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat']]
        if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
          results.append(dict(
            url=obj.getObject().absolute_url(),
            title=obj.Title,
            color=organ.eventsColor,
            role=roles))

      return results


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()