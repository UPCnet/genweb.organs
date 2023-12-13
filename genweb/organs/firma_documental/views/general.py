# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone import api

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental import utils as utilsFD

import json
import logging
import requests

logger = logging.getLogger(__name__)


def getCopiaAutentica(self, uuid):
    fd_settings = utilsFD.get_settings_firma_documental()
    result = requests.get(fd_settings.copiesautentiques_url + '/api/copia?idDocument=' + uuid + '&idioma=CATALA', headers={'X-Api-Key': fd_settings.copiesautentiques_apikey})
    if result.status_code == 200:
        return result.content
    else:
        self.context.plone_utils.addPortalMessage(_(u'Error al consultar les dades'), 'error')
        return None


def getGDoc(self, uuid):
    fd_settings = utilsFD.get_settings_firma_documental()
    result = requests.get(fd_settings.gdoc_url + '/api/documentelectronic/' + uuid + '?uid=' + fd_settings.gdoc_user + '&hash=' + fd_settings.gdoc_hash)
    if result.status_code == 200:
        return result.content
    else:
        self.context.plone_utils.addPortalMessage(_(u'Error al consultar les dades'), 'error')
        return None


def viewCopiaAutentica(self, uuid, contentType, filename):
    organ = utils.get_organ(self.context)
    if organ.visiblegdoc:
        copia_autentica = getCopiaAutentica(self, uuid)
        if copia_autentica:
            self.request.response.setHeader('content-type', contentType)
            self.request.response.setHeader('content-disposition', 'inline; filename=' + str(filename))
            return copia_autentica

        return self.request.response.redirect(self.context.absolute_url())


def downloadCopiaAutentica(self, uuid, contentType, filename):
    organ = utils.get_organ(self.context)
    if organ.visiblegdoc:
        copia_autentica = getCopiaAutentica(self, uuid)
        if copia_autentica:
            self.request.response.setHeader('content-type', contentType)
            self.request.response.setHeader('content-disposition', 'attachment; filename=' + str(filename))
            return copia_autentica

        return self.request.response.redirect(self.context.absolute_url())


def viewGDoc(self, uuid, contentType, filename):
    organ = utils.get_organ(self.context)
    if organ.visiblegdoc:
        copia_autentica = getGDoc(self, uuid)
        if copia_autentica:
            self.request.response.setHeader('content-type', contentType)
            self.request.response.setHeader('content-disposition', 'inline; filename=' + str(filename))
            return copia_autentica

        return self.request.response.redirect(self.context.absolute_url())


def downloadGDoc(self, uuid, contentType, filename):
    organ = utils.get_organ(self.context)
    if organ.visiblegdoc:
        copia_autentica = getGDoc(self, uuid)
        if copia_autentica:
            self.request.response.setHeader('content-type', contentType)
            self.request.response.setHeader('content-disposition', 'attachment; filename=' + str(filename))
            return copia_autentica

        return self.request.response.redirect(self.context.absolute_url())


class UpdateInfoPortafirmes(BrowserView):

    def __call__(self):
        try:
            body = json.loads(self.request['BODY'])
            if body:
                idFirma = body['idPeticio']
                newEstatFirma = body['estatPeticio']

                portal_catalog = api.portal.get_tool(name='portal_catalog')
                firma = portal_catalog.searchResults(id_firma=idFirma)
                if firma:
                    firma = firma[0].getObject()

                    if firma.estat_firma != newEstatFirma:
                        firma.estat_firma = newEstatFirma
                        firma.reindexObject()
        except:
            logger.info("ERROR updateInfoPortafirmes")
