# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone import api

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental import utils as utilsFD
from genweb.organs.firma_documental.views import TIMEOUT
from genweb.organs.firma_documental.views.general import downloadCopiaAutentica
from genweb.organs.firma_documental.views.general import downloadGDoc
from genweb.organs.firma_documental.views.general import viewCopiaAutentica
from genweb.organs.firma_documental.views.general import viewGDoc
from genweb.organs.firma_documental.webservices import ClientFirma, ClientFirmaException, uploadFileGdoc
from plone.namedfile.file import NamedBlobFile

#import Acquisition.ImplicitAcquisitionWrapper
from Acquisition import ImplicitAcquisitionWrapper

import ast
import datetime
import json
import logging
import os
import pdfkit
import requests
import transaction

logger = logging.getLogger(__name__)


class SignSessio(BrowserView):
    def canView(self):
        return True

    def canModify(self):
        return True

    def canViewVoteButtons(self):
        return True

    def canViewAddQuorumButtons(self):
        return True

    def canViewManageQuorumButtons(self):
        return True

    def canViewManageVote(self):
        return True

    def canViewResultsVote(self):
        return True

    def hihaPunts(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            path={'query': folder_path,
                  'depth': 1})
        if values:
            return True
        else:
            return False

    def getColor(self, data):
        # assign custom colors on organ states
        return utils.getColor(data)

    def estatsCanvi(self, data):
        # assign custom colors on organ states
        return utils.estatsCanvi(data)

    def getTitlePrompt(self):
        return _(u'title_prompt_votacio')

    def getErrorPrompt(self):
        return _(u'error_prompt_votacio')

    def PuntsInside(self):
        """ Retorna punts i acords d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        
        results = []

        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        for obj in values:
            agreement = False
            isPunt = True
            # canOpenVote = False
            # canCloseVote = False
            # canRecloseVote = False
            titleEsmena = ''
            # classVote = False
            # hasVote = False
            # favorVote = False
            # againstVote = False
            whiteVote = False

            if obj.portal_type == 'genweb.organs.acta' or obj.portal_type == 'genweb.organs.audio':
                # add actas to view_template for ordering but dont show them
                item = obj._unrestrictedGetObject()
                results.append(dict(id=obj.id,
                                    classe='hidden',
                                    show=False,
                                    agreement=False))
                continue

            elif obj.portal_type == 'Folder':
                # la carpeta es pels punts proposats!
                continue

            item = obj._unrestrictedGetObject()
            if len(item.objectIds()) > 0:
                inside = True
            else:
                inside = False
            # TODO !
            # review_state = api.content.get_state(self.context)
            # if review_state in ['realitzada', 'en_correccio']
            # if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles):
            #     classe = "ui-state-grey"
            # else:
            #     classe = "ui-state-grey-not_move"
            # Els acords tenen camp agreement, la resta no
            classe = "ui-state-grey-not_move"
            if obj.portal_type == 'genweb.organs.acord':
                if item.agreement:
                    agreement = item.agreement
                else:
                    agreement = _(u"sense numeracio")
                isPunt = False

                # acord = obj.getObject()
                # votacio = acord
                # canOpenVote = acord.estatVotacio is None
                # canCloseVote = acord.estatVotacio == 'open'

                # if canOpenVote:
                #     acord_folder_path = '/'.join(item.getPhysicalPath())
                #     esmenas = portal_catalog.unrestrictedSearchResults(
                #         portal_type=['genweb.organs.votacioacord'],
                #         sort_on='getObjPositionInParent',
                #         path={'query': acord_folder_path,
                #                 'depth': 1})

                #     for esmena in esmenas:
                #         if esmena.getObject().estatVotacio == 'open':
                #             canRecloseVote = acord.id + '/' + esmena.id
                #             titleEsmena = esmena.Title
                #             votacio = esmena.getObject()
                #             canOpenVote = False

                # currentUser = api.user.get_current().id

                # if not isinstance(votacio.infoVotacio, dict):
                #     if votacio.infoVotacio == None or votacio.infoVotacio == "":
                #         votacio.infoVotacio = {}
                #     else:
                #         votacio.infoVotacio = ast.literal_eval(votacio.infoVotacio)

                # hasVote = currentUser in votacio.infoVotacio
                # if hasVote:
                #     favorVote = votacio.infoVotacio[currentUser] == 'favor'
                #     againstVote = votacio.infoVotacio[currentUser] == 'against'
                #     whiteVote = votacio.infoVotacio[currentUser] == 'white'

                # if votacio.estatVotacio == None:
                #     classVote = 'fa fa-bar-chart'
                # else:
                #     if votacio.tipusVotacio == 'public':
                #         classVote = 'fa fa-pie-chart'
                #     else:
                #         classVote = 'fa fa-user-chart'

            results.append(dict(title=obj.Title,
                                portal_type=obj.portal_type,
                                absolute_url=item.absolute_url(),
                                item_path=item.absolute_url_path(),
                                proposalPoint=item.proposalPoint,
                                agreement=agreement,
                                state=item.estatsLlista,
                                css=self.getColor(obj),
                                estats=self.estatsCanvi(obj),
                                id=obj.id,
                                show=True,
                                isPunt=isPunt,
                                classe=classe,
                                # canOpenVote=canOpenVote,
                                # canCloseVote=canCloseVote,
                                # canRecloseVote=canRecloseVote,
                                # titleEsmena=titleEsmena,
                                # hasVote=hasVote,
                                # classVote=classVote,
                                # favorVote=favorVote,
                                # againstVote=againstVote,
                                whiteVote=whiteVote,
                                items_inside=inside))
        return results

    def filesinsidePunt(self, item):
        session_path = '/'.join(self.context.getPhysicalPath()) + '/' + item['id']
        portal_catalog = api.portal.get_tool(name='portal_catalog')

        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file', 'genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': session_path,
                  'depth': 1})
        results = []
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        for obj in values:
            value = obj.getObject()
            if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles:
                # Editor i Secretari veuen contingut. NO obren en finestra nova
                if obj.portal_type == 'genweb.organs.file':
                    classCSS = 'fa fa-file-pdf-o'  # Es un file
                    if value.visiblefile and value.hiddenfile:
                        classCSS = 'fa fa-file-pdf-o text-success double-icon'
                    elif value.hiddenfile:
                        classCSS = 'fa fa-file-pdf-o text-error'
                    elif value.visiblefile:
                        classCSS = 'fa fa-file-pdf-o text-success'
                else:
                    classCSS = 'fa fa-file-text-o'  # Es un DOC
                    if value.defaultContent and value.alternateContent:
                        classCSS = 'fa fa-file-text-o text-success double-icon'
                    elif value.alternateContent:
                        classCSS = 'fa fa-file-text-o text-error'
                    elif value.defaultContent:
                        classCSS = 'fa fa-file-text-o text-success'
                # si està validat els mostrem tots
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=obj.getURL(),
                                    new_tab=False,
                                    classCSS=classCSS,
                                    id=str(item['id']) + '/' + obj.id))
            else:
                # Anonim / Afectat / Membre veuen obrir en finestra nova dels fitxers.
                # Es un document, mostrem part publica si la té
                if obj.portal_type == 'genweb.organs.document':
                    classCSS = 'fa fa-file-text-o'
                    if value.defaultContent and value.alternateContent:
                        if 'OG3-Membre' in roles:
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL(),
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                        else:
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL(),
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                    elif value.defaultContent:
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL(),
                                            new_tab=True,
                                            classCSS=classCSS,
                                            id=str(item['id']) + '/' + obj.id))
                    elif value.alternateContent:
                        if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles:
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL(),
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                # es un fitxer, mostrem part publica si la té
                if obj.portal_type == 'genweb.organs.file':
                    classCSS = 'fa fa-file-pdf-o'
                    if value.visiblefile and value.hiddenfile:
                        if 'OG3-Membre' in roles:
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL() + '/@@display-file/hiddenfile/' + value.hiddenfile.filename,
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                        else:
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL() + '/@@display-file/visiblefile/' + value.visiblefile.filename,
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                    elif value.visiblefile:
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL() + '/@@display-file/visiblefile/' + value.visiblefile.filename,
                                            new_tab=True,
                                            classCSS=classCSS,
                                            id=str(item['id']) + '/' + obj.id))
                    elif value.hiddenfile:
                        if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles:
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL() + '/@@display-file/hiddenfile/' + value.hiddenfile.filename,
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
        return results


    def SubpuntsInside(self, data):
            """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
            """
            portal_catalog = api.portal.get_tool(name='portal_catalog')
            folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + data['id']
            values = portal_catalog.unrestrictedSearchResults(
                portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                sort_on='getObjPositionInParent',
                path={'query': folder_path,
                    'depth': 1})
            results = []
            for obj in values:

                canOpenVote = False
                canCloseVote = False
                canRecloseVote = False
                titleEsmena = ''
                classVote = False
                hasVote = False
                favorVote = False
                againstVote = False
                whiteVote = False

                item = obj.getObject()
                if obj.portal_type == 'genweb.organs.acord':
                    if item.agreement:
                        agreement = item.agreement
                    else:
                        agreement = _(u"sense numeracio")

                    votacio = item
                    canOpenVote = item.estatVotacio == None
                    canCloseVote = item.estatVotacio == 'open'

                    if canOpenVote:
                        acord_folder_path = '/'.join(item.getPhysicalPath())
                        esmenas = portal_catalog.unrestrictedSearchResults(
                            portal_type=['genweb.organs.votacioacord'],
                            sort_on='getObjPositionInParent',
                            path={'query': acord_folder_path,
                                'depth': 1})

                        for esmena in esmenas:
                            if esmena.getObject().estatVotacio == 'open':
                                canRecloseVote = '/'.join(item.absolute_url_path().split('/')[-2:]) + '/' + esmena.id
                                titleEsmena = esmena.Title
                                votacio = esmena.getObject()
                                canOpenVote = False

                    currentUser = api.user.get_current().id

                    if not isinstance(votacio.infoVotacio, dict):
                        if votacio.infoVotacio == None or votacio.infoVotacio == "":
                            votacio.infoVotacio = {}
                        else:
                            votacio.infoVotacio = ast.literal_eval(votacio.infoVotacio)

                    hasVote = currentUser in votacio.infoVotacio
                    if hasVote:
                        favorVote = votacio.infoVotacio[currentUser] == 'favor'
                        againstVote = votacio.infoVotacio[currentUser] == 'against'
                        whiteVote = votacio.infoVotacio[currentUser] == 'white'

                    if votacio.estatVotacio == None:
                        classVote = 'fa fa-bar-chart'
                    else:
                        if votacio.tipusVotacio == 'public':
                            classVote = 'fa fa-pie-chart'
                        else:
                            classVote = 'fa fa-user-chart'
                else:
                    agreement = False
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=item.absolute_url(),
                                    proposalPoint=item.proposalPoint,
                                    item_path=item.absolute_url_path(),
                                    state=item.estatsLlista,
                                    agreement=agreement,
                                    estats=self.estatsCanvi(obj),
                                    css=self.getColor(obj),
                                    canOpenVote=canOpenVote,
                                    canCloseVote=canCloseVote,
                                    canRecloseVote=canRecloseVote,
                                    titleEsmena=titleEsmena,
                                    hasVote=hasVote,
                                    classVote=classVote,
                                    favorVote=favorVote,
                                    againstVote=againstVote,
                                    whiteVote=whiteVote,
                                    id='/'.join(item.absolute_url_path().split('/')[-2:])))
            return results
