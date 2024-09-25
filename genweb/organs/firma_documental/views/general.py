# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from genweb.organs.firma_documental.webservices import ClientFirma
from plone import api
from plone.app.uuid.utils import uuidToObject

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
        # Ahora al signar un documento se llama a la función timbrarFiles que devuelve un id con el documento
        # ya timbrado, por lo que no es necesario llamar a getCopiaAutentica
        #
        # if self.context.portal_type in ['genweb.organs.punt', 'genweb.organs.subpunt', 'genweb.organs.acord']:
        #     acta = uuidToObject(self.context.info_firma['related_acta'])
        # else:
        #     acta = self.context
        # if acta.estat_firma.lower() == 'signada':
        #     copia_autentica = getCopiaAutentica(self, uuid)
        # else:
        copia_autentica = getGDoc(self, uuid)
        if copia_autentica:
            self.request.response.setHeader('content-type', contentType)
            self.request.response.setHeader('content-disposition', 'inline; filename=' + str(filename))
            return copia_autentica

        return self.request.response.redirect(self.context.absolute_url())


def downloadGDoc(self, uuid, contentType, filename):
    organ = utils.get_organ(self.context)
    if organ.visiblegdoc:
        if self.context.estat_firma.lower() == 'signada':
            copia_autentica = getCopiaAutentica(self, uuid)
        else:
            copia_autentica = getGDoc(self, uuid)
        if copia_autentica:
            self.request.response.setHeader('content-type', contentType)
            self.request.response.setHeader('content-disposition', 'attachment; filename=' + str(filename))
            return copia_autentica

        return self.request.response.redirect(self.context.absolute_url())


class UpdateInfoPortafirmes(BrowserView):

    # def _timbrarFile(self, info_firma):
    #     client = ClientFirma()
    #     logger.info("Timbrant document: [%s] %s " % (info_firma['id'], info_firma['filename']))
    #     res = client.timbrarDocumentGdoc(info_firma['id'])
    #     info_firma['id'] = res['idDocument']
    #     logger.info("Document timbrat correctament: [%s] %s " % (info_firma['id'], info_firma['filename']))
    #     return info_firma

    # def timbrarFiles(self, context):
    #     files = utils.getFilesSessio(context)
    #     for file in files:
    #         if file.visiblefile and file.info_firma.get('public', {}).get('uploaded', False):
    #             file.info_firma['public'] = self._timbrarFile(file.info_firma['public'])

    #         if file.hiddenfile and file.info_firma.get('private', {}).get('uploaded', False):
    #             file.info_firma['private'] = self._timbrarFile(file.info_firma['private'])
    #         file.reindexObject()

    #     logger.info("Tots els documents timbrats correctament")

    def __call__(self):
        logger.info("Notificacio de portafirmes")
        try:
            body = json.loads(self.request['BODY'])
            if not body:
                return

            idFirma = body['idPeticio']
            newEstatFirma = body['estatPeticio']
            logger.info("id de la firma: " + str(idFirma) + ". Estat: " + newEstatFirma)
            portal_catalog = api.portal.get_tool(name='portal_catalog')

            firma = portal_catalog.searchResults(id_firma=str(idFirma))
            if not firma:
                return

            firma = firma[0].getObject()

            if firma.estat_firma != newEstatFirma:
                firma.estat_firma = newEstatFirma
                firma.reindexObject()

            # if firma.estat_firma.lower() == 'signada':
            #     self.timbrarFiles(context=firma)

        except Exception as e:
            logger.exception("ERROR updateInfoPortafirmes. Exception: " + str(e))
