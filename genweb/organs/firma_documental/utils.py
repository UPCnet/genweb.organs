# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from genweb.organs.firma_documental.controlpanel import IFirmaDocumentalSettings
from genweb.organs import utils

import ast
import json
import requests


def get_settings_firma_documental():
    return getUtility(IRegistry).forInterface(IFirmaDocumentalSettings)


def is_valid_serie_gdoc(self):
    organ = utils.get_organ(self.context)
    if organ.visiblegdoc:
        firma_settings = get_settings_firma_documental()
        try:
            result = requests.get(firma_settings.gdoc_url + '/api/serie/' + organ.serie + '?hash=' + firma_settings.gdoc_hash, timeout=10)
            if result.status_code == 200:
                return {'visible_gdoc': True,
                        'valid_serie': True,
                        'msg_error': ''}
            else:
                content = json.loads(result.content)
                if 'codi' in content:
                    if content['codi'] == 503:
                        return {'visible_gdoc': True,
                                'valid_serie': False,
                                'msg_error': u'GDoc: Contacta amb algun administrador de la web perquè revisi la configuració'}

                    elif content['codi'] == 528:
                        return {'visible_gdoc': True,
                                'valid_serie': False,
                                'msg_error': u'GDoc: La sèrie documental configurada no existeix'}

                return {'visible_gdoc': True,
                        'valid_serie': False,
                        'msg_error': u'GDoc: Contacta amb algun administrador de la web perquè revisi la configuració'}

        except:
            return {'visible_gdoc': False,
                    'valid_serie': False,
                    'msg_error': u'GDoc timeout: Contacta amb algun administrador de la web perquè revisi la configuració'}
    else:
        return {'visible_gdoc': False,
                'valid_serie': False,
                'msg_error': ''}


class UtilsFirmaDocumental():

    def hasFirma(self):
        info_firma = getattr(self.context, 'info_firma', None)
        if info_firma:
            if not isinstance(info_firma, dict):
                info_firma = ast.literal_eval(info_firma)
                self.context.info_firma = info_firma

            return 'unitatDocumental' in info_firma and 'enviatASignar' in info_firma and info_firma['enviatASignar']
        else:
            info_firma = {}
            return False

    def estatFirma(self):
        estat_firma = getattr(self.context, 'estat_firma', None)
        if estat_firma:
            return self.context.estat_firma.lower()
        else:
            return 'pendent'

    def checkSerieGDoc(self):
        if utils.isManager(self) or utils.isSecretari(self):
            return is_valid_serie_gdoc(self)

        return {'visible_gdoc': False,
                'valid_serie': False,
                'msg_error': ''}
