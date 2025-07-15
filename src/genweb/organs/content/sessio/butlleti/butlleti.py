# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from io import StringIO

from operator import attrgetter
from operator import itemgetter
from plone import api
from plone.event.interfaces import IEventAccessor
from plone.folder.interfaces import IExplicitOrdering
from zope.interface import alsoProvides
from zope.i18n import translate

from genweb6.core.utils import json_response
from genweb.organs import _
from genweb.organs import utils
from genweb.organs.indicators.updating import update_indicators
from genweb.organs.utils import addEntryLog
from genweb.organs.utils import get_settings_property
from genweb.organs.utils import getLdapUserData

import ast
import csv
import datetime
import DateTime
import json
import transaction
import unicodedata
import time


class Butlleti(BrowserView):
    __call__ = ViewPageTemplateFile('butlleti.pt')

    def status(self):
        return api.content.get_state(obj=self.context)

    def PuntsOrdreDelDia(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            # value = obj.getObject()
            value = obj._unrestrictedGetObject()
            if value.portal_type == 'genweb.organs.acord':
                if value.agreement:
                    agreement = value.agreement
                else:
                    agreement = _(u"sense numeracio") if not getattr(value, 'omitAgreement', False) else False
            else:
                agreement = False
            results.append(dict(Title=obj.Title,
                                url=value.absolute_url_path(),
                                punt=value.proposalPoint,
                                acord=agreement))
            if len(value.objectIds()) > 0:
                # valuesInside = portal_catalog.searchResults(
                valuesInside = portal_catalog.unrestrictedSearchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': obj.getPath(),
                          'depth': 1})
                for item in valuesInside:
                    # subpunt = item.getObject()
                    subpunt = item._unrestrictedGetObject()
                    if subpunt.portal_type == 'genweb.organs.acord':
                        if subpunt.agreement:
                            agreement = subpunt.agreement
                        else:
                            agreement = _(u"sense numeracio") if not getattr(subpunt, 'omitAgreement', False) else False
                    else:
                        agreement = False
                    results.append(dict(Title=item.Title,
                                        url=subpunt.absolute_url_path(),
                                        punt=subpunt.proposalPoint,
                                        acord=agreement))
        return results

    def getTitle(self):
        return self.context.Title()

    def getOrganTitle(self):
        return self.context.aq_parent.Title()

    def getUnitat(self):
        return self.context.aq_parent.aq_parent.Title()

    def canView(self):
        # Permissions to GENERATE BUTLLETI
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada':
                return True
            elif estatSessio == 'realitzada':
                return True
            elif estatSessio == 'tancada':
                return True
            elif estatSessio == 'en_correccio':
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_members_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_affected_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized