# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import form
from plone.directives import dexterity
from genweb.organs import _
from plone.app.dexterity import PloneMessageFactory as _PMF
from collective import dexteritytextindexer
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.supermodel.directives import fieldset
from plone.namedfile.field import NamedBlobImage
from Products.CMFCore.utils import getToolByName

grok.templatedir("templates")


class IActa(form.Schema):
    fieldset('assistents',
             label=_(u'Assistents'),
             fields=['membresConvocats', 'membresConvidats', 'llistaExcusats', 'llistaNoAssistens']
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    dataSessio = schema.Date(
        title=_(u"Session date"),
        required=True,
    )

    llocConvocatoria = schema.TextLine(
        title=_(u"Session location"),
        required=False,
    )

    horaInici = schema.Time(
        title=_(u"Session start time"),
        required=False,
    )

    horaFi = schema.Time(
        title=_(u"Session end time"),
        required=False,
    )

    directives.widget(membresConvocats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('membresConvocats')
    membresConvocats = schema.Text(
        title=_(u"Incoming members list"),
        description=_(u"Incoming members list help"),
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

    actaLogo = NamedBlobImage(
        title=_(u"Imatge de les actes"),
        description=_(u"Imatge que es fa servir en imprimir les actes, en comptes de fer servir la imatge definida a l'òrgan."),
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
    return data.context.membresConvocats


@form.default_value(field=IActa['llistaExcusats'])
def llistaExcusatsDefaultValue(data):
    # copy llistaExcusats from Session (parent object)
    return data.context.llistaExcusats


@form.default_value(field=IActa['llistaNoAssistens'])
def llistaNoAssistensDefaultValue(data):
    # copy noAssistents from Session (parent object)
    return data.context.noAssistents


# Hidden field used only to render and generate the PDF
@form.default_value(field=IActa['dataSessio'])
def dataSessioDefaultValue(data):
    # copy dataSessio from Session (parent object)
    return data.context.dataSessio


# Hidden field used only to render and generate the PDF
@form.default_value(field=IActa['llocConvocatoria'])
def llocConvocatoriaDefaultValue(data):
    # copy llocConvocatoria from Session (parent object)
    return data.context.llocConvocatoria


# Hidden field used only to render and generate the PDF
@form.default_value(field=IActa['horaInici'])
def horaIniciDefaultValue(data):
    # copy horaInici from Session (parent object)
    return data.context.horaInici


# Hidden field used only to render and generate the PDF
@form.default_value(field=IActa['horaFi'])
def horaFiDefaultValue(data):
    # copy horaFi from Session (parent object)
    return data.context.horaFi


@form.default_value(field=IActa['ordenDelDia'])
def ordenDelDiaDefaultValue(data):
    # Copy all Punts from Session to Acta
    return Punts2Acta(data)


def Punts2Acta(self):
    """ Retorna els punt en format text per mostrar a l'ordre
        del dia de les actes
    """
    portal_catalog = getToolByName(self.context, 'portal_catalog')
    folder_path = '/'.join(self.context.getPhysicalPath())
    values = portal_catalog.searchResults(
        portal_type='genweb.organs.punt',
        sort_on='getObjPositionInParent',
        path={'query': folder_path,
              'depth': 1})

    results = []
    for obj in values:
        # value = obj.getObject()
        value = obj._unrestrictedGetObject()
        if value.proposalPoint:
            number = str(value.proposalPoint) + '.- '
        else:
            number = ''
        results.append(number + str(obj.Title))
        if len(value.objectIds()) > 0:
            valuesInside = portal_catalog.searchResults(
                portal_type='genweb.organs.subpunt',
                sort_on='getObjPositionInParent',
                path={'query': obj.getPath(),
                      'depth': 1})
            for item in valuesInside:
                subpunt = item.getObject()
                if subpunt.proposalPoint:
                    numberSubpunt = str(subpunt.proposalPoint) + '.- '
                else:
                    numberSubpunt = ''
                results.append('&nbsp;&nbsp;' + numberSubpunt + str(item.Title))

    return '<br/>'.join(results)


class View(dexterity.DisplayForm):
    grok.context(IActa)
    grok.template('acta_view')

    def horaFi(self):
        if self.context.horaFi:
            return self.context.horaFi.strftime('%H:%M')
        else:
            return ''

    def horaInici(self):
        if self.context.horaInici:
            return self.context.horaInici.strftime('%H:%M')
        else:
            return ''

    def dataSessio(self):
        if self.context.dataSessio:
            return self.context.dataSessio.strftime('%d/%m/%Y')
        else:
            return ''


class Edit(dexterity.EditForm):
    """A standard edit form.
    """
    grok.context(IActa)
