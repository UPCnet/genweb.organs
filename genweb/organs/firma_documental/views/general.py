# -*- coding: utf-8 -*-
from genweb.organs import _
from genweb.organs.firma_documental import utils

import requests


def getCopiaAutentica(self, uuid):
    fd_settings = utils.get_settings_firma_documental()
    result = requests.get(fd_settings.copiesautentiques_url + '/api/copia?idDocument=' + uuid + '&idioma=CATALA', headers={'X-Api-Key': fd_settings.copiesautentiques_apikey})
    if result.status_code == 200:
        return result.content
    else:
        self.context.plone_utils.addPortalMessage(_(u'Error al consultar les dades'), 'error')
        return None


def getGDoc(self, uuid):
    fd_settings = utils.get_settings_firma_documental()
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
