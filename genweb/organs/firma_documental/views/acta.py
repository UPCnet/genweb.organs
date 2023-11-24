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


class SignActa(BrowserView):

    def getSignants(self, organ):
        signants = organ.signants_acta
        if signants:
            return signants.split(', ')
        return None

    def generateActaPDF(self):
        options = {'cookie': [('__ac', self.request.cookies['__ac']),
                              ('I18N_LANGUAGE', self.request.cookies.get('I18N_LANGUAGE', 'ca'))]}

        pdfkit.from_url(self.context.absolute_url() + '/printActa', '/tmp/' + self.context.id + '.pdf', options=options)
        return open('/tmp/' + self.context.id + '.pdf', 'rb')

    def removeActaPDF(self):
        try:
            os.remove('/tmp/' + self.context.id + '.pdf')
        except:
            pass

    def getFilesSessio(self, portal_type=None):
        if not portal_type:
            portal_type = ['genweb.organs.file', 'genweb.organs.document']
        else:
            portal_type = [portal_type]
        portal_catalog = api.portal.get_tool('portal_catalog')
        session = utils.get_session(self.context)
        session_path = '/'.join(session.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type=portal_type,
            sort_on='getObjPositionInParent',
            path={'query': session_path}
        )
        return [(val.getObject(), val.getObject().getParentNode()) for val in values]

    def uploadFilesGdoc(self, id_exp, files, save_title=False, save_size=False):
        uploaded_files = {}
        for idx, file_content in enumerate(files):
            file = file_content.file if not isinstance(file_content, NamedBlobFile) else file_content
            info_adjunt = uploadFileGdoc(id_exp, file)
            if save_title and not isinstance(file_content, NamedBlobFile):
                info_adjunt['title'] = file_content.title
            if save_size and not isinstance(file_content, NamedBlobFile):
                info_adjunt['sizeKB'] = file.getSize() / 1024
            uploaded_files.update({str(idx): info_adjunt})
            self.context.reindexObject()
        return uploaded_files

    def uploadFilesSessioGdoc(self, id_exp, files):
        uploaded_files = {}
        idx = 0
        for file_content, parent_container in files:
            filename_append = 'Informe sobre '
            if parent_container.portal_type == 'genweb.organs.acord':
                filename_append = 'Acord [%s] ' % (parent_container.agreement or 'Acord sense numerar')

            if file_content.visiblefile:
                info_file = uploadFileGdoc(
                    expedient=id_exp,
                    file=file_content.visiblefile,
                    filename=('Public - ' + filename_append + file_content.visiblefile.filename)
                )
                uploaded_files.update({str(idx): info_file})
                idx += 1

            if file_content.hiddenfile:
                info_file = uploadFileGdoc(
                    expedient=id_exp,
                    file=file_content.hiddenfile,
                    filename=('Restringit - ' + filename_append + file_content.hiddenfile.filename)
                )
                info_file.update({'title': file_content.title, 'sizeKB': file_content.hiddenfile.getSize() / 1024})
                uploaded_files.update({str(idx): info_file})
                idx += 1

        return uploaded_files

    def __call__(self):
        import ipdb; ipdb.set_trace()
        error_to_msg_map = {
            'deleteSerieDocumental': {
                'console_log': '0.ERROR. Eliminació serie documental en gdoc per tornar-la a crear.',
                'portal_msg': _(u'GDoc: No s\'ha pogut eliminar els contiguts de GDoc per tornar-los a crear.')
            },
            'getCodiExpedidElementCreatient': {
                'console_log': '2.ERROR. Petició per demanar el codi del expedient.',
                'portal_msg': _(u'GDoc: No s\'ha pogut obtenir el codi del expedient: Contacta amb algun administrador de la web perquè revisi la configuració.')
            },
            'createSerieDocumental': {
                'console_log': '3.ERROR. Creació de la serie documental en gdoc.',
                'portal_msg': _(u'GDoc: No s\'ha pogut crear la serie documental: Contacta amb algun administrador de la web perquè revisi la configuració.'),
                'portal_msg_noExisteix': _(u'GDoc: No s\'ha pogut crear la serie documental: La serie documental no existeix.'),
                'choose_portal_msg': lambda resp: 'portal_msg_noExisteix' if resp['codi'] and resp['codi'] == 528 else 'portal_msg'
            },
            'uploadActaGDoc': {
                'console_log': '4.ERROR. Puja de l\'acta al gdoc.',
                'portal_msg': _(u'GDoc: No s\'ha pogut pujar l\'acta: Contacta amb algun administrador de la web perquè revisi la configuració.')
            },
            'uploadAdjuntGDoc': {
                'console_log': '5.ERROR. Puja del fitxer adjunt al gdoc.',
                'portal_msg': _(u'GDoc: No s\'ha pogut pujar el fitxer adjunt: Contacta amb algun administrador de la web perquè revisi la configuració.')
            },
            'uploadAudioGDoc': {
                'console_log': '6.ERROR. Puja del àudio al gdoc.',
                'portal_msg': _(u'GDoc: No s\'ha pogut pujar el àudio: Contacta amb algun administrador de la web perquè revisi la configuració.')
            },
            'uploadSessionFiles': {
                'console_log': '7.ERROR. Puja dels fitxers de la sessió al gdoc.',
                'portal_msg': _(u'GDoc: No s\'ha pogut pujar els fitxers de la sessió: Contacta amb algun administrador de la web perquè revisi la configuració.')
            },
            'uploadURLFile': {
                'console_log': '8.ERROR. Puja del fitxer .url al gdoc.',
                'portal_msg': _(u'GDoc: No s\'ha pogut pujar el fitxer .url: Contacta amb algun administrador de la web perquè revisi la configuració.')
            },
            'uploadActaPortafirmes': {
                'console_log': '9.ERROR. Petició de la firma al portafirmes.',
                'portal_msg': _(u'Portafirmes: No s\'ha pogut enviar la petició de la firma: Contacta amb algun administrador de la web perquè revisi la configuració.'),
                'portal_msg_supera_tamany': _(u'Portafirmes: No s\'ha pogut enviar la petició de la firma: El tamany dels fitxers supera el màxim permès.'),
                'choose_portal_msg': lambda resp: 'portal_msg_supera_tamany' if 'tamany' in json.dumps(resp) else 'portal_msg'
            }
        }

        if not isinstance(self.context.info_firma, dict):
            self.context.info_firma = ast.literal_eval(self.context.info_firma)

        if self.context.info_firma and 'enviatASignar' in self.context.info_firma and self.context.info_firma['enviatASignar']:
            return self.request.response.redirect(self.context.absolute_url())

        organ = utils.get_organ(self.context)
        signants = self.getSignants(organ)

        if not signants:
            self.context.plone_utils.addPortalMessage(_(u'No hi ha secretaris per firmar l\'acta.'), 'error')
            return self.request.response.redirect(self.context.absolute_url())

        if not organ.visiblegdoc:
            return

        client = ClientFirma()
        sign_step = ""

        try:
            sign_step = "deleteSerieDocumental"
            if self.context.info_firma and 'unitatDocumental' in self.context.info_firma and self.context.info_firma['unitatDocumental']:
                logger.info('0. Eliminació serie documental en gdoc per tornar-la a crear')
                client.deleteSerieDocumental(self.context.info_firma['unitatDocumental'])
                logger.info('0.1. S\'ha eliminat correctament la serie documental en gdoc')

            logger.info('1. Iniciant firma de l\'acta - ' + self.context.title)

            sign_step = "getCodiExpedient"
            logger.info('2. Demamant codi del expedient al servei generadorcodiexpedient')
            content_codi = client.getCodiExpedient(organ.serie)
            logger.info('2.1. S\'ha obtingut correctament el codi del expedient')

            now = datetime.datetime.now()
            codi_expedient = now.strftime("%Y") + '-' + content_codi['codi']

            sign_step = "createSerieDocumental"
            logger.info('3. Creació de la serie documental en gdoc')
            content_exp = client.createSerieDocumental(
                serie=organ.serie,
                expedient=codi_expedient,
                titolPropi=codi_expedient + ' - ' + self.context.title
            )

            logger.info('3.1. S\'ha creat correctament la serie documental')

            if not isinstance(self.context.info_firma, dict):
                self.context.info_firma = ast.literal_eval(self.context.info_firma)
            self.context.info_firma.update({
                'unitatDocumental': str(content_exp['idElementCreat']),
                'acta': {},
                'adjunts': {},
                'audios': {},
                'url': {},
                'sessio': {
                    'fitxers': {},
                    'documents': {}
                },
                'enviatASignar': False
            })
            self.context.reindexObject()

            actaPDF = self.generateActaPDF()
            sign_step = "uploadActaGDoc"
            logger.info('4. Puja de l\'acta al gdoc')
            self.context.info_firma['acta'] = uploadFileGdoc(
                content_exp['idElementCreat'],
                {'fitxer': (self.context.id + '.pdf', actaPDF.read(), 'application/pdf')},
                is_acta=True
            )
            self.context.info_firma['acta'].update({
                'sizeKB': os.path.getsize('/tmp/' + self.context.id + '.pdf') / 1024
            })

            logger.info('5. Puja dels fitxers adjunts al gdoc')
            sign_step = "uploadAdjuntGDoc"
            lista_adjunts = [self.context[key] for key in self.context if self.context[key].portal_type == 'genweb.organs.annex']
            self.context.info_firma['adjunts'].update(
                self.uploadFilesGdoc(content_exp['idElementCreat'], lista_adjunts, save_title=True, save_size=True)
            )

            logger.info('6. Puja dels àudios al gdoc')
            sign_step = "uploadAudioGDoc"
            lista_audios = [self.context[key] for key in self.context if self.context[key].portal_type == 'genweb.organs.audio']
            self.context.info_firma['audios'].update(
                self.uploadFilesGdoc(content_exp['idElementCreat'], lista_audios, save_title=True)
            )

            logger.info('7. Puja dels fitxers de la sessió al gdoc')
            sign_step = "uploadSessionFiles"
            lista_fitxers = self.getFilesSessio(portal_type='genweb.organs.file')
            self.context.info_firma['sessio']['fitxers'].update(
                self.uploadFilesSessioGdoc(content_exp['idElementCreat'], lista_fitxers)
            )

            # Creem el fitxer .url apuntant a la URL de la sessió
            logger.info('8. Creació del fitxer .url')
            session = utils.get_session(self.context)
            furl = open("/tmp/" + session.id + ".url", "w")
            furl.write("[InternetShortcut]\n")
            furl.write("URL=" + session.absolute_url())
            furl.close()

            furl = open("/tmp/" + session.id + ".url", "r")
            files = {'fitxer': (session.id + '.url', furl.read(), 'application/octet-stream')}

            # Pujem el fitxer .url a la sèrie documental creada al gdoc
            sign_step = "uploadURLFile"
            logger.info('8.1 Puja del fitxer .url al gdoc')

            self.context.info_firma['url'] = uploadFileGdoc(content_exp['idElementCreat'], files)
            self.context.reindexObject()

            sign_step = 'uploadActaPortafirmes'
            logger.info('9. Petició de la firma al portafirmes')
            documentAnnexos = (
                [{"codi": adjunt['uuid']} for adjunt in self.context.info_firma['adjunts'].values()] +
                [{"codi": audio['uuid']} for audio in self.context.info_firma['audios'].values()] +
                [{"codi": fitxer['uuid']} for fitxer in self.context.info_firma['sessio']['fitxers'].values()] +
                [{"codi": self.context.info_firma['url']['uuid']}]
            )
            content_sign = client.uploadActaPortafirmes(
                self.context.title,
                self.context.info_firma['acta']['uuid'],
                documentAnnexos,
                signants,
            )
            logger.info('9.1. S\'ha enviat correctament la petició de la firma al portafirmes')

            self.context._Add_portal_content_Permission = ('Manager', 'Site Administrator', 'WebMaster')
            self.context._Modify_portal_content_Permission = ('Manager', 'Site Administrator', 'WebMaster')
            self.context._Delete_objects_Permission = ('Manager', 'Site Administrator', 'WebMaster')

            self.context.acta = None
            for audio_id in self.context:
                api.content.delete(self.context[audio_id])

            self.context.info_firma['enviatASignar'] = True

            self.context.id_firma = content_sign['idPeticio']
            self.context.estat_firma = "PENDENT"
            self.context.reindexObject()

            self.context.plone_utils.addPortalMessage(_(u'S\'ha enviat a firmar correctament'), 'success')
            transaction.commit()
            self.removeActaPDF()

        except ClientFirmaException as e:
            if e.timeout:
                self.context.plone_utils.addPortalMessage(_(u'S\'ha sobrepasat el temps d\'espera per executar la petició: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                self.removeActaPDF()
                return self.request.response.redirect(self.context.absolute_url())

            choose_msg_func = error_to_msg_map[sign_step].get('choose_portal_msg', None)
            portal_msg = 'portal_msg' if not choose_msg_func else choose_msg_func(e.response)
            # if sign_step == 'createSerieDocumental' and e.response['codi'] and e.response['codi'] == 528:
            #     portal_msg == 'portal_msg_no_existeix'
            # if sign_step == 'uploadActaPortafirmes' and 'tamany' in json.dumps(e.response):
            #     portal_msg == 'portal_msg_supera_tamany'

            logger.info(error_to_msg_map[sign_step]['console_log'] + ' Exception: %s', str(e))
            self.context.plone_utils.addPortalMessage(error_to_msg_map[sign_step][portal_msg], 'error')
            self.removeActaPDF()
            return self.request.response.redirect(self.context.absolute_url())

        utils.addEntryLog(self.context.__parent__, None, _(u'Acta send to sign'), self.context.absolute_url())
        return self.request.response.redirect(self.context.absolute_url())

    def __old_call__(self):
        if not isinstance(self.context.info_firma, dict):
            self.context.info_firma = ast.literal_eval(self.context.info_firma)

        if self.context.info_firma and 'enviatASignar' in self.context.info_firma and self.context.info_firma['enviatASignar']:
            return self.request.response.redirect(self.context.absolute_url())

        organ = utils.get_organ(self.context)
        signants = self.getSignants(organ)
        if not signants:
            self.context.plone_utils.addPortalMessage(_(u'No hi ha secretaris per firmar l\'acta.'), 'error')
            return self.request.response.redirect(self.context.absolute_url())

        if organ.visiblegdoc:
            fd_settings = utilsFD.get_settings_firma_documental()

            try:
                if self.context.info_firma and 'unitatDocumental' in self.context.info_firma and self.context.info_firma['unitatDocumental']:
                    logger.info('0. Eliminació serie documental en gdoc per tornar-la a crear')
                    result_del = requests.delete(fd_settings.gdoc_url + '/api/udch/' + self.context.info_firma['unitatDocumental'] + '/esborrar?&hash=' + fd_settings.gdoc_hash, timeout=TIMEOUT)

                    if result_del.status_code == 200:
                        logger.info('0.1. S\'ha eliminat correctament la serie documental en gdoc')
                    else:
                        logger.info('0.ERROR Eliminació serie documental en gdoc per tornar-la a crear')
                        logger.info(result_del.content)
                        self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pogut eliminar els contiguts de GDoc per tornar-los a crear.'), 'error')
                        return self.request.response.redirect(self.context.absolute_url())

                # Petició per obtenir un codi d'expedient
                logger.info('1. Iniciant firma de l\'acta - ' + self.context.title)
                logger.info('2. Demamant codi del expedient al servei generadorcodiexpedient')
                result_codi = requests.get(fd_settings.codiexpedient_url + '/api/codi?serie=' + organ.serie, headers={'X-Api-Key': fd_settings.codiexpedient_apikey}, timeout=TIMEOUT)

                if result_codi.status_code == 200:
                    logger.info('2.1. S\'ha obtingut correctament el codi del expedient')
                    content_codi = json.loads(result_codi.content)

                    now = datetime.datetime.now()
                    codi_expedient = now.strftime("%Y") + '-' + content_codi['codi']

                    data_exp = {"expedient": codi_expedient,
                                "titolPropi": codi_expedient + ' - ' + self.context.title}

                    # Petició que crea un sèrie documental / expedient en gdoc
                    logger.info('3. Creació de la serie documental en gdoc')

                    result_exp = requests.post(fd_settings.gdoc_url + '/api/serie/' + organ.serie + '/udch?uid=' + fd_settings.gdoc_user + '&hash=' + fd_settings.gdoc_hash, json=data_exp, timeout=TIMEOUT)
                    content_exp = json.loads(result_exp.content)

                    if result_exp.status_code == 200:
                        if 'idElementCreat' in content_exp:

                            logger.info('3.1. S\'ha creat correctament la serie documental')
                            if not isinstance(self.context.info_firma, dict):
                                self.context.info_firma = ast.literal_eval(self.context.info_firma)

                            self.context.info_firma.update({'unitatDocumental': str(content_exp['idElementCreat']),
                                                            'acta': {},
                                                            'adjunts': {},
                                                            'audios': {},
                                                            'url': {},
                                                            'enviatASignar': False})
                            self.context.reindexObject()

                            data_acta = {"tipusDocumental": "452",
                                         "idioma": "CA",
                                         "nomAplicacioCreacio": "Govern UPC",
                                         "autors": "[{'id': '1291399'}]",
                                         "agentsAmbCodiEsquemaIdentificacio": False,
                                         "validesaAdministrativa": True}

                            actaPDF = self.generateActaPDF()
                            files = {'fitxer': (self.context.id + '.pdf', actaPDF.read(), 'application/pdf')}

                            # Pujem l'acta a la sèrie documental creada al gdoc
                            logger.info('4. Puja de l\'acta al gdoc')
                            result_acta = requests.post(fd_settings.gdoc_url + '/api/pare/' + str(content_exp['idElementCreat']) + '/doce?uid=' + fd_settings.gdoc_user + '&hash=' + fd_settings.gdoc_hash, data=data_acta, files=files)

                            content_acta = json.loads(result_acta.content)
                            if result_acta.status_code == 200:
                                logger.info('4.1. S\'ha creat correctament l\'acta')

                                # Obtenim el uuid de la acta pujada, necessària per a la petició al portafirmes
                                logger.info('4.2. Petició per demanar el uuid de l\'acta')
                                result_info_acta = requests.get(fd_settings.gdoc_url + '/api/doce/' + str(content_acta['idElementCreat']) + '/consulta?hash=' + fd_settings.gdoc_hash, timeout=TIMEOUT)

                                content_info_acta = json.loads(result_info_acta.content)
                                if result_info_acta.status_code == 200:
                                    logger.info('4.3. S\'ha obtingut correctament el uuid de l\'acta')
                                    self.context.info_firma['acta'] = {'id': str(content_acta['idElementCreat']),
                                                                       'uuid': str(content_info_acta['documentElectronic']['uuid']),
                                                                       'filename': self.context.id + '.pdf',
                                                                       'contentType': 'application/pdf',
                                                                       'sizeKB': os.path.getsize('/tmp/' + self.context.id + '.pdf') / 1024}
                                    self.context.reindexObject()

                                else:
                                    logger.info('4.2.ERROR. Petició per demanar el uuid de l\'acta')
                                    logger.info(result_info_acta.content)
                                    self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pugut obtenir l\'informació de l\'acta: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                                    self.removeActaPDF()
                                    return self.request.response.redirect(self.context.absolute_url())

                            else:
                                logger.info('4.ERROR. Puja de l\'acta al gdoc')
                                logger.info(result_acta.content)
                                self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pogut pujar l\'acta: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                                self.removeActaPDF()
                                return self.request.response.redirect(self.context.absolute_url())

                            pos = 0

                            # Mirem si hi ha algun fitxer adjunt
                            for adjunt_id in self.context:
                                if self.context[adjunt_id].portal_type == 'genweb.organs.annex':
                                    annex = self.context[adjunt_id]
                                    data_file = {"tipusDocumental": "906340",
                                                 "idioma": "CA",
                                                 "nomAplicacioCreacio": "Govern UPC",
                                                 "autors": "[{'id': '1291399'}]",
                                                 "agentsAmbCodiEsquemaIdentificacio": False,
                                                 "validesaAdministrativa": True}

                                    files = {'fitxer': (annex.file.filename, annex.file.open().read(), annex.file.contentType)}

                                    # Pujem el fitxer adjunt a la sèrie documental creada al gdoc
                                    logger.info('5. Puja del fitxer adjunt al gdoc')
                                    result_file = requests.post(fd_settings.gdoc_url + '/api/pare/' + str(content_exp['idElementCreat']) + '/doce?uid=' + fd_settings.gdoc_user + '&hash=' + fd_settings.gdoc_hash, data=data_file, files=files)

                                    content_file = json.loads(result_file.content)
                                    if result_file.status_code == 200:
                                        logger.info('5.1. S\'ha creat correctament el fitxer adjunt')

                                        # Obtenim el uuid del fitxer adjunt pujat, necessària per a la petició al portafirmes
                                        logger.info('5.2. Petició per demanar el uuid del fitxer adjunt')
                                        result_info_file = requests.get(fd_settings.gdoc_url + '/api/doce/' + str(content_file['idElementCreat']) + '/consulta?hash=' + fd_settings.gdoc_hash, timeout=TIMEOUT)

                                        content_info_file = json.loads(result_info_file.content)
                                        if result_info_file.status_code == 200:
                                            logger.info('5.3. S\'ha obtingut correctament el uuid del fitxer adjunt')
                                            self.context.info_firma['adjunts'].update({str(pos): {
                                                'id': str(content_file['idElementCreat']),
                                                'uuid': str(content_info_file['documentElectronic']['uuid']),
                                                'title': annex.title,
                                                'filename': annex.file.filename,
                                                'contentType': annex.file.contentType,
                                                'sizeKB': annex.file.getSize() / 1024}})

                                            pos += 1
                                            self.context.reindexObject()

                                        else:
                                            logger.info('5.2.ERROR. Petició per demanar el uuid del fitxer adjunt')
                                            logger.info(result_info_file.content)
                                            self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pugut obtenir l\'informació del fitxer adjunt: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                                            self.removeActaPDF()
                                            return self.request.response.redirect(self.context.absolute_url())

                                    else:
                                        logger.info('5.ERROR. Puja del fitxer adjunt al gdoc - ' + annex.file.filename)
                                        logger.info(result_file.content)
                                        self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pogut pujar el fitxer adjunt: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                                        self.removeActaPDF()
                                        return self.request.response.redirect(self.context.absolute_url())

                            pos = 0

                            # Mirem si hi ha algun àudio pujat
                            for audio_id in self.context:
                                if self.context[audio_id].portal_type == 'genweb.organs.audio':
                                    audio = self.context[audio_id]
                                    data_audio = {"tipusDocumental": "906340",
                                                  "idioma": "CA",
                                                  "nomAplicacioCreacio": "Govern UPC",
                                                  "autors": "[{'id': '1291399'}]",
                                                  "agentsAmbCodiEsquemaIdentificacio": False,
                                                  "validesaAdministrativa": True}

                                    files = {'fitxer': (audio.file.filename, audio.file.open(), audio.file.contentType)}

                                    # Pujem l'àudio a la sèrie documental creada al gdoc
                                    logger.info('6. Puja del àudio al gdoc - ' + audio.file.filename)
                                    result_audio = requests.post(fd_settings.gdoc_url + '/api/pare/' + str(content_exp['idElementCreat']) + '/doce?uid=' + fd_settings.gdoc_user + '&hash=' + fd_settings.gdoc_hash, data=data_audio, files=files)

                                    content_audio = json.loads(result_audio.content)
                                    if result_audio.status_code == 200:
                                        logger.info('6.1. S\'ha creat correctament el àudio')

                                        # Obtenim el uuid de l'àudio pujat, necessària per a la petició al portafirmes
                                        logger.info('6.2. Petició per demanar el uuid del àudio')
                                        result_info_audio = requests.get(fd_settings.gdoc_url + '/api/doce/' + str(content_audio['idElementCreat']) + '/consulta?hash=' + fd_settings.gdoc_hash, timeout=TIMEOUT)

                                        content_info_audio = json.loads(result_info_audio.content)
                                        if result_info_audio.status_code == 200:
                                            logger.info('6.3. S\'ha obtingut correctament el uuid del àudio')
                                            self.context.info_firma['audios'].update({str(pos): {
                                                'id': str(content_audio['idElementCreat']),
                                                'uuid': str(content_info_audio['documentElectronic']['uuid']),
                                                'title': audio.title,
                                                'filename': audio.file.filename,
                                                'contentType': audio.file.contentType}})

                                            pos += 1
                                            self.context.reindexObject()

                                        else:
                                            logger.info('6.2.ERROR. Petició per demanar el uuid del àudio')
                                            logger.info(result_info_audio.content)
                                            self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pugut obtenir l\'informació del àudio: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                                            self.removeActaPDF()
                                            return self.request.response.redirect(self.context.absolute_url())

                                    else:
                                        logger.info('6.ERROR. Puja del àudio al gdoc - ' + audio.file.filename)
                                        logger.info(result_audio.content)
                                        self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pogut pujar el àudio: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                                        self.removeActaPDF()
                                        return self.request.response.redirect(self.context.absolute_url())

                            # Creem el fitxer .url apuntant a la URL de la sessió
                            logger.info('7. Creació del fitxer .url')
                            session = utils.get_session(self.context)
                            furl = open("/tmp/" + session.id + ".url", "w")
                            furl.write("[InternetShortcut]\n")
                            furl.write("URL=" + session.absolute_url())
                            furl.close()

                            data_url = {"tipusDocumental": "906340",
                                        "idioma": "CA",
                                        "nomAplicacioCreacio": "Govern UPC",
                                        "autors": "[{'id': '1291399'}]",
                                        "agentsAmbCodiEsquemaIdentificacio": False,
                                        "validesaAdministrativa": True}

                            furl = open("/tmp/" + session.id + ".url", "r")
                            files = {'fitxer': (session.id + '.url', furl.read(), 'application/octet-stream')}

                            # Pujem el fitxer .url a la sèrie documental creada al gdoc
                            logger.info('7. Puja del fitxer .url al gdoc')
                            result_url = requests.post(fd_settings.gdoc_url + '/api/pare/' + str(content_exp['idElementCreat']) + '/doce?uid=' + fd_settings.gdoc_user + '&hash=' + fd_settings.gdoc_hash, data=data_url, files=files)

                            content_url = json.loads(result_url.content)
                            if result_url.status_code == 200:
                                logger.info('7.1. S\'ha creat correctament el fitxer .url')

                                # Obtenim el uuid del fitxer .url pujada, necessària per a la petició al portafirmes
                                logger.info('7.2. Petició per demanar el uuid del fitxer .url')
                                result_info_url = requests.get(fd_settings.gdoc_url + '/api/doce/' + str(content_url['idElementCreat']) + '/consulta?hash=' + fd_settings.gdoc_hash, timeout=TIMEOUT)

                                if result_info_url.status_code == 200:
                                    content_info_url = json.loads(result_info_url.content)
                                    logger.info('7.3. S\'ha obtingut correctament el uuid de la URL')
                                    self.context.info_firma['url'] = {'id': str(content_url['idElementCreat']),
                                                                      'uuid': str(content_info_url['documentElectronic']['uuid']),
                                                                      'filename': session.id + '.url',
                                                                      'contentType': 'application/octet-stream'}
                                    self.context.reindexObject()

                                else:
                                    logger.info('7.2.ERROR. Petició per demanar el uuid del fitxer .url')
                                    logger.info(result_info_url.content)
                                    self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pugut obtenir l\'informació de la URL: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                                    self.removeActaPDF()
                                    return self.request.response.redirect(self.context.absolute_url())

                            else:
                                logger.info('7.ERROR. Puja del fitxer .url al gdoc')
                                logger.info(content_url.content)
                                self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pogut pujar el fitxer .url: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                                self.removeActaPDF()
                                return self.request.response.redirect(self.context.absolute_url())

                            data_sign = {
                                "descripcioPeticio": "Signatura acta" + ' - ' + self.context.title,
                                "documents": [
                                    {
                                        "paginaSignaturaVisible": 1,
                                        "codi": self.context.info_firma['acta']['uuid']
                                    }
                                ],
                                "passosPeticio": [],
                                "promocionar": "S",
                                "codiCategoria": "CAT6",
                                "codiTipusSignatura": "ATTACHED_VISIBLE_MARGE",
                                "dataLimit": (now + datetime.timedelta(days=1)).strftime("%d-%m-%Y %H:%M:00"),
                                "emissor": "Govern UPC",
                                "informacio": "Signatura acta" + ' - ' + self.context.title,
                                "motiusRebuig": [
                                    {
                                        "codi": "Inacabada",
                                        "descripcio": "Petició inacabada"
                                    }
                                ],
                                "documentsAnnexos": [],
                                "callbackUrl": api.portal.get().absolute_url() + '/updateInfoPortafirmes'
                            }

                            for signant in signants:
                                data_sign["passosPeticio"].append({
                                    "nivellSignatura": "CDA",
                                    "signants": [{"commonName": signant}]
                                })

                            if self.context.info_firma['audios'] or self.context.info_firma['adjunts']:
                                for adjunt in self.context.info_firma['adjunts']:
                                    data_sign['documentsAnnexos'].append({"codi": self.context.info_firma['adjunts'][adjunt]['uuid']})

                                for audio in self.context.info_firma['audios']:
                                    data_sign['documentsAnnexos'].append({"codi": self.context.info_firma['audios'][audio]['uuid']})

                            data_sign['documentsAnnexos'].append({"codi": self.context.info_firma['url']['uuid']})

                            # Creem la petició al portafirmes de l'acta i els àudios annexos
                            logger.info('8. Petició de la firma al portafirmes')
                            result_sign = requests.post(fd_settings.portafirmes_url, json=data_sign, headers={'X-Api-Key': fd_settings.portafirmes_apikey})

                            if result_sign.status_code == 201:
                                logger.info('8.1. La petició de la firma s\'ha processat correctament')
                                self.context._Add_portal_content_Permission = ('Manager', 'Site Administrator', 'WebMaster')
                                self.context._Modify_portal_content_Permission = ('Manager', 'Site Administrator', 'WebMaster')
                                self.context._Delete_objects_Permission = ('Manager', 'Site Administrator', 'WebMaster')

                                self.context.acta = None
                                for audio_id in self.context:
                                    api.content.delete(self.context[audio_id])

                                self.context.info_firma['enviatASignar'] = True

                                content_sign = json.loads(result_sign.content)
                                self.context.id_firma = content_sign['idPeticio']
                                self.context.estat_firma = "PENDENT"
                                self.context.reindexObject()

                                self.context.plone_utils.addPortalMessage(_(u'S\'ha enviat a firmar correctament'), 'success')
                                transaction.commit()
                                self.removeActaPDF()
                            else:
                                logger.info('8.ERROR. Petició de la firma al portafirmes')
                                logger.info(result_sign.content)
                                if 'tamany' in result_sign.content:
                                    self.context.plone_utils.addPortalMessage(_(u'No s\'ha pogut enviar a firmar: S\'ha superat el tamany màxim'), 'error')
                                else:
                                    self.context.plone_utils.addPortalMessage(_(u'No s\'ha pogut enviar a firmar: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')

                            self.removeActaPDF()
                            utils.addEntryLog(self.context.__parent__, None, _(u'Acta send to sign'), self.context.absolute_url())
                            return self.request.response.redirect(self.context.absolute_url())
                    else:
                        logger.info('3.ERROR. Creació de la serie documental en gdoc')
                        logger.info(result_exp.content)
                        if 'codi' in content_exp:
                            if content_exp['codi'] == 503:
                                self.context.plone_utils.addPortalMessage(_(u'GDoc: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                            elif content_exp['codi'] == 528:
                                self.context.plone_utils.addPortalMessage(_(u'GDoc: La sèrie documental configurada no existeix'), 'error')

                            self.removeActaPDF()
                            return self.request.response.redirect(self.context.absolute_url())

                        self.context.plone_utils.addPortalMessage(_(u'GDoc: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                        self.removeActaPDF()
                        return self.request.response.redirect(self.context.absolute_url())
                else:
                    logger.info('2.ERROR. Demamant codi del expedient al servei generadorcodiexpedient')
                    logger.info(result_codi.content)
                    self.context.plone_utils.addPortalMessage(_(u'No s\'ha pogut generar el codi de expedient: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                    self.removeActaPDF()
                    return self.request.response.redirect(self.context.absolute_url())
            except:
                self.context.plone_utils.addPortalMessage(_(u'S\'ha sobrepasat el temps d\'espera per executar la petició: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                self.removeActaPDF()
                return self.request.response.redirect(self.context.absolute_url())


class ViewActa(BrowserView):

    def __call__(self):
        if not isinstance(self.context.info_firma, dict):
            self.context.info_firma = ast.literal_eval(self.context.info_firma)

        content = self.context.info_firma['acta']
        return viewCopiaAutentica(self, content['uuid'], content['contentType'], content['filename'])


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

            content = self.context.info_firma['adjunts'][self.request['pos']]
            return viewGDoc(self, content['uuid'], content['contentType'], content['filename'])


class DownloadFile(BrowserView):

    def __call__(self):
        if 'pos' in self.request:
            if not isinstance(self.context.info_firma, dict):
                self.context.info_firma = ast.literal_eval(self.context.info_firma)

            content = self.context.info_firma['adjunts'][self.request['pos']]
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
