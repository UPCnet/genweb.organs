# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from Products.Five.browser import BrowserView

from plone import api
from plone.uuid.interfaces import IUUID

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental.views.general import downloadCopiaAutentica
from genweb.organs.firma_documental.views.general import downloadGDoc
from genweb.organs.firma_documental.views.general import viewCopiaAutentica
from genweb.organs.firma_documental.views.general import viewGDoc
from genweb.organs.firma_documental.webservices import ClientFirma, ClientFirmaException, uploadFileGdoc

import ast
import datetime
import json
import logging
import os
import pdfkit
import transaction
import traceback

logger = logging.getLogger(__name__)


class SignActa(BrowserView):

    def getSignants(self, organ):
        signants = organ.signants
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
        except Exception:
            pass

    def generateDocumentPDF(self, document, filename, visibility='public'):
        options = {'cookie': [('__ac', self.request.cookies['__ac']),
                              ('I18N_LANGUAGE', self.request.cookies.get('I18N_LANGUAGE', 'ca'))]}
        _filename = filename.replace('/', ' ')
        pdfkit.from_url(document.absolute_url() + '/printDocument?visibility=' + visibility, '/tmp/' + _filename, options=options)
        return open('/tmp/' + _filename, 'rb')

    def removeDocumentPDF(self, filename):
        _filename = filename.replace('/', ' ')
        try:
            os.remove('/tmp/' + _filename)
        except Exception:
            pass

    def getPuntsWithFiles(self):
        portal_catalog = api.portal.get_tool('portal_catalog')
        session = utils.get_session(self.context)
        session_path = '/'.join(session.getPhysicalPath())
        punts = portal_catalog.searchResults(
            portal_type=['genweb.organs.acord', 'genweb.organs.punt'],
            path={'query': session_path, 'depth': 1},
            sort_on='getObjPositionInParent'
        )
        punts_with_files = []
        for punt in punts:
            files_punt = portal_catalog.searchResults(
                portal_type=['genweb.organs.file', 'genweb.organs.document'],
                path={'query': punt.getPath(), 'depth': 1},
                sort_on='getObjPositionInParent'
            )
            if files_punt:
                punts_with_files.append(punt.getObject())

            if punt.getObject().portal_type == 'genweb.organs.acord':
                continue

            subpunts = portal_catalog.searchResults(
                portal_type=['genweb.organs.acord', 'genweb.organs.subpunt'],
                path={'query': punt.getPath(), 'depth': 1},
                sort_on='getObjPositionInParent'
            )

            for subpunt in subpunts:
                files_subpunt = portal_catalog.searchResults(
                    portal_type=['genweb.organs.file', 'genweb.organs.document'],
                    path={'query': subpunt.getPath(), 'depth': 1},
                    sort_on='getObjPositionInParent'
                )
                if files_subpunt:
                    punts_with_files.append(subpunt.getObject())

        return punts_with_files

    def uploadFilesPuntsGdoc(self, id_exp, punts):
        portal_catalog = api.portal.get_tool('portal_catalog')
        uploaded_files_uuid = []
        for punt in punts:
            punt.info_firma = {
                'related_acta': '',
                'fitxers': {},
            }
            files = portal_catalog.searchResults(
                portal_type=['genweb.organs.file', 'genweb.organs.document'],
                path={'query': '/'.join(punt.getPhysicalPath()), 'depth': 1},
                sort_on='getObjPositionInParent'
            )
            filename_append = ''
            if punt.portal_type == 'genweb.organs.acord':
                filename_append = 'Acord [%s] ' % (punt.agreement or 'Acord sense numerar')
            idx = 0
            for file in files:
                file_content = file.getObject()
                if file.portal_type == 'genweb.organs.file':
                    file_info = self.uploadFileSessioGdoc(id_exp, file_content, filename_append)
                else:
                    file_info = self.uploadDocsSessioGdoc(id_exp, file_content, filename_append)

                if file_info['public']:
                    punt.info_firma['fitxers'][str(idx)] = file_info['public']
                    uploaded_files_uuid.append(file_info['public']['uuid'])
                    idx += 1
                if file_info['private']:
                    punt.info_firma['fitxers'][str(idx)] = file_info['private']
                    uploaded_files_uuid.append(file_info['private']['uuid'])
                    idx += 1
                punt.reindexObject()
            punt.info_firma['related_acta'] = IUUID(self.context, None)
        return uploaded_files_uuid

    def uploadFilesGdoc(self, id_exp, files, save_title=False, save_size=False):
        uploaded_files = {}
        for idx, file_content in enumerate(files):
            info_adjunt = uploadFileGdoc(id_exp, file_content.file)
            if save_title:
                info_adjunt['title'] = file_content.title
            if save_size:
                info_adjunt['sizeKB'] = file_content.file.getSize() / 1024
            uploaded_files[str(idx)] = info_adjunt
            self.context.reindexObject()
        return uploaded_files

    def uploadFileSessioGdoc(self, id_exp, file_content, filename_append):
        file_res = {
            'public': None,
            'private': None
        }
        for filetype in ['visiblefile', 'hiddenfile']:
            file = getattr(file_content, filetype) if hasattr(file_content, filetype) else None
            if not file:
                continue
            file = getattr(file_content, filetype)
            is_public = filetype == 'visiblefile'

            filename = ('Public - ' if is_public else 'LOPD - ') + filename_append + file_content.Title()

            info_file = uploadFileGdoc(id_exp, file, filename.decode('utf-8'))
            info_file.update({'title': filename, 'sizeKB': file.getSize() / 1024, 'public': is_public})
            file_res['public' if is_public else 'private'] = info_file

        return file_res

    def uploadDocsSessioGdoc(self, id_exp, document_content, filename_append):
        file_res = {
            'public': None,
            'private': None
        }

        for filetype in ['defaultContent', 'alternateContent']:
            document = getattr(document_content, filetype) if hasattr(document_content, filetype) else None
            if not document:
                continue
            is_public = filetype == 'defaultContent'
            filename = ('Public - ' if is_public else 'LOPD - ') + filename_append + document_content.Title()
            pdf_file = self.generateDocumentPDF(document_content, filename, 'public' if is_public else 'private')
            info_file = uploadFileGdoc(
                expedient=id_exp,
                file={"fitxer": [filename.decode('utf-8'), pdf_file.read(), 'application/pdf']},
            )
            info_file.update({'title': filename, 'public': is_public})
            file_res['public' if is_public else 'private'] = info_file
            pdf_file.close()
            self.removeDocumentPDF(filename)

        return file_res

    def __call__(self):
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
                {'fitxer': [self.context.id + '.pdf', actaPDF.read(), 'application/pdf']},
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
            sign_step = "getPuntsWithFiles"
            logger.info('7.1 Obtenir tots els punts i acords amb fitxers')
            lista_punts = self.getPuntsWithFiles()
            sign_step = "uploadSessionFiles"
            logger.info('7.2 Puja dels fitxers de la sessió al gdoc')
            punt_files_uuid = self.uploadFilesPuntsGdoc(content_exp['idElementCreat'], lista_punts)

            # Creem el fitxer .url apuntant a la URL de la sessió
            logger.info('8. Creació del fitxer .url')
            session = utils.get_session(self.context)
            furl = open("/tmp/" + session.id + ".url", "w")
            furl.write("[InternetShortcut]\n")
            furl.write("URL=" + session.absolute_url())
            furl.close()

            furl = open("/tmp/" + session.id + ".url", "r")
            files = {'fitxer': [session.id + '.url', furl.read(), 'application/octet-stream']}

            # Pujem el fitxer .url a la sèrie documental creada al gdoc
            sign_step = "uploadURLFile"
            logger.info('8.1 Puja del fitxer .url al gdoc')

            self.context.info_firma['url'] = uploadFileGdoc(content_exp['idElementCreat'], files)
            self.context.reindexObject()

            sign_step = 'uploadActaPortafirmes'
            logger.info('9. Petició de la firma al portafirmes')
            documentAnnexos = (
                [{"codi": adjunt['uuid']} for idx, adjunt in self.context.info_firma['adjunts'].items()] +
                [{"codi": audio['uuid']} for idx, audio in self.context.info_firma['audios'].items()] +
                [{"codi": self.context.info_firma['url']['uuid']}] +
                [{"codi": punt_file_uuid} for punt_file_uuid in punt_files_uuid]
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

            logger.error(error_to_msg_map[sign_step]['console_log'] + ' Exception: %s', str(e))
            self.context.plone_utils.addPortalMessage(error_to_msg_map[sign_step][portal_msg], 'error')
            self.removeActaPDF()
            return self.request.response.redirect(self.context.absolute_url())

        except Exception as e:
            logger.error('ERROR. ' + sign_step + ' Exception: %s', str(e))
            logger.error(traceback.format_exc())
            self.context.plone_utils.addPortalMessage(_(u'Error al signar l\'acta: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
            self.removeActaPDF()
            return self.request.response.redirect(self.context.absolute_url())

        utils.addEntryLog(self.context.__parent__, None, _(u'Acta send to sign'), self.context.absolute_url())
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
