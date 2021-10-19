# -*- coding: utf-8 -*-
from AccessControl import Unauthorized

from collective import dexteritytextindexer
from five import grok
from plone import api
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from plone.directives import dexterity
from plone.directives import form
from plone.event.interfaces import IEventAccessor
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.utils import get_contenttype
from plone.supermodel.directives import fieldset
from zope import schema
from zope.schema import ValidationError

from genweb.organs import _
from genweb.organs import utils

grok.templatedir("templates")


class IActa(form.Schema):
    """ ACTA """

    fieldset('acta',
             label=_(u'Tab acta'),
             fields=['title', 'horaInici', 'horaFi', 'llocConvocatoria',
                     'ordenDelDia', 'enllacVideo']
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
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self) or utils.isConvidat(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self) or utils.isConvidat(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self) or utils.isConvidat(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self) or utils.isConvidat(self)):
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

    def AudioInside(self):
        """ Retorna els fitxers d'audio creats aquí dintre (sense tenir compte estat)
        """
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
                results.append(dict(title=obj.Title,
                                    absolute_url=obj.getURL(),
                                    audio=obj.getObject().file))
            return results
        else:
            return False

    def AnnexInside(self):
        """ Retorna els fitxers annexos creats aquí dintre (sense tenir compte estat)
        """
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
                results.append(dict(title=obj.Title,
                                    absolute_url=obj.getURL(),
                                    file=obj.getObject().file))
            return results
        else:
            return False


class Edit(dexterity.EditForm):
    """A standard edit form.
    """
    grok.context(IActa)
