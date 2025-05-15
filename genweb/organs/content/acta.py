# -*- coding: utf-8 -*-
from AccessControl import Unauthorized

from collective import dexteritytextindexer
from plone import api
from Products.CMFPlone import PloneMessageFactory as _PMF
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from z3c.form import form
from plone.event.interfaces import IEventAccessor
from plone.namedfile.field import NamedBlobFile
from plone.supermodel.directives import fieldset
from zope import schema
from plone.supermodel import model

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental.utils import UtilsFirmaDocumental

import ast

import transaction

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# Define las funciones defaultFactory para cada campo
def title_default_factory(context):
    return 'Acta - ' + context.Title()

def membres_convidats_default_factory(context):
    return context.membresConvidats

def membres_convocats_default_factory(context):
    return context.assistents

def llista_excuses_default_factory(context):
    return context.llistaExcusats

def llista_no_assistens_default_factory(context):
    return context.noAssistents

def lloc_convocatoria_default_factory(context):
    return context.llocConvocatoria

def hora_inici_default_factory(context):
    acc = IEventAccessor(context)
    return acc.start

def hora_fi_default_factory(context):
    acc = IEventAccessor(context)
    return acc.end

def orden_del_dia_default_factory(context):
    return Punts2Acta(context)


class IActa(model.Schema):
    """ ACTA """

    fieldset('acta',
             label=_(u'Tab acta'),
             fields=['title', 'horaInici', 'horaFi', 'llocConvocatoria',
                     'ordenDelDia', 'enllacVideo', 'acta']
             )

    fieldset('assistents',
             label=_(u'Assistents'),
             fields=['membresConvocats', 'membresConvidats', 'llistaExcusats', 'llistaNoAssistens']
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True,
        defaultFactory=title_default_factory
    )

    horaInici = schema.Datetime(
        title=_(u"Session start time"),
        required=False,
        defaultFactory=hora_inici_default_factory
    )

    horaFi = schema.Datetime(
        title=_(u"Session end time"),
        required=False,
        defaultFactory=hora_fi_default_factory
    )

    llocConvocatoria = schema.TextLine(
        title=_(u"Session location"),
        required=False,
        defaultFactory=lloc_convocatoria_default_factory
    )

    directives.widget(membresConvocats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('membresConvocats')
    membresConvocats = schema.Text(
        title=_(u"Assistants"),
        description=_(u"Assistants help"),
        required=False,
        defaultFactory=membres_convocats_default_factory
    )

    directives.widget(membresConvidats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('membresConvidats')
    membresConvidats = schema.Text(
        title=_(u"Invited members"),
        description=_(u"Invited members help"),
        required=False,
        defaultFactory=membres_convidats_default_factory
    )

    directives.widget(llistaExcusats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('llistaExcusats')
    llistaExcusats = schema.Text(
        title=_(u"Excused members"),
        description=_(u"Excused members help"),
        required=False,
        defaultFactory=llista_excuses_default_factory
    )

    directives.widget(llistaNoAssistens=WysiwygFieldWidget)
    dexteritytextindexer.searchable('llistaNoAssistens')
    llistaNoAssistens = schema.Text(
        title=_(u"No assistents"),
        description=_(u"No assistents help"),
        required=False,
        defaultFactory=llista_no_assistens_default_factory
    )

    directives.widget(ordenDelDia=WysiwygFieldWidget)
    dexteritytextindexer.searchable('ordenDelDia')
    ordenDelDia = schema.Text(
        title=_(u"Session order"),
        description=_(u"Session order description"),
        required=False,
        defaultFactory=orden_del_dia_default_factory
    )

    enllacVideo = schema.TextLine(
        title=_(u"Video link"),
        description=_(u"If you want to add a video file, not a url, there is a trick, you must add an Audio Type and leave this field empty."),
        required=False,
    )

    directives.mode(acta='hidden')
    acta = NamedBlobFile(
        title=_(u"Acta PDF"),
        description=_(u"Acta PDF file description"),
        required=False,
    )


# @form.default_value(field=IActa['title'])
# def titleDefaultValue(data):
#     # copy membresConvidats from Session (parent object)
#     return 'Acta - ' + data.context.Title()


# @form.default_value(field=IActa['membresConvidats'])
# def membresConvidatsDefaultValue(data):
#     # copy membresConvidats from Session (parent object)
#     return data.context.membresConvidats


# @form.default_value(field=IActa['membresConvocats'])
# def membresConvocatsDefaultValue(data):
#     # copy membresConvocats from Session (parent object)
#     return data.context.assistents


# @form.default_value(field=IActa['llistaExcusats'])
# def llistaExcusatsDefaultValue(data):
#     # copy llistaExcusats from Session (parent object)
#     return data.context.llistaExcusats


# @form.default_value(field=IActa['llistaNoAssistens'])
# def llistaNoAssistensDefaultValue(data):
#     # copy noAssistents from Session (parent object)
#     return data.context.noAssistents


# # Hidden field used only to render and generate the PDF
# @form.default_value(field=IActa['llocConvocatoria'])
# def llocConvocatoriaDefaultValue(data):
#     # copy llocConvocatoria from Session (parent object)
#     return data.context.llocConvocatoria


# # Hidden field used only to render and generate the PDF
# @form.default_value(field=IActa['horaInici'])
# def horaIniciDefaultValue(data):
#     # copy horaInici from Session (parent object)
#     acc = IEventAccessor(data.context)
#     return acc.start


# # Hidden field used only to render and generate the PDF
# @form.default_value(field=IActa['horaFi'])
# def horaFiDefaultValue(data):
#     # copy horaFi from Session (parent object)
#     acc = IEventAccessor(data.context)
#     return acc.end


# @form.default_value(field=IActa['ordenDelDia'])
# def ordenDelDiaDefaultValue(data):
#     # Copy all Punts from Session to Acta
#     return Punts2Acta(data)


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
    results.append('<div class="num_acta">')
    for obj in values:
        # value = obj.getObject()
        value = obj._unrestrictedGetObject()
        if value.portal_type == 'genweb.organs.acord':
            if value.agreement:
                agreement = ' [Acord ' + str(value.agreement) + ']'
            else:
                agreement = _(u"[Acord sense numerar]")  if not getattr(value, 'omitAgreement', False) else ''
        else:
            agreement = ''
        results.append('<p>' + str(value.proposalPoint) + '. ' + str(obj.Title) + ' ' + str(agreement) + '</p>')

        if len(value.objectIds()) > 0:
            valuesInside = portal_catalog.searchResults(
                portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                sort_on='getObjPositionInParent',
                path={'query': obj.getPath(),
                      'depth': 1})

            for item in valuesInside:
                subpunt = item.getObject()
                if subpunt.portal_type == 'genweb.organs.acord':
                    if subpunt.agreement:
                        agreement = ' [Acord ' + str(subpunt.agreement) + ']'
                    else:
                        agreement = _("[Acord sense numerar]") if not getattr(subpunt, 'omitAgreement', False) else ''
                else:
                    agreement = ''
                results.append('<p style="padding-left: 30px;">' + str(subpunt.proposalPoint) + '. ' + str(item.Title) + ' ' + str(agreement) + '</p>')

    results.append('</div>')
    return ''.join(results)


class View(BrowserView, UtilsFirmaDocumental):
    index = ViewPageTemplateFile("templates/acta_view.pt")

    def __call__(self):
        return self.index()

    def canView(self):
        # Permissions to view acta
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
            return True
        elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif organ_tipus == 'open_organ' and estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
            return True
        elif organ_tipus != 'open_organ' and estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        else:
            raise Unauthorized

    def viewPrintButon(self):
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True
        if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
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

    def AudioInside(self):
        """ Retorna els fitxers d'audio creats aquí dintre (sense tenir compte estat)
        """
        if not self.hasFirma():
            folder_path = '/'.join(self.context.getPhysicalPath())
            portal_catalog = api.portal.get_tool(name='portal_catalog')
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
                                        download_url=obj.getURL() + '/@@download/file',
                                        content_type=audio.contentType))
                return results
        else:
            if self.context.info_firma['audios']:
                results = []
                for pos in self.context.info_firma['audios']:
                    audio = self.context.info_firma['audios'][pos]
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
            if 'adjunts' in self.context.info_firma and self.context.info_firma['adjunts']:
                results = []
                for pos in self.context.info_firma['adjunts']:
                    annex = self.context.info_firma['adjunts'][pos]
                    results.append(dict(title=annex['title'],
                                        absolute_url=self.context.absolute_url() + '/viewFile?pos=' + str(pos),
                                        download_url=self.context.absolute_url() + '/downloadFile?pos=' + str(pos),
                                        filename=annex['filename'],
                                        sizeKB=annex['sizeKB']))
                return results

        return False

    def getPFDActa(self):
        if not hasattr(self.context, 'info_firma'):
            self.context.info_firma = {}
            transaction.commit()
            self.context.reindexObject()

        if not isinstance(self.context.info_firma, dict):
            self.context.info_firma = ast.literal_eval(self.context.info_firma)

        if self.context.info_firma and self.context.info_firma['acta'] != {}:
            return {'filename': self.context.info_firma['acta']['filename'],
                    'sizeKB': self.context.info_firma['acta']['sizeKB']}

    def isSigned(self):
        estat_firma = getattr(self.context, 'estat_firma', None) or ""
        if self.hasFirma() and estat_firma.lower() == 'signada':
            return True
        return False

class Edit(form.EditForm):
    """A standard edit form.
    """
    pass
