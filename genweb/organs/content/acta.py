# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName

from five import grok
from collective import dexteritytextindexer
from plone import api
from plone.directives import form
from plone.directives import dexterity
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.supermodel.directives import fieldset
from plone.autoform import directives
from plone.event.interfaces import IEventAccessor
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.utils import get_contenttype
from zope import schema
from zope.schema import ValidationError

from genweb.organs import _
from genweb.organs import utils

import ast
import datetime
import json
import logging
import os
import pdfkit
import requests
import transaction

logger = logging.getLogger(__name__)
TIMEOUT = 15

grok.templatedir("templates")


class InvalidPDFFile(ValidationError):
    """Exception for invalid PDF file"""
    __doc__ = _(u"Invalid PDF file")


class IActa(form.Schema):
    """ ACTA """

    fieldset('acta',
             label=_(u'Tab acta'),
             fields=['title', 'horaInici', 'horaFi', 'llocConvocatoria',
                     'ordenDelDia', 'enllacVideo', 'acta', 'infoGDoc']
             )

    fieldset('assistents',
             label=_(u'Assistents'),
             fields=['membresConvocats', 'membresConvidats', 'llistaExcusats', 'llistaNoAssistens']
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    horaInici = schema.Datetime(
        title=_(u"Session start time"),
        required=False,
    )

    horaFi = schema.Datetime(
        title=_(u"Session end time"),
        required=False,
    )

    llocConvocatoria = schema.TextLine(
        title=_(u"Session location"),
        required=False,
    )

    directives.widget(membresConvocats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('membresConvocats')
    membresConvocats = schema.Text(
        title=_(u"Assistants"),
        description=_(u"Assistants help"),
        required=False,
    )

    directives.widget(membresConvidats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('membresConvidats')
    membresConvidats = schema.Text(
        title=_(u"Invited members"),
        description=_(u"Invited members help"),
        required=False,
    )

    directives.widget(llistaExcusats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('llistaExcusats')
    llistaExcusats = schema.Text(
        title=_(u"Excused members"),
        description=_(u"Excused members help"),
        required=False,
    )

    directives.widget(llistaNoAssistens=WysiwygFieldWidget)
    dexteritytextindexer.searchable('llistaNoAssistens')
    llistaNoAssistens = schema.Text(
        title=_(u"No assistents"),
        description=_(u"No assistents help"),
        required=False,
    )

    directives.widget(ordenDelDia=WysiwygFieldWidget)
    dexteritytextindexer.searchable('ordenDelDia')
    ordenDelDia = schema.Text(
        title=_(u"Session order"),
        description=_(u"Session order description"),
        required=False,
    )

    enllacVideo = schema.TextLine(
        title=_(u"Video link"),
        description=_(u"If you want to add a video file, not a url, there is a trick, you must add an Audio Type and leave this field empty."),
        required=False,
    )

    acta = NamedBlobFile(
        title=_(u"Acta PDF"),
        description=_(u"Acta PDF file description"),
        required=False,
    )

    directives.omitted('infoGDoc')
    infoGDoc = schema.Text(title=u'', required=False, default=u'{}')


@form.validator(field=IActa['acta'])
def validateFileType(value):
    if value is not None:
        mimetype = get_contenttype(value)
        if mimetype != 'application/pdf':
            raise InvalidPDFFile(mimetype)


@form.default_value(field=IActa['title'])
def titleDefaultValue(data):
    # copy membresConvidats from Session (parent object)
    return 'Acta - ' + data.context.Title()


@form.default_value(field=IActa['membresConvidats'])
def membresConvidatsDefaultValue(data):
    # copy membresConvidats from Session (parent object)
    return data.context.membresConvidats


@form.default_value(field=IActa['membresConvocats'])
def membresConvocatsDefaultValue(data):
    # copy membresConvocats from Session (parent object)
    return data.context.assistents


@form.default_value(field=IActa['llistaExcusats'])
def llistaExcusatsDefaultValue(data):
    # copy llistaExcusats from Session (parent object)
    return data.context.llistaExcusats


@form.default_value(field=IActa['llistaNoAssistens'])
def llistaNoAssistensDefaultValue(data):
    # copy noAssistents from Session (parent object)
    return data.context.noAssistents


# Hidden field used only to render and generate the PDF
@form.default_value(field=IActa['llocConvocatoria'])
def llocConvocatoriaDefaultValue(data):
    # copy llocConvocatoria from Session (parent object)
    return data.context.llocConvocatoria


# Hidden field used only to render and generate the PDF
@form.default_value(field=IActa['horaInici'])
def horaIniciDefaultValue(data):
    # copy horaInici from Session (parent object)
    acc = IEventAccessor(data.context)
    return acc.start


# Hidden field used only to render and generate the PDF
@form.default_value(field=IActa['horaFi'])
def horaFiDefaultValue(data):
    # copy horaFi from Session (parent object)
    acc = IEventAccessor(data.context)
    return acc.end


@form.default_value(field=IActa['ordenDelDia'])
def ordenDelDiaDefaultValue(data):
    # Copy all Punts from Session to Acta
    return Punts2Acta(data)


def Punts2Acta(self):
    """ Retorna els punt en format text per mostrar a l'ordre
        del dia de les actes
    """
    portal_catalog = api.portal.get_tool(name='portal_catalog')
    folder_path = '/'.join(self.context.getPhysicalPath())
    values = portal_catalog.searchResults(
        portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
        sort_on='getObjPositionInParent',
        path={'query': folder_path,
              'depth': 1})

    results = []
    results.append('<div class="num_acta"> <ol>')
    for obj in values:
        # value = obj.getObject()
        value = obj._unrestrictedGetObject()
        if value.portal_type == 'genweb.organs.acord':
            if value.agreement:
                agreement = ' [Acord ' + str(value.agreement) + ']'
            else:
                agreement = _(u"[Acord sense numerar]")
        else:
            agreement = ''
        results.append('<li>' + str(obj.Title) + ' ' + str(agreement))

        if len(value.objectIds()) > 0:
            valuesInside = portal_catalog.searchResults(
                portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                sort_on='getObjPositionInParent',
                path={'query': obj.getPath(),
                      'depth': 1})

            results.append('<ol>')
            for item in valuesInside:
                subpunt = item.getObject()
                if subpunt.portal_type == 'genweb.organs.acord':
                    if subpunt.agreement:
                        agreement = ' [Acord ' + str(subpunt.agreement) + ']'
                    else:
                        agreement = _("[Acord sense numerar]")
                else:
                    agreement = ''
                results.append('<li>' + str(item.Title) + ' ' + str(agreement) + '</li>')
            results.append('</ol></li>')
        else:
            results.append('</li>')

    results.append('</ol> </div>')

    return ''.join(results)


class View(dexterity.DisplayForm):
    grok.context(IActa)
    grok.template('acta_view')

    def canView(self):
        # Permissions to view acta
        if utils.isManager(self):
            return True
        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            else:
                raise Unauthorized
        else:
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            else:
                raise Unauthorized

    def viewPrintButon(self):
        if utils.isManager(self):
            return True
        if (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        else:
            return False

    def horaFi(self):
        if self.context.horaFi:
            return self.context.horaFi.strftime('%d/%m/%Y %H:%M')
        else:
            return ''

    def horaInici(self):
        if self.context.horaInici:
            return self.context.horaInici.strftime('%d/%m/%Y %H:%M')
        else:
            return ''

    def checkSerieGDoc(self):
        if utils.isManager(self) or utils.isSecretari(self):
            return utils.isValidSerieGdoc(self)

        return {'visible_gdoc': False,
                'valid_serie': False,
                'msg_error': ''}

    def AudioInside(self):
        """ Retorna els fitxers d'audio creats aquí dintre (sense tenir compte estat)
        """
        if not self.hasFirma():
            folder_path = '/'.join(self.context.getPhysicalPath())
            portal_catalog = getToolByName(self, 'portal_catalog')
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
                                        download_url=self.context.absolute_url() + '/@@download/file/' + audio.filename,
                                        content_type=audio.contentType))
                return results
        else:
            if self.context.infoGDoc['audios']:
                results = []
                for pos in self.context.infoGDoc['audios']:
                    audio = self.context.infoGDoc['audios'][pos]
                    results.append(dict(title=audio['title'],
                                        absolute_url=self.context.absolute_url() + '/viewAudio?pos=' + str(pos),
                                        download_url=self.context.absolute_url() + '/downloadAudio?pos=' + str(pos),
                                        content_type=audio['contentType']))
                return results

        return False

    def AnnexInside(self):
        """ Retorna els fitxers annexos creats aquí dintre (sense tenir compte estat)
        """
        if not self.hasFirma():
            folder_path = '/'.join(self.context.getPhysicalPath())
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
                                        download_url=self.context.absolute_url() + '/@@download/file/' + annex.filename,
                                        filename=annex.filename,
                                        sizeKB=annex.getSize() / 1024))
                return results
        else:
            if self.context.infoGDoc['adjunts']:
                results = []
                for pos in self.context.infoGDoc['adjunts']:
                    annex = self.context.infoGDoc['adjunts'][pos]
                    results.append(dict(title=annex['title'],
                                        absolute_url=self.context.absolute_url() + '/viewFile?pos=' + str(pos),
                                        download_url=self.context.absolute_url() + '/downloadFile?pos=' + str(pos),
                                        filename=annex['filename'],
                                        sizeKB=annex['sizeKB']))
                return results

        return False

    def getGdDocActa(self):
        if not isinstance(self.context.infoGDoc, dict):
            self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

        if self.context.infoGDoc and self.context.infoGDoc['acta'] != {}:
            return {'filename': self.context.infoGDoc['acta']['filename'],
                    'sizeKB': self.context.infoGDoc['acta']['sizeKB']}

    def hasUnitatDocumental(self):
        if not isinstance(self.context.infoGDoc, dict):
            self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

        return 'unitatDocumental' in self.context.infoGDoc

    def hasFirma(self):
        if not isinstance(self.context.infoGDoc, dict):
            self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

        return 'unitatDocumental' in self.context.infoGDoc and 'enviatASignar' in self.context.infoGDoc and self.context.infoGDoc['enviatASignar']

    def estatFirma(self):
        if not isinstance(self.context.infoGDoc, dict):
            self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

        if 'firma' in self.context.infoGDoc and 'id' in self.context.infoGDoc['firma']:
            gdoc_settings = utils.get_settings_gdoc()
            result = requests.get(gdoc_settings.portafirmes_url + '/' + str(self.context.infoGDoc['firma']['id']), headers={'X-Api-Key': gdoc_settings.portafirmes_apikey}, timeout=TIMEOUT)

            if result.status_code == 200:
                content = json.loads(result.content)
                self.context.infoGDoc['firma']['estat'] = content['estatPeticio']
                return content['estatPeticio']
            else:
                self.context.plone_utils.addPortalMessage(_(u'No s\'ha pogut obtenir informació del portafirmes: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                return self.context.infoGDoc['firma']['estat']
        else:
            return 'PENDENT'


class Edit(dexterity.EditForm):
    """A standard edit form.
    """
    grok.context(IActa)


class SignActa(grok.View):
    grok.context(IActa)
    grok.name('signActa')
    grok.require('genweb.organs.gdoc.sign')

    def getSignants(self):
        local_roles = self.context.get_local_roles()
        users = []
        for user in local_roles:
            if 'OG1-Secretari' in user[1]:
                try:
                    users_group = api.user.get_users(groupname=user[0])
                    for userx in users_group:
                        if userx:
                            users.append(userx.id)
                except:
                    users.append(user[0])

        return users

    def generateActaPDF(self):
        options = {'cookie': [('__ac', self.request.cookies['__ac']), ]}
        pdfkit.from_url(self.context.absolute_url() + '/printActa', '/tmp/' + self.context.id + '.pdf', options=options)
        return open('/tmp/' + self.context.id + '.pdf', 'r')

    def removeActaPDF(self):
        os.remove('/tmp/' + self.context.id + '.pdf')

    def render(self):
        actaPDF = self.generateActaPDF()

        if not isinstance(self.context.infoGDoc, dict):
            self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

        if self.context.infoGDoc and 'enviatASignar' in self.context.infoGDoc and self.context.infoGDoc['enviatASignar']:
            return self.request.response.redirect(self.context.absolute_url())

        signants = self.getSignants()
        if not signants:
            self.context.plone_utils.addPortalMessage(_(u'No hi ha secretaris per firmar l\'acta.'), 'error')
            return self.request.response.redirect(self.context.absolute_url())

        organ = utils.get_organ(self.context)
        if organ.visiblegdoc:

            gdoc_settings = utils.get_settings_gdoc()

            try:
                if self.context.infoGDoc and 'unitatDocumental' in self.context.infoGDoc and self.context.infoGDoc['unitatDocumental']:
                    logger.info('0. Eliminació serie documental en gdoc per tornar-la a crear')
                    result_del = requests.delete(gdoc_settings.gdoc_url + '/api/udch/' + self.context.infoGDoc['unitatDocumental'] + '/esborrar?&hash=' + gdoc_settings.gdoc_hash, timeout=TIMEOUT)

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
                result_codi = requests.get(gdoc_settings.codiexpedient_url + '/api/codi?serie=' + organ.serie, headers={'X-Api-Key': gdoc_settings.codiexpedient_apikey}, timeout=TIMEOUT)

                if result_codi.status_code == 200:
                    logger.info('2.1. S\'ha obtingut correctament el codi del expedient')
                    content_codi = json.loads(result_codi.content)

                    now = datetime.datetime.now()
                    codi_expedient = now.strftime("%Y") + '-' + content_codi['codi']

                    data_exp = {"expedient": codi_expedient,
                                "titolPropi": codi_expedient + ' - ' + self.context.title}

                    # Petició que crea un sèrie documental / expedient en gdoc
                    logger.info('3. Creació de la serie documental en gdoc')
                    result_exp = requests.post(gdoc_settings.gdoc_url + '/api/serie/' + organ.serie + '/udch?uid=' + gdoc_settings.gdoc_user + '&hash=' + gdoc_settings.gdoc_hash, json=data_exp, timeout=TIMEOUT)
                    content_exp = json.loads(result_exp.content)

                    if result_exp.status_code == 200:
                        if 'idElementCreat' in content_exp:

                            logger.info('3.1. S\'ha creat correctament la serie documental')
                            if not isinstance(self.context.infoGDoc, dict):
                                self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

                            self.context.infoGDoc.update({'unitatDocumental': str(content_exp['idElementCreat']),
                                                          'acta': {},
                                                          'adjunts': {},
                                                          'audios': {},
                                                          'enviatASignar': False,
                                                          'firma': {}})
                            self.context.reindexObject()

                            data_acta = {"tipusDocumental": "452",
                                         "idioma": "CA",
                                         "nomAplicacioCreacio": "Govern UPC",
                                         "autors": "[{'id': '1291399'}]",
                                         "agentsAmbCodiEsquemaIdentificacio": False,
                                         "validesaAdministrativa": True}

                            files = {'fitxer': (self.context.id + '.pdf', actaPDF.read(), 'application/pdf')}

                            # Pujem l'acta a la sèrie documental creada al gdoc
                            logger.info('4. Puja de l\'acta al gdoc')
                            result_acta = requests.post(gdoc_settings.gdoc_url + '/api/pare/' + str(content_exp['idElementCreat']) + '/doce?uid=' + gdoc_settings.gdoc_user + '&hash=' + gdoc_settings.gdoc_hash, data=data_acta, files=files)

                            content_acta = json.loads(result_acta.content)
                            if result_acta.status_code == 200:
                                logger.info('4.1. S\'ha creat correctament l\'acta')

                                # Obtenim el uuid de la acta pujada, necessària per a la petició al portafirmes
                                logger.info('4.2. Petició per demanar el uuid de l\'acta')
                                result_info_acta = requests.get(gdoc_settings.gdoc_url + '/api/doce/' + str(content_acta['idElementCreat']) + '/consulta?hash=' + gdoc_settings.gdoc_hash, timeout=TIMEOUT)

                                content_info_acta = json.loads(result_info_acta.content)
                                if result_info_acta.status_code == 200:
                                    logger.info('4.3. S\'ha obtingut correctament el uuid de l\'acta')
                                    self.context.infoGDoc['acta'] = {'id': str(content_acta['idElementCreat']),
                                                                     'uuid': str(content_info_acta['documentElectronic']['uuid']),
                                                                     'filename': self.context.id + '.pdf',
                                                                     'contentType': 'application/pdf',
                                                                     'sizeKB': os.path.getsize(self.context.id + '.pdf') / 1024}
                                    self.context.reindexObject()

                                else:
                                    logger.info('4.2.ERROR. Petició per demanar el uuid de l\'acta')
                                    logger.info(result_info_acta.content)
                                    self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pugut obtenir l\'informació de l\'acta: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                                    return self.request.response.redirect(self.context.absolute_url())

                            else:
                                logger.info('4.ERROR. Puja de l\'acta al gdoc')
                                logger.info(result_acta.content)
                                self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pogut pujar l\'acta: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
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
                                    result_file = requests.post(gdoc_settings.gdoc_url + '/api/pare/' + str(content_exp['idElementCreat']) + '/doce?uid=' + gdoc_settings.gdoc_user + '&hash=' + gdoc_settings.gdoc_hash, data=data_file, files=files)

                                    content_file = json.loads(result_file.content)
                                    if result_file.status_code == 200:
                                        logger.info('5.1. S\'ha creat correctament el fitxer adjunt')

                                        # Obtenim el uuid del fitxer adjunt pujat, necessària per a la petició al portafirmes
                                        logger.info('5.2. Petició per demanar el uuid del fitxer adjunt')
                                        result_info_file = requests.get(gdoc_settings.gdoc_url + '/api/doce/' + str(content_file['idElementCreat']) + '/consulta?hash=' + gdoc_settings.gdoc_hash, timeout=TIMEOUT)

                                        content_info_file = json.loads(result_info_file.content)
                                        if result_info_file.status_code == 200:
                                            logger.info('5.3. S\'ha obtingut correctament el uuid del fitxer adjunt')
                                            self.context.infoGDoc['adjunts'].update({str(pos): {'id': str(content_file['idElementCreat']),
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
                                            return self.request.response.redirect(self.context.absolute_url())

                                    else:
                                        logger.info('5.ERROR. Puja del fitxer adjunt al gdoc - ' + annex.file.filename)
                                        logger.info(result_file.content)
                                        self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pogut pujar el fitxer adjunt: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
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
                                    result_audio = requests.post(gdoc_settings.gdoc_url + '/api/pare/' + str(content_exp['idElementCreat']) + '/doce?uid=' + gdoc_settings.gdoc_user + '&hash=' + gdoc_settings.gdoc_hash, data=data_audio, files=files)

                                    content_audio = json.loads(result_audio.content)
                                    if result_audio.status_code == 200:
                                        logger.info('6.1. S\'ha creat correctament el àudio')

                                        # Obtenim el uuid de l'àudio pujat, necessària per a la petició al portafirmes
                                        logger.info('6.2. Petició per demanar el uuid del àudio')
                                        result_info_audio = requests.get(gdoc_settings.gdoc_url + '/api/doce/' + str(content_audio['idElementCreat']) + '/consulta?hash=' + gdoc_settings.gdoc_hash, timeout=TIMEOUT)

                                        content_info_audio = json.loads(result_info_audio.content)
                                        if result_info_audio.status_code == 200:
                                            logger.info('6.3. S\'ha obtingut correctament el uuid del àudio')
                                            self.context.infoGDoc['audios'].update({str(pos): {'id': str(content_audio['idElementCreat']),
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
                                            return self.request.response.redirect(self.context.absolute_url())

                                    else:
                                        logger.info('6.ERROR. Puja del àudio al gdoc - ' + audio.file.filename)
                                        logger.info(result_audio.content)
                                        self.context.plone_utils.addPortalMessage(_(u'GDoc: No s\'ha pogut pujar el àudio: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                                        return self.request.response.redirect(self.context.absolute_url())

                            data_sign = {
                                "descripcioPeticio": "Signatura acta" + ' - ' + self.context.title,
                                "documents": [
                                    {
                                        "paginaSignaturaVisible": 1,
                                        "codi": self.context.infoGDoc['acta']['uuid']
                                    }
                                ],
                                "passosPeticio": [
                                    {
                                        "nivellSignatura": "CDA",
                                        "signants": [{"commonName": signant} for signant in signants],
                                    },
                                ],
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
                                ]
                            }

                            if self.context.infoGDoc['audios'] or self.context.infoGDoc['adjunts']:
                                data_sign.update({'documentsAnnexos': []})
                                for adjunt in self.context.infoGDoc['adjunts']:
                                    data_sign['documentsAnnexos'].append({"codi": self.context.infoGDoc['adjunts'][adjunt]['uuid']})

                                for audio in self.context.infoGDoc['audios']:
                                    data_sign['documentsAnnexos'].append({"codi": self.context.infoGDoc['audios'][audio]['uuid']})

                            # Creem la petició al portafirmes de l'acta i els àudios annexos
                            logger.info('7. Petició de la firma al portafirmes')
                            result_sign = requests.post(gdoc_settings.portafirmes_url, json=data_sign, headers={'X-Api-Key': gdoc_settings.portafirmes_apikey})

                            if result_sign.status_code == 201:
                                logger.info('7.1. La petició de la firma s\'ha processat correctament')
                                self.context._Add_portal_content_Permission = ('Manager', 'Site Administrator', 'WebMaster')
                                self.context._Modify_portal_content_Permission = ('Manager', 'Site Administrator', 'WebMaster')
                                self.context._Delete_objects_Permission = ('Manager', 'Site Administrator', 'WebMaster')

                                self.context.acta = None
                                for audio_id in self.context:
                                    api.content.delete(self.context[audio_id])

                                self.context.infoGDoc['enviatASignar'] = True

                                content_sign = json.loads(result_sign.content)
                                self.context.infoGDoc['firma'] = {'id': content_sign['idPeticio'],
                                                                  'estat': content_sign['estatPeticio']}

                                self.context.plone_utils.addPortalMessage(_(u'S\'ha enviat a firmar correctament'), 'success')
                                transaction.commit()
                            else:
                                logger.info('7.ERROR. Petició de la firma al portafirmes')
                                logger.info(result_sign.content)
                                self.context.plone_utils.addPortalMessage(_(u'No s\'ha pogut enviar a firmar: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')

                            return self.request.response.redirect(self.context.absolute_url())
                    else:
                        logger.info('3.ERROR. Creació de la serie documental en gdoc')
                        logger.info(result_exp.content)
                        if 'codi' in content_exp:
                            if content_exp['codi'] == 503:
                                self.context.plone_utils.addPortalMessage(_(u'GDoc: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                            elif content_exp['codi'] == 528:
                                self.context.plone_utils.addPortalMessage(_(u'GDoc: La sèrie documental configurada no existeix'), 'error')

                            return self.request.response.redirect(self.context.absolute_url())

                        self.context.plone_utils.addPortalMessage(_(u'GDoc: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                        return self.request.response.redirect(self.context.absolute_url())
                else:
                    logger.info('2.ERROR. Demamant codi del expedient al servei generadorcodiexpedient')
                    logger.info(result_codi.content)
                    self.context.plone_utils.addPortalMessage(_(u'No s\'ha pogut generar el codi de expedient: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                    return self.request.response.redirect(self.context.absolute_url())
            except:
                self.context.plone_utils.addPortalMessage(_(u'S\'ha sobrepasat el temps d\'espera per executar la petició: Contacta amb algun administrador de la web perquè revisi la configuració'), 'error')
                return self.request.response.redirect(self.context.absolute_url())

            try:
                self.removeActaPDF()
            except:
                pass


class ViewActa(grok.View):
    grok.context(IActa)
    grok.name('viewActa')
    grok.require('genweb.organs.gdoc.view')

    def render(self):
        organ = utils.get_organ(self.context)
        if organ.visiblegdoc:
            gdoc_settings = utils.get_settings_gdoc()

            if not isinstance(self.context.infoGDoc, dict):
                self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

            result = requests.get(gdoc_settings.gdoc_url + '/api/documentelectronic/' + self.context.infoGDoc['acta']['uuid'] + '?uid=' + gdoc_settings.gdoc_user + '&hash=' + gdoc_settings.gdoc_hash)

            if result.status_code == 200:
                self.request.response.setHeader('content-type', self.context.infoGDoc['acta']['contentType'])
                self.request.response.setHeader('content-disposition', 'inline; filename=' + str(self.context.infoGDoc['acta']['filename']))
                return result.content
            else:
                self.context.plone_utils.addPortalMessage(_(u'Error al consultar les dades'), 'error')

            return self.request.response.redirect(self.context.absolute_url())


class DownloadActa(grok.View):
    grok.context(IActa)
    grok.name('downloadActa')
    grok.require('genweb.organs.gdoc.view')

    def render(self):
        organ = utils.get_organ(self.context)
        if organ.visiblegdoc:
            gdoc_settings = utils.get_settings_gdoc()

            if not isinstance(self.context.infoGDoc, dict):
                self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

            result = requests.get(gdoc_settings.gdoc_url + '/api/documentelectronic/' + self.context.infoGDoc['acta']['uuid'] + '?uid=' + gdoc_settings.gdoc_user + '&hash=' + gdoc_settings.gdoc_hash)

            if result.status_code == 200:
                self.request.response.setHeader('content-type', self.context.infoGDoc['acta']['contentType'])
                self.request.response.setHeader('content-disposition', 'attachment; filename=' + str(self.context.infoGDoc['acta']['filename']))
                return result.content
            else:
                self.context.plone_utils.addPortalMessage(_(u'Error al consultar les dades'), 'error')

            return self.request.response.redirect(self.context.absolute_url())


class ViewFile(grok.View):
    grok.context(IActa)
    grok.name('viewFile')
    grok.require('genweb.organs.gdoc.view')

    def render(self):
        if 'pos' in self.request:
            organ = utils.get_organ(self.context)
            if organ.visiblegdoc:
                gdoc_settings = utils.get_settings_gdoc()

                if not isinstance(self.context.infoGDoc, dict):
                    self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

                result = requests.get(gdoc_settings.gdoc_url + '/api/documentelectronic/' + self.context.infoGDoc['adjunts'][self.request['pos']]['uuid'] + '?uid=' + gdoc_settings.gdoc_user + '&hash=' + gdoc_settings.gdoc_hash)

                if result.status_code == 200:
                    self.request.response.setHeader('content-type', self.context.infoGDoc['adjunts'][self.request['pos']]['contentType'])
                    self.request.response.setHeader('content-disposition', 'inline; filename=' + str(self.context.infoGDoc['adjunts'][self.request['pos']]['filename']))
                    return result.content
                else:
                    self.context.plone_utils.addPortalMessage(_(u'Error al consultar les dades'), 'error')

            return self.request.response.redirect(self.context.absolute_url())


class DownloadFile(grok.View):
    grok.context(IActa)
    grok.name('downloadFile')
    grok.require('genweb.organs.gdoc.view')

    def render(self):
        if 'pos' in self.request:
            organ = utils.get_organ(self.context)
            if organ.visiblegdoc:
                gdoc_settings = utils.get_settings_gdoc()

                if not isinstance(self.context.infoGDoc, dict):
                    self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

                result = requests.get(gdoc_settings.gdoc_url + '/api/documentelectronic/' + self.context.infoGDoc['adjunts'][self.request['pos']]['uuid'] + '?uid=' + gdoc_settings.gdoc_user + '&hash=' + gdoc_settings.gdoc_hash)

                if result.status_code == 200:
                    self.request.response.setHeader('content-type', self.context.infoGDoc['adjunts'][self.request['pos']]['contentType'])
                    self.request.response.setHeader('content-disposition', 'attachment; filename=' + str(self.context.infoGDoc['adjunts'][self.request['pos']]['filename']))
                    return result.content
                else:
                    self.context.plone_utils.addPortalMessage(_(u'Error al consultar les dades'), 'error')

                return self.request.response.redirect(self.context.absolute_url())


class ViewAudio(grok.View):
    grok.context(IActa)
    grok.name('viewAudio')
    grok.require('genweb.organs.gdoc.view')

    def render(self):
        if 'pos' in self.request:
            organ = utils.get_organ(self.context)
            if organ.visiblegdoc:
                gdoc_settings = utils.get_settings_gdoc()

                if not isinstance(self.context.infoGDoc, dict):
                    self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

                result = requests.get(gdoc_settings.gdoc_url + '/api/documentelectronic/' + self.context.infoGDoc['audios'][self.request['pos']]['uuid'] + '?uid=' + gdoc_settings.gdoc_user + '&hash=' + gdoc_settings.gdoc_hash)

                if result.status_code == 200:
                    self.request.response.setHeader('content-type', self.context.infoGDoc['audios'][self.request['pos']]['contentType'])
                    self.request.response.setHeader('content-disposition', 'inline; filename=' + str(self.context.infoGDoc['audios'][self.request['pos']]['filename']))
                    return result.content
                else:
                    self.context.plone_utils.addPortalMessage(_(u'Error al consultar les dades'), 'error')

            return self.request.response.redirect(self.context.absolute_url())


class DownloadAudio(grok.View):
    grok.context(IActa)
    grok.name('downloadAudio')
    grok.require('genweb.organs.gdoc.view')

    def render(self):
        if 'pos' in self.request:
            organ = utils.get_organ(self.context)
            if organ.visiblegdoc:
                gdoc_settings = utils.get_settings_gdoc()

                if not isinstance(self.context.infoGDoc, dict):
                    self.context.infoGDoc = ast.literal_eval(self.context.infoGDoc)

                result = requests.get(gdoc_settings.gdoc_url + '/api/documentelectronic/' + self.context.infoGDoc['audios'][self.request['pos']]['uuid'] + '?uid=' + gdoc_settings.gdoc_user + '&hash=' + gdoc_settings.gdoc_hash)

                if result.status_code == 200:
                    self.request.response.setHeader('content-type', self.context.infoGDoc['audios'][self.request['pos']]['contentType'])
                    self.request.response.setHeader('content-disposition', 'attachment; filename=' + str(self.context.infoGDoc['audios'][self.request['pos']]['filename']))
                    return result.content
                else:
                    self.context.plone_utils.addPortalMessage(_(u'Error al consultar les dades'), 'error')

                return self.request.response.redirect(self.context.absolute_url())
