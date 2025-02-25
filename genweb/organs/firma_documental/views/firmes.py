# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from Products.Five.browser import BrowserView

from plone import api

# from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject

from genweb.organs import _
from genweb.organs import utils
# from genweb.organs.firma_documental.views.general import downloadCopiaAutentica
# from genweb.organs.firma_documental.views.general import downloadGDoc
from genweb.organs.firma_documental.views.general import downloadCopiaAutentica, viewCopiaAutentica
# from genweb.organs.firma_documental.views.general import viewGDoc
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


class FirmesMixin(object):
    error_message_map = {}

    def printError(self, sign_step, exc):
        if not isinstance(exc, ClientFirmaException):
            logger.error('ERROR. ' + sign_step + ' Exception: %s', str(exc))
            logger.error(traceback.format_exc())
            self.context.plone_utils.addPortalMessage(_(
                u'Error desconegut: Contacta amb algun administrador de la web perquè revisi la configuració'
            ), 'error')
            return "Error"

        if exc.timeout:
            self.context.plone_utils.addPortalMessage(_(
                u'S\'ha sobrepasat el temps d\'espera per executar la petició: ' +
                u'Contacta amb algun administrador de la web perquè revisi la configuració'
            ), 'error')
            return "gDOC Timeout"

        choose_msg_func = self.error_to_msg_map[sign_step].get('choose_portal_msg', None)
        portal_msg = choose_msg_func(exc.response) if choose_msg_func else 'portal_msg'

        logger.error(self.error_to_msg_map[sign_step]['console_log'] + ' Exception: %s', str(exc))
        self.context.plone_utils.addPortalMessage(self.error_to_msg_map[sign_step][portal_msg], 'error')

        return "Error"


class UploadFiles(BrowserView, FirmesMixin):
    error_to_msg_map = {
        'deleteSerieDocumental': {
            'console_log': '0.ERROR. Eliminació serie documental en gDOC per tornar-la a crear.',
            'portal_msg': _(u'gDOC: No s\'ha pogut eliminar els contiguts de gDOC per tornar-los a crear.')
        },
        'getCodiExpedient': {
            'console_log': '2.ERROR. Petició per demanar el codi del expedient.',
            'portal_msg': _(
                u'gDOC: No s\'ha pogut obtenir el codi del expedient: ' +
                u'Contacta amb algun administrador de la web perquè revisi la configuració.'
            )
        },
        'createSerieDocumental': {
            'console_log': '3.ERROR. Creació de la serie documental en gDOC.',
            'portal_msg': _(u'gDOC: No s\'ha pogut crear la serie documental: Contacta amb algun administrador de la web perquè revisi la configuració.'),
            'portal_msg_noExisteix': _(u'gDOC: No s\'ha pogut crear la serie documental: La serie documental no existeix.'),
            'choose_portal_msg': lambda resp: 'portal_msg_noExisteix' if resp['codi'] and resp['codi'] == 528 else 'portal_msg'
        },
        'uploadSessionFiles': {
            'console_log': '7.ERROR. Puja dels fitxers de la sessió al gDOC.',
            'portal_msg': _(u'gDOC: No s\'ha pogut pujar els fitxers de la sessió: Contacta amb algun administrador de la web perquè revisi la configuració.')
        },
    }

    def uploadFileGdoc(self, author, file, visibility):

        if not hasattr(file, 'info_firma'):
            file.info_firma = {}

        elif not isinstance(file.info_firma, dict):
            file.info_firma = ast.literal_eval(file.info_firma)

        if file.info_firma.get(visibility, None) and file.info_firma[visibility].get('uploaded', False):
            return True  # Already uploaded

        if visibility not in ['public', 'private']:
            is_public = True
        else:
            is_public = visibility == 'public'

        parent = file.aq_parent
        filename_append = ''
        if parent.portal_type == 'genweb.organs.acord':
            filename_append = 'Acord [%s] ' % (parent.agreement or 'Acord sense numerar')

        if is_public:
            file_content = file.visiblefile
            filename = 'Public - ' + filename_append + file.Title()
        else:
            file_content = file.hiddenfile
            filename = 'Restringit - ' + filename_append + file.Title()

        try:
            info_file = uploadFileGdoc(author, self.context.unitatDocumental, file_content, filename.decode('utf-8'))
            info_file['uploaded'] = True
            info_file['error'] = None

        except ClientFirmaException as e:
            logger.error('ERROR. Puja del fitxer al gDOC. Exception: %s', str(e))
            info_file = {
                'uploaded': False,
                'error': "No s'ha pogut pujar el fitxer al gDOC. Torneu a provar-ho més tard."
            }
            return False

        except Exception as e:
            logger.error('ERROR. Puja del fitxer al gDOC. Exception: %s', str(e))
            logger.error(traceback.format_exc())
            info_file = {
                'uploaded': False,
                'error': "Hi ha hagut un error intern a l'hora de pujar el fitxer. Contacta amb algún administrador de la web perquè revisi la configuració."
            }
            return False

        finally:
            file.info_firma[visibility] = info_file
            file.info_firma = str(file.info_firma)
            file.reindexObject()

        return True

    def __call__(self):
        organ = utils.get_organ(self.context)

        if not organ.visiblegdoc:
            return "gDOC not set up"

        sign_step = ""
        files = self.request.form.get('check', None)

        if not files:
            self.context.plone_utils.addPortalMessage(_(u'No s\'ha seleccionat cap fitxer per signar'), 'error')
            return "No files selected"

        if not isinstance(files, list):
            files = [files]

        client = ClientFirma()

        try:
            if not self.context.unitatDocumental:
                sign_step = "getCodiExpedient"
                logger.info('0.1. Demanant codi del expedient al servei generadorcodiexpedient')
                content_codi = client.getCodiExpedient(organ.serie)
                logger.info('0.1.1. S\'ha obtingut correctament el codi del expedient')

                now = datetime.datetime.now()
                codi_expedient = now.strftime("%Y") + '-' + content_codi['codi']

                sign_step = "createSerieDocumental"
                logger.info('0.2. Creació de la serie documental en gDOC')
                content_exp = client.createSerieDocumental(
                    serie=organ.serie,
                    expedient=codi_expedient,
                    titolPropi=codi_expedient + ' - ' + self.context.title
                )
                self.context.unitatDocumental = str(content_exp['idElementCreat'])
                logger.info('0.2.1 S\'ha creat correctament la serie documental')

            logger.info('1. Puja dels fitxers de la sessió al gDOC')
            success = True

            for file_id in files:
                visibility = 'private' if file_id.startswith('private') else 'public'
                file_id = file_id.replace(visibility + '-', '', 1)
                file_obj = uuidToObject(file_id)
                if file_obj:
                    success = self.uploadFileGdoc(organ.author, file_obj, visibility) and success
                    if not isinstance(file_obj.info_firma, dict):
                        file_obj.info_firma = ast.literal_eval(file_obj.info_firma)
                    res = client.timbrarDocumentGdoc(file_obj.info_firma[visibility]['id'])
                    file_obj.info_firma[visibility]['id'] = res['idDocument']
                    file_obj.reindexObject()
                    logger.info("1.1 Document timbrat correctament: [%s] %s " % (file_obj.info_firma[visibility]['id'], file_obj.info_firma[visibility]['filename']))
                else:
                    logger.error('ERROR. No s\'ha pogut obtenir el fitxer amb id %s', file_id)

        except Exception as e:
            return self.printError(sign_step, e)

        finally:
            transaction.commit()

        if not success:
            self.context.plone_utils.addPortalMessage(_(u"Alguns dels fitxers no s'han pujat corectament. Revisa els estats dels fitxers per més informació."), 'error')
            return "Error"

        self.context.plone_utils.addPortalMessage(_(u'S\'han pujat els fitxers correctament al gDOC'), 'success')
        return "Success"


class SignActa(BrowserView, FirmesMixin):
    error_to_msg_map = {
        'deleteSerieDocumental': {
            'console_log': '0.ERROR. Eliminació serie documental en gDOC per tornar-la a crear.',
            'portal_msg': _(u'gDOC: No s\'ha pogut eliminar els contiguts de gDOC per tornar-los a crear.')
        },
        'getCodiExpedidElementCreatient': {
            'console_log': '2.ERROR. Petició per demanar el codi del expedient.',
            'portal_msg': _(u'gDOC: No s\'ha pogut obtenir el codi del expedient: Contacta amb algun administrador de la web perquè revisi la configuració.')
        },
        'createSerieDocumental': {
            'console_log': '3.ERROR. Creació de la serie documental en gDOC.',
            'portal_msg': _(u'gDOC: No s\'ha pogut crear la serie documental: Contacta amb algun administrador de la web perquè revisi la configuració.'),
            'portal_msg_noExisteix': _(u'gDOC: No s\'ha pogut crear la serie documental: La serie documental no existeix.'),
            'choose_portal_msg': lambda resp: 'portal_msg_noExisteix' if resp['codi'] and resp['codi'] == 528 else 'portal_msg'
        },
        'uploadActaGDoc': {
            'console_log': '4.ERROR. Puja de l\'acta al gDOC.',
            'portal_msg': _(u'gDOC: No s\'ha pogut pujar l\'acta: Contacta amb algun administrador de la web perquè revisi la configuració.')
        },
        'uploadAdjuntGDoc': {
            'console_log': '5.ERROR. Puja del fitxer adjunt al gDOC.',
            'portal_msg': _(u'gDOC: No s\'ha pogut pujar el fitxer adjunt: Contacta amb algun administrador de la web perquè revisi la configuració.')
        },
        'uploadAudioGDoc': {
            'console_log': '6.ERROR. Puja del àudio al gDOC.',
            'portal_msg': _(u'gDOC: No s\'ha pogut pujar el àudio: Contacta amb algun administrador de la web perquè revisi la configuració.')
        },
        'uploadSessionFiles': {
            'console_log': '7.ERROR. Puja dels fitxers de la sessió al gDOC.',
            'portal_msg': _(u'gDOC: No s\'ha pogut pujar els fitxers de la sessió: Contacta amb algun administrador de la web perquè revisi la configuració.')
        },
        'uploadURLFile': {
            'console_log': '8.ERROR. Puja del fitxer .url al gDOC.',
            'portal_msg': _(u'gDOC: No s\'ha pogut pujar el fitxer .url: Contacta amb algun administrador de la web perquè revisi la configuració.')
        },
        'uploadActaPortafirmes': {
            'console_log': '9.ERROR. Petició de la firma al portafirmes.',
            'portal_msg': _(u'Portafirmes: No s\'ha pogut enviar la petició de la firma: Contacta amb algun administrador de la web perquè revisi la configuració.'),
            'portal_msg_supera_tamany': _(u'Portafirmes: No s\'ha pogut enviar la petició de la firma: El tamany dels fitxers supera el màxim permès.'),
            'choose_portal_msg': lambda resp: 'portal_msg_supera_tamany' if 'tamany' in json.dumps(resp) else 'portal_msg'
        }
    }

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

    def fileUploaded(self, file):
        if not getattr(file, 'info_firma', None):
            file.info_firma = {}
            return False
        if not isinstance(file.info_firma, dict):
            file.info_firma = ast.literal_eval(file.info_firma)

        if file.visiblefile and not file.info_firma.get('public', {}).get('uploaded', False):
            return False
        if file.hiddenfile and not file.info_firma.get('private', {}).get('uploaded', False):
            return False

        return True

    def uploadFilesGdoc(self, author, id_exp, files, save_title=False, save_size=False):
        uploaded_files = {}
        for idx, file_content in enumerate(files):
            info_adjunt = uploadFileGdoc(author, id_exp, file_content.file)
            if save_title:
                info_adjunt['title'] = file_content.title
            if save_size:
                info_adjunt['sizeKB'] = file_content.file.getSize() / 1024
            uploaded_files[str(idx)] = info_adjunt
            self.context.reindexObject()
        return uploaded_files

    def __call__(self):
        if not isinstance(self.context.info_firma, dict):
            self.context.info_firma = ast.literal_eval(self.context.info_firma)

        if self.context.info_firma and self.context.info_firma.get('enviatASignar', False):
            return "Already sent to sign"

        organ = utils.get_organ(self.context)
        sessio = utils.get_session(self.context)
        signants = self.getSignants(organ)

        if not signants:
            self.context.plone_utils.addPortalMessage(_(u'No hi ha secretaris per firmar l\'acta.'), 'error')
            return "No signants"

        if not organ.visiblegdoc:
            return "gDOC not set up"

        sign_step = ""

        client = ClientFirma()

        try:
            # sign_step = "deleteSerieDocumental"
            # if self.context.info_firma and 'unitatDocumental' in self.context.info_firma and self.context.info_firma['unitatDocumental']:
            #     logger.info('0. Eliminació serie documental en gDOC per tornar-la a crear')
            #     client.deleteSerieDocumental(self.context.info_firma['unitatDocumental'])
            #     logger.info('0.1. S\'ha eliminat correctament la serie documental en gDOC')

            # logger.info('1. Iniciant firma de l\'acta - ' + self.context.title)

            # sign_step = "getCodiExpedient"
            # logger.info('2. Demanant codi del expedient al servei generadorcodiexpedient')
            # content_codi = client.getCodiExpedient(organ.serie)
            # logger.info('2.1. S\'ha obtingut correctament el codi del expedient')

            # now = datetime.datetime.now()
            # codi_expedient = now.strftime("%Y") + '-' + content_codi['codi']

            # sign_step = "createSerieDocumental"
            # logger.info('3. Creació de la serie documental en gDOC')
            # content_exp = client.createSerieDocumental(
            #     serie=organ.serie,
            #     expedient=codi_expedient,
            #     titolPropi=codi_expedient + ' - ' + self.context.title
            # )

            # logger.info('3.1. S\'ha creat correctament la serie documental')

            files_sessio = utils.getFilesSessio(sessio)
            if any(not self.fileUploaded(file) for file in files_sessio):
                self.context.plone_utils.addPortalMessage(_(u'Hi ha fitxers de la sessió que no s\'han pujat al Gestor Documental'), 'error')
                return "Error"

            if not isinstance(self.context.info_firma, dict):
                self.context.info_firma = ast.literal_eval(self.context.info_firma)
            self.context.info_firma.update({
                'unitatDocumental': str(sessio.unitatDocumental),
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
            logger.info('4. Puja de l\'acta al gDOC')
            self.context.info_firma['acta'] = uploadFileGdoc(
                organ.author,
                sessio.unitatDocumental,
                {'fitxer': [self.context.id + '.pdf', actaPDF.read(), 'application/pdf']},
                is_acta=True
            )
            self.context.info_firma['acta'].update({
                'sizeKB': os.path.getsize('/tmp/' + self.context.id + '.pdf') / 1024
            })

            logger.info('5. Puja dels fitxers adjunts al gDOC')
            sign_step = "uploadAdjuntGDoc"
            lista_adjunts = [
                self.context[key]
                for key in self.context if self.context[key].portal_type == 'genweb.organs.annex'
            ]
            self.context.info_firma['adjunts'].update(
                self.uploadFilesGdoc(organ.author, sessio.unitatDocumental, lista_adjunts, save_title=True, save_size=True)
            )

            logger.info('6. Puja dels àudios al gDOC')
            sign_step = "uploadAudioGDoc"
            lista_audios = [
                self.context[key]
                for key in self.context if self.context[key].portal_type == 'genweb.organs.audio'
            ]
            self.context.info_firma['audios'].update(
                self.uploadFilesGdoc(organ.author, sessio.unitatDocumental, lista_audios, save_title=True)
            )

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
            logger.info('8.1 Puja del fitxer .url al gDOC')

            self.context.info_firma['url'] = uploadFileGdoc(organ.author, sessio.unitatDocumental, files)
            self.context.reindexObject()

            sign_step = 'uploadActaPortafirmes'
            logger.info('9. Petició de la firma al portafirmes')

            punt_files_uuid = []
            for file in files_sessio:
                if not isinstance(file.info_firma, dict):
                    file.info_firma = ast.literal_eval(file.info_firma)
                pubuuid = file.info_firma.get('public', {}).get('uuid', None)
                if pubuuid:
                    punt_files_uuid.append(pubuuid)

                privuuid = file.info_firma.get('private', {}).get('uuid', None)
                if privuuid:
                    punt_files_uuid.append(privuuid)

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

            self.context.id_firma = str(content_sign['idPeticio'])
            self.context.estat_firma = "PENDENT"
            self.context.reindexObject()

            self.context.plone_utils.addPortalMessage(_(u'S\'ha enviat a firmar correctament'), 'success')
            transaction.commit()
            self.removeActaPDF()

        except Exception as e:
            error = self.printError(sign_step, e)
            self.removeActaPDF()
            return error

        utils.addEntryLog(self.context.__parent__, None, _(u'Acta send to sign'), self.context.absolute_url())
        return "Success"


class ViewFile(BrowserView):
    _obtain_file_method_ = viewCopiaAutentica

    def __call__(self):
        if 'pos' in self.request or 'visibility' in self.request:
            if not isinstance(self.context.info_firma, dict):
                self.context.info_firma = ast.literal_eval(self.context.info_firma)
            if self.context.portal_type == 'genweb.organs.acta':
                if not self.canViewActa():
                    raise Unauthorized
                content = self.context.info_firma['adjunts'][self.request['pos']]
            else:
                visibility = self.request.get('visibility', 'public')
                if visibility != 'private':
                    visibility = 'public'

                if not self.canViewFile(visibility):
                    raise Unauthorized

                if visibility not in self.context.info_firma:
                    self.context.plone_utils.addPortalMessage(_(u'El fitxer no existeix'), 'error')
                    return None

                content = self.context.info_firma[visibility]

            return self._obtain_file_method_(content['uuid'], content['contentType'], content['filename'])

    def canViewActa(self):
        # Permissions to view acta

        if self.context.portal_type != 'genweb.organs.acta':
            raise Unauthorized # Only for actes

        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        roles_to_check = ['OG1-Secretari', 'OG2-Editor']
        if estatSessio != 'planificada':
            roles_to_check += ['OG3-Membre', 'OG5-Convidat']
            if organ_tipus == 'open_organ' and estatSessio == 'tancada':
                roles_to_check.append('OG4-Afectat')

        if not utils.checkhasRol(roles_to_check, roles):
            raise Unauthorized

        return True

    def canViewFile(self, visibility):
        organ_tipus = self.context.organType
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True
        roles_to_check = ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat']
        if organ_tipus == 'open_organ':
            roles_to_check.append('OG4-Afectat')
        elif not utils.checkhasRol(roles_to_check, roles):
            raise Unauthorized

        if visibility != 'public' and not utils.checkhasRol(roles_to_check, roles):
            raise Unauthorized

        return True


class DownloadFile(ViewFile):
    _obtain_file_method_ = downloadCopiaAutentica