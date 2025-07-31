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
from plone.app.uuid.utils import uuidToObject
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


class SignSessioView(BrowserView, utilsFD.UtilsFirmaDocumental):
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

    def hihaDocs(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.file'],
            path={'query': folder_path,
                  'depth': 3})
        if values:
            return True
        else:
            return False

    def PuntsInside(self):
        """ Retorna punts i acords d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []

        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        for obj in values:
            item = obj._unrestrictedGetObject()
            if len(item.objectIds()) > 0:
                inside = True
            else:
                inside = False
            # TODO !
            # review_state = api.content.get_state(self.context)
            # if review_state in ['realitzada', 'en_correccio']
            if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles):
                classe = "ui-state-grey"
            else:
                classe = "ui-state-grey-not_move"
            # Els acords tenen camp agreement, la resta no
            if obj.portal_type == 'genweb.organs.acord':
                if item.agreement:
                    agreement = item.agreement
                else:
                    agreement = _(u"sense numeracio")
                isPunt = False

            else:
                agreement = False
                isPunt = True

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
                                items_inside=inside,
                                info_firma=item.info_firma if hasattr(item, 'info_firma') else None))
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

            item = obj.getObject()
            if obj.portal_type == 'genweb.organs.acord':
                if item.agreement:
                    agreement = item.agreement
                else:
                    agreement = _(u"sense numeracio")
            else:
                agreement = False
            results.append(dict(
                title=obj.Title,
                portal_type=obj.portal_type,
                absolute_url=item.absolute_url(),
                proposalPoint=item.proposalPoint,
                item_path=item.absolute_url_path(),
                state=item.estatsLlista,
                agreement=agreement,
                estats=self.estatsCanvi(obj),
                css=self.getColor(obj),
                id='/'.join(item.absolute_url_path().split('/')[-2:]),
            ))
        return results

    def hasUnsentFiles(self, item, depth=1):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + item['id']
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.file'],
            path={'query': folder_path,
                  'depth': depth})
        for file in values:
            file_obj = file.getObject()
            if not getattr(file_obj, 'info_firma', None):
                file_obj.info_firma = {}
                return True
            if not isinstance(file_obj.info_firma, dict):
                file_obj.info_firma = ast.literal_eval(file_obj.info_firma)
            if file_obj.visiblefile and not file_obj.info_firma.get('public', {}).get('uploaded', False):
                return True
            if file_obj.hiddenfile and not file_obj.info_firma.get('private', {}).get('uploaded', False):
                return True

        return False

    def filesinsidePunt(self, item):
        session_path = '/'.join(self.context.getPhysicalPath()) + '/' + item['id']
        portal_catalog = api.portal.get_tool(name='portal_catalog')

        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file'],
            sort_on='getObjPositionInParent',
            path={'query': session_path,
                  'depth': 1})
        results = []
        for obj in values:
            value = obj.getObject()

            for attr in ['visiblefile', 'hiddenfile']:
                classCSS = 'fa fa-file-pdf-o'  # Es un file
                if getattr(value, attr, None):
                    classCSS += ' text-success' if attr == 'visiblefile' else ' text-error'
                    visibility = 'public' if attr == 'visiblefile' else 'private'
                    info_firma = getattr(obj.getObject(), 'info_firma', None)
                    if not info_firma:
                        info_firma = {}
                    if not isinstance(info_firma, dict):
                        info_firma = ast.literal_eval(info_firma)
                    info_firma = info_firma.get(visibility, {})
                    absolute_url = obj.getURL()
                    if info_firma.get('uploaded', False):
                        absolute_url += '/viewFileGDoc?visibility=' + visibility
                    firma_status = {
                        'sent': bool(info_firma),
                        'success': info_firma and info_firma.get('uploaded', False),
                        'failed': info_firma and not info_firma.get('uploaded', False) and not info_firma.get('replaced', False),
                        'replaced': info_firma and not info_firma.get('uploaded', False) and info_firma.get('replaced', False),
                        'cssClass': 'estatFirmaFile uploaded',
                        'message': info_firma.get('error', "")
                    }
                    if firma_status['replaced']:
                        firma_status['cssClass'] = 'estatFirmaFile replaced'
                    elif firma_status['failed']:
                        firma_status['cssClass'] = 'estatFirmaFile failed'

                    results.append(dict(
                        title=obj.Title,
                        portal_type=obj.portal_type,
                        absolute_url=absolute_url,
                        new_tab=False,
                        classCSS=classCSS,
                        id=str(item['id']) + '/' + obj.id,
                        uuid=visibility + '-' + str(obj.UID),
                        info_firma=firma_status,
                    ))

        return results

    def activeActa(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.acta'],
            path={'query': folder_path, 'depth': 1},
            sort_on='created',
            sort_order='reverse')
        if values:
            return values[0].getObject()
        else:
            return None

    def AudioInsideActa(self, acta):
        """ Retorna els fitxers d'audio creats aquí dintre (sense tenir compte estat)
        """
        if not self.hasFirma(acta):
            folder_path = '/'.join(acta.getPhysicalPath())
            portal_catalog = api.portal.get_tool(name='portal_catalog')
            values = portal_catalog.searchResults(
                portal_type='genweb.organs.audio',
                sort_on='getObjPositionInParent',
                path={'query': folder_path,
                      'depth': 1})
            if values:
                results = []
                for obj in values:
                    audio = obj.getObject().file
                    results.append(dict(title=obj.Title,
                                        absolute_url=obj.getURL(),
                                        download_url=acta.absolute_url() + '/@@download/file/' + audio.filename,
                                        content_type=audio.contentType))
                return results
        else:
            if acta.info_firma['audios']:
                results = []
                for pos in acta.info_firma['audios']:
                    audio = acta.info_firma['audios'][pos]
                    results.append(dict(title=audio['title'],
                                        absolute_url=acta.absolute_url() + '/viewAudio?pos=' + str(pos),
                                        download_url=acta.absolute_url() + '/downloadAudio?pos=' + str(pos),
                                        content_type=audio['contentType']))
                return results

        return False

    def AnnexInsideActa(self, acta):
        """ Retorna els fitxers annexos creats aquí dintre (sense tenir compte estat)
        """
        if not self.hasFirma(acta):
            folder_path = '/'.join(acta.getPhysicalPath())
            portal_catalog = api.portal.get_tool(name='portal_catalog')
            values = portal_catalog.searchResults(
                portal_type='genweb.organs.annex',
                sort_on='getObjPositionInParent',
                path={'query': folder_path,
                      'depth': 1})
            if values:
                results = []
                for obj in values:
                    annex = obj.getObject().file
                    results.append(dict(title=obj.Title,
                                        absolute_url=obj.getURL(),
                                        download_url=acta.absolute_url() + '/@@download/file/' + annex.filename,
                                        filename=annex.filename,
                                        sizeKB=annex.getSize() / 1024))
                return results
        else:
            if 'adjunts' in acta.info_firma and acta.info_firma['adjunts']:
                results = []
                for pos in acta.info_firma['adjunts']:
                    annex = acta.info_firma['adjunts'][pos]
                    results.append(dict(title=annex['title'],
                                        absolute_url=acta.absolute_url() + '/viewFile?pos=' + str(pos),
                                        download_url=acta.absolute_url() + '/downloadFile?pos=' + str(pos),
                                        filename=annex['filename'],
                                        sizeKB=annex['sizeKB']))
                return results

        return False

    def getPDFActa(self, acta):
        if not hasattr(acta, 'info_firma'):
            acta.info_firma = {}
            transaction.commit()
            acta.reindexObject()

        if not isinstance(acta.info_firma, dict):
            acta.info_firma = ast.literal_eval(acta.info_firma)

        if acta.info_firma and acta.info_firma['acta'] != {}:
            return {'filename': acta.info_firma['acta']['filename'],
                    'sizeKB': acta.info_firma['acta']['sizeKB']}

    def canFirm(self):
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        return utils.checkhasRol(['Manager', 'OG1-Secretari'], roles)

    def hasFirma(self, acta):
        return utilsFD.hasFirmaActa(acta)

    def estatFirma(self, acta):
        return utilsFD.estatFirmaActa(acta)

    def isSigned(self, acta):
        estat_firma = getattr(acta, 'estat_firma', None) or ""
        if self.hasFirma(acta) and estat_firma.lower() == 'signada':
            return True
        return False

    def checkSerieGDoc(self):
          return {'visible_gdoc': True,
                'valid_serie': True,
                'msg_error': ''}