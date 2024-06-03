# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from Products.Five.browser import BrowserView

from plone import api
from plone.uuid.interfaces import IUUID

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental.views.general import downloadCopiaAutentica
from genweb.organs.firma_documental.views.general import downloadGDoc
from genweb.organs.firma_documental.views.general import viewGDoc
from genweb.organs.firma_documental.webservices import ClientFirma, ClientFirmaException, uploadFileGdoc
from genweb.organs.firma_documental.views.firmes import FirmesMixin

import ast
import datetime
import json
import logging
import os
import pdfkit
import transaction
import traceback

logger = logging.getLogger(__name__)


class ViewActa(BrowserView):

    def __call__(self):
        if not isinstance(self.context.info_firma, dict):
            self.context.info_firma = ast.literal_eval(self.context.info_firma)

        content = self.context.info_firma['acta']
        return viewGDoc(self, content['uuid'], content['contentType'], content['filename'])


class DownloadActa(BrowserView):

    def __call__(self):
        if not isinstance(self.context.info_firma, dict):
            self.context.info_firma = ast.literal_eval(self.context.info_firma)

        content = self.context.info_firma['acta']
        return downloadCopiaAutentica(self, content['uuid'], content['contentType'], content['filename'])


class ViewFile(BrowserView):

    def __call__(self):
        if 'pos' in self.request:
            if not isinstance(self.context.info_firma, dict):
                self.context.info_firma = ast.literal_eval(self.context.info_firma)
            if self.context.portal_type == 'genweb.organs.acta':
                content = self.context.info_firma['adjunts'][self.request['pos']]
            else:
                organ_tipus = self.context.organType
                roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
                content = self.context.info_firma['fitxers'][self.request['pos']]
                roles_to_check = ['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat']
                if organ_tipus == 'open_organ':
                    roles_to_check.append('OG4-Afectat')
                elif not utils.checkhasRol(roles_to_check, roles):
                    raise Unauthorized

                if not content['public'] and not utils.checkhasRol(roles_to_check, roles):
                    raise Unauthorized

            return viewGDoc(self, content['uuid'], content['contentType'], content['filename'])


class DownloadFile(BrowserView):

    def __call__(self):
        if 'pos' in self.request:
            if not isinstance(self.context.info_firma, dict):
                self.context.info_firma = ast.literal_eval(self.context.info_firma)
            if self.context.portal_type == 'genweb.organs.acta':
                content = self.context.info_firma['adjunts'][self.request['pos']]
            else:
                content = self.context.info_firma['fitxers'][self.request['pos']]
            return downloadGDoc(self, content['uuid'], content['contentType'], content['filename'])


class ViewAudio(BrowserView):

    def __call__(self):
        if 'pos' in self.request:
            if not isinstance(self.context.info_firma, dict):
                self.context.info_firma = ast.literal_eval(self.context.info_firma)

            content = self.context.info_firma['audios'][self.request['pos']]
            return viewGDoc(self, content['uuid'], content['contentType'], content['filename'])


class DownloadAudio(BrowserView):

    def __call__(self):
        if 'pos' in self.request:
            if not isinstance(self.context.info_firma, dict):
                self.context.info_firma = ast.literal_eval(self.context.info_firma)

            content = self.context.info_firma['audios'][self.request['pos']]
            return downloadGDoc(self, content['uuid'], content['contentType'], content['filename'])
