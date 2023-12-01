#-*- coding: utf-8 -*-

import requests
import json
import logging
import datetime

import unicodedata

from plone import api
from requests.exceptions import ConnectTimeout, ConnectionError, HTTPError, ReadTimeout
from genweb.organs.firma_documental.utils import get_settings_firma_documental

logger = logging.getLogger(__name__)


class ClientFirmaException(Exception):
    def __init__(self, url, message='', status=None, response=None, timeout=False):
        self.url = url
        self.message = message
        self.status = status
        self.response = response
        self.timeout = timeout

    def __str__(self):
        if self.timeout:
            return '(%s) Request timeout: %s' % (self.url, self.message)
        if self.status:
            return '(%s) Request failed with status [%s]: %s' % (self.url, self.status, self.message)
        return '(%s) Request failed: %s' % (self.url, self.message)


class ClientFirma(object):
    def __init__(self, settings=None, timeout=15):
        self.settings = settings or get_settings_firma_documental()
        self.timeout = timeout

    def deleteSerieDocumental(self, unitatDocumental):
        url = self.settings.gdoc_url + '/api/udch/' + unitatDocumental + '/esborrar?&hash=' + self.settings.gdoc_hash
        return json.loads(
            self._request('DELETE', url, timeout=self.timeout).content
        )

    def getCodiExpedient(self, serie):
        url = self.settings.codiexpedient_url + '/api/codi?serie=' + serie
        headers = {
            'X-Api-Key': self.settings.codiexpedient_apikey
        }

        return json.loads(
            self._request('GET', url, headers=headers).content
        )

    def createSerieDocumental(self, serie, expedient, titolPropi):
        url = self.settings.gdoc_url + '/api/serie/' + serie + '/udch?uid=' + self.settings.gdoc_user + '&hash=' + self.settings.gdoc_hash
        data_exp = {
            'expedient': expedient,
            'titolPropi': titolPropi
        }
        return json.loads(
            self._request('POST', url, json_data=data_exp, timeout=self.timeout).content
            )

    def uploadFitxerGDoc(self, expedient, fitxer, is_acta=False):
        if not isinstance(fitxer, dict):
            fitxer = {'fitxer': [fitxer.filename, fitxer.open().read(), fitxer.contentType]}
        filename = fitxer['fitxer'][0]
        # Limpiar caracteres especiales
        fitxer['fitxer'][0] = ''.join(
            [
                c if ord(c) < 128 else ' '
                for c in unicodedata.normalize('NFD', unicode(filename))
                if unicodedata.category(c) != 'Mn'
            ]
        )

        url = self.settings.gdoc_url + '/api/pare/' + str(expedient) + '/doce?uid=' + self.settings.gdoc_user + '&hash=' + self.settings.gdoc_hash
        data = {
            'tipusDocumental': "452" if is_acta else '906340',
            'idioma': 'CA',
            'nomAplicacioCreacio': 'Govern UPC',
            'autors': "[{'id': '1291399'}]",
            'agentsAmbCodiEsquemaIdentificacio': False,
            'validesaAdministrativa': True
        }
        return json.loads(
            self._request('POST', url, data=data, files=fitxer, timeout=self.timeout).content
        )

    def getInfoElement(self, idElement):
        url = self.settings.gdoc_url + '/api/doce/' + str(idElement) + '/consulta?hash=' + self.settings.gdoc_hash
        return json.loads(
            self._request('GET', url, timeout=self.timeout).content
        )

    def uploadActaPortafirmes(self, acta_title, acta_uuid, documents_annexos, signants):
        url = self.settings.portafirmes_url
        data_sign = {
            "descripcioPeticio": "Signatura acta" + ' - ' + acta_title,
            "documents": [
                {
                    "paginaSignaturaVisible": 1,
                    "codi": acta_uuid,
                }
            ],
            "passosPeticio": [{
                    "nivellSignatura": "CDA",
                    "signants": [{"commonName": signant}]
                } for signant in signants],
            "promocionar": "S",
            "codiCategoria": "CAT43",
            "codiTipusSignatura": "ATTACHED_VISIBLE_MARGE",
            "dataLimit": (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y %H:%M:00"),
            "emissor": "Govern UPC",
            "informacio": "Signatura acta" + ' - ' + acta_title,
            "motiusRebuig": [
                {
                    "codi": "Inacabada",
                    "descripcio": "Petició inacabada"
                }
            ],
            "documentsAnnexos": documents_annexos,
            "callbackUrl": api.portal.get().absolute_url() + '/updateInfoPortafirmes'
        }
        return json.loads(
            self._request('POST', url, json_data=data_sign, headers={'X-Api-Key': self.settings.portafirmes_apikey}, timeout=60).content
        )

    def _request(self, method, url, data=None, json_data=None, headers=None, files=None, timeout=None):
        timeout = timeout or self.timeout
        try:
            res = requests.request(method, url, data=data, json=json_data, headers=headers, files=files, timeout=timeout)
        except (ConnectTimeout, ReadTimeout):
            raise ClientFirmaException(url, 'ClientFirmaException', timeout=True)
        except ConnectionError as e:
            raise ClientFirmaException(url, message=str(e))

        try:
            res.raise_for_status()
        except HTTPError as e:
            raise ClientFirmaException(
                url,
                message=str(e),
                status=res.status_code,
                response=json.loads(res.content)
            )

        return res


def uploadFileGdoc(expedient, file, filename=None, is_acta=False):
    if not isinstance(file, dict):
        file = {'fitxer': [filename or file.filename, file.open().read(), file.contentType]}

    client = ClientFirma()

    upload_step = 'uploadFile'
    try:
        logger.info('Puja del fitxer al gdoc - ' + file['fitxer'][0])
        content_file = client.uploadFitxerGDoc(expedient=expedient, fitxer=file, is_acta=is_acta)
        logger.info("S'ha creat correctament el fitxer")

        upload_step = 'getInfoElement'
        logger.info('Petició per demanar el uuid del fitxer')
        content_info_file = client.getInfoElement(content_file['idElementCreat'])
        logger.info("S'ha obtingut correctament el uuid del fitxer")

    except ClientFirmaException as e:
        error = 'ERROR. Puja del fitxer al gdoc.' if upload_step == 'uploadFile' else 'ERROR. Demanar el uuid del fitxer.'
        logger.error(error)
        raise e
    return {
        'id': str(content_file['idElementCreat']),
        'uuid': str(content_info_file['documentElectronic']['uuid']),
        'filename': file['fitxer'][0],
        'contentType': file['fitxer'][2]
    }
