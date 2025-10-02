# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.CMFPlone.utils import safe_unicode
from html import escape

from plone.app.dexterity import textindexer
from plone import api
from Products.CMFPlone import PloneMessageFactory as _PMF
from plone.autoform import directives
from z3c.form import form
from plone.event.interfaces import IEventAccessor
from plone.namedfile.field import NamedBlobFile
from plone.supermodel.directives import fieldset
from zope import schema
from plone.supermodel import model
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.interface import provider
from zope.component import ComponentLookupError
from plone.app.textfield import RichText as RichTextField

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental.utils import UtilsFirmaDocumental

import ast

import transaction

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# Define las funciones defaultFactory para cada campo


@provider(IContextAwareDefaultFactory)
def title_default_factory(context):
    return 'Acta - ' + context.Title()


def get_richtext_content(field_value):
    """Safely get content from a RichText or Text field."""
    if hasattr(field_value, 'raw'):
        return field_value.raw
    return field_value or ''


@provider(IContextAwareDefaultFactory)
def membres_convidats_default_factory(context):
    parent = getattr(context, 'aq_parent', None) or getattr(context, '__parent__', None)
    source = getattr(parent, 'membresConvidats', None)
    return get_richtext_content(source)


@provider(IContextAwareDefaultFactory)
def membres_convocats_default_factory(context):
    parent = getattr(context, 'aq_parent', None) or getattr(context, '__parent__', None)
    source = getattr(parent, 'assistents', None)
    return get_richtext_content(source)


@provider(IContextAwareDefaultFactory)
def llista_excuses_default_factory(context):
    parent = getattr(context, 'aq_parent', None) or getattr(context, '__parent__', None)
    source = getattr(parent, 'llistaExcusats', None)
    return get_richtext_content(source)


@provider(IContextAwareDefaultFactory)
def llista_no_assistens_default_factory(context):
    parent = getattr(context, 'aq_parent', None) or getattr(context, '__parent__', None)
    source = getattr(parent, 'noAssistents', None)
    return get_richtext_content(source)


@provider(IContextAwareDefaultFactory)
def lloc_convocatoria_default_factory(context):
    parent = getattr(context, 'aq_parent', None) or getattr(context, '__parent__', None)
    return getattr(parent, 'llocConvocatoria', None)


@provider(IContextAwareDefaultFactory)
def hora_inici_default_factory(context):
    """Obtener hora de inicio del contexto padre (sessió).

    Durante la creación o migración, si no hay parent válido,
    retorna None.
    """
    parent = getattr(context, 'aq_parent', None) or getattr(context, '__parent__', None)
    if parent is None:
        return None

    try:
        acc = IEventAccessor(parent)
        return acc.start
    except (TypeError, ComponentLookupError):
        # Si el parent no es IEventAccessor, intentar con context
        try:
            acc = IEventAccessor(context)
            return acc.start
        except (TypeError, ComponentLookupError):
            # Si tampoco funciona, retornar None
            return None


@provider(IContextAwareDefaultFactory)
def hora_fi_default_factory(context):
    """Obtener hora de fin del contexto padre (sessió).

    Durante la creación o migración, si no hay parent válido,
    retorna None.
    """
    parent = getattr(context, 'aq_parent', None) or getattr(context, '__parent__', None)
    if parent is None:
        return None

    try:
        acc = IEventAccessor(parent)
        return acc.end
    except (TypeError, ComponentLookupError):
        # Si el parent no es IEventAccessor, intentar con context
        try:
            acc = IEventAccessor(context)
            return acc.end
        except (TypeError, ComponentLookupError):
            # Si tampoco funciona, retornar None
            return None


@provider(IContextAwareDefaultFactory)
def orden_del_dia_default_factory(context):
    return Punts2Acta(context)


class IActa(model.Schema):
    """ ACTA """

    fieldset('acta',
             label=_(u'Tab acta'),
             fields=['title', 'horaInici', 'horaFi', 'llocConvocatoria',
                     'ordenDelDia', 'enllacVideo', 'acta']
             )

    fieldset('assistents', label=_(u'Assistents'), fields=[
             'membresConvocats', 'membresConvidats', 'llistaExcusats', 'llistaNoAssistens'])

    textindexer.searchable('title')
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

    textindexer.searchable('membresConvocats')
    membresConvocats = RichTextField(
        title=_(u"Assistants"),
        description=_(u"Assistants help"),
        required=False,
        defaultFactory=membres_convocats_default_factory
    )

    textindexer.searchable('membresConvidats')
    membresConvidats = RichTextField(
        title=_(u"Invited members"),
        description=_(u"Invited members help"),
        required=False,
        defaultFactory=membres_convidats_default_factory
    )

    textindexer.searchable('llistaExcusats')
    llistaExcusats = RichTextField(
        title=_(u"Excused members"),
        description=_(u"Excused members help"),
        required=False,
        defaultFactory=llista_excuses_default_factory
    )

    textindexer.searchable('llistaNoAssistens')
    llistaNoAssistens = RichTextField(
        title=_(u"No assistents"),
        description=_(u"No assistents help"),
        required=False,
        defaultFactory=llista_no_assistens_default_factory
    )

    textindexer.searchable('ordenDelDia')
    ordenDelDia = RichTextField(
        title=_(u"Session order"),
        description=_(u"Session order description"),
        required=False,
        defaultFactory=orden_del_dia_default_factory
    )

    enllacVideo = schema.TextLine(
        title=_(u"Video link"),
        description=_(
            u"If you want to add a video file, not a url, there is a trick, you must add an Audio Type and leave this field empty."),
        required=False,)

    directives.omitted('acta')
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


def Punts2Acta(context):
    """ Retorna els punt en format text per mostrar a l'ordre
        del dia de les actes.
        Refactored for Python 3 and Plone 6.
    """
    portal_catalog = api.portal.get_tool(name='portal_catalog')
    folder_path = '/'.join(context.getPhysicalPath())
    values = portal_catalog.searchResults(
        portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
        sort_on='getObjPositionInParent',
        path={'query': folder_path,
              'depth': 1})

    results = ['<div class="num_acta">']
    for obj in values:
        value = obj._unrestrictedGetObject()
        title = escape(safe_unicode(obj.Title))
        try:
            proposal_point = escape(safe_unicode(value.proposalPoint))
        except:
            proposal_point = str(value.proposalPoint)
        agreement_text = ''

        if value.portal_type == 'genweb.organs.acord':
            if value.agreement:
                agreement_text = f' [Acord {escape(safe_unicode(value.agreement))}]'
            elif not getattr(value, 'omitAgreement', False):
                agreement_text = f' [{_("Acord sense numerar")}]'

        results.append(f'<p>{proposal_point}. {title}{agreement_text}</p>')

        # Check for sub-items
        if len(value.objectIds()) > 0:
            valuesInside = portal_catalog.searchResults(
                portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                sort_on='getObjPositionInParent',
                path={'query': obj.getPath(),
                      'depth': 1})

            for item in valuesInside:
                subpunt = item.getObject()
                sub_title = escape(safe_unicode(item.Title))
                sub_proposal_point = escape(safe_unicode(subpunt.proposalPoint))
                sub_agreement_text = ''

                if subpunt.portal_type == 'genweb.organs.acord':
                    if subpunt.agreement:
                        agreement_value = escape(safe_unicode(subpunt.agreement))
                        sub_agreement_text = f' [Acord {agreement_value}]'
                    elif not getattr(subpunt, 'omitAgreement', False):
                        sub_agreement_text = f' [{_("Acord sense numerar")}]'

                results.append(
                    f'<p style="padding-left: 30px;">{sub_proposal_point}. {sub_title}{sub_agreement_text}</p>')

    results.append('</div>')
    return ''.join(results)


class View(BrowserView, UtilsFirmaDocumental):
    index = ViewPageTemplateFile("acta.pt")

    def __call__(self):
        return self.index()

    @property
    def title(self):
        """Devuelve el título del anexo."""
        return getattr(self.context, 'title', '')

    def canView(self):
        # Permissions to view acta
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if estatSessio == 'planificada' and utils.checkhasRol(
            ['OG1-Secretari', 'OG2-Editor'],
                roles):
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
                    results.append(
                        dict(
                            title=audio['title'],
                            absolute_url=self.context.absolute_url() +
                            '/viewAudio?pos=' + str(pos),
                            download_url=self.context.absolute_url() +
                            '/downloadAudio?pos=' + str(pos),
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
                    results.append(
                        dict(
                            title=obj.Title, absolute_url=obj.getURL(),
                            download_url=self.context.absolute_url() +
                            '/@@download/file/' + annex.filename,
                            filename=annex.filename, sizeKB=annex.getSize() /
                            1024))
                return results
        else:
            if 'adjunts' in self.context.info_firma and self.context.info_firma['adjunts']:
                results = []
                for pos in self.context.info_firma['adjunts']:
                    annex = self.context.info_firma['adjunts'][pos]
                    results.append(
                        dict(
                            title=annex['title'],
                            absolute_url=self.context.absolute_url() +
                            '/viewFile?pos=' + str(pos),
                            download_url=self.context.absolute_url() +
                            '/downloadFile?pos=' + str(pos),
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
