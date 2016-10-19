# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import form
from plone.directives import dexterity
from genweb.organs import _
from plone.app.dexterity import PloneMessageFactory as _PMF
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from collective import dexteritytextindexer
from genweb.organs import utils
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.supermodel.directives import fieldset


class IActa(form.Schema):
    """ Tipus ACTA: Per a cada Òrgan de Govern es podran crear
        totes les actes que es considerin oportunes
    """
    fieldset('assistents',
             label=_(u'Assistents'),
             fields=['membresConvocats', 'membresConvidats', 'llistaExcusats', 'llistaNoAssistens']
             )

    fieldset('acta',
             label=_(u'Acta'),
             fields=['actaBody', 'footer'],
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
        title=_(u"Attending members"),
        required=False,
    )

    directives.widget(membresConvidats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('membresConvidats')
    membresConvidats = schema.Text(
        title=_(u"Invited members"),
        required=False,
    )

    directives.widget(llistaExcusats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('llistaExcusats')
    llistaExcusats = schema.Text(
        title=_(u"Excused members"),
        required=False,
    )

    directives.widget(llistaNoAssistens=WysiwygFieldWidget)
    dexteritytextindexer.searchable('llistaNoAssistens')
    llistaNoAssistens = schema.Text(
        title=_(u"Missing members"),
        required=False,
    )

    directives.widget(ordreSessio=WysiwygFieldWidget)
    dexteritytextindexer.searchable('ordreSessio')
    ordreSessio = schema.Text(
        title=_(u"Session order"),
        required=False,
    )

    directives.widget(actaBody=WysiwygFieldWidget)
    dexteritytextindexer.searchable('actaBody')
    actaBody = schema.Text(
        title=_(u"Acta Body"),
        required=False,
    )

    directives.widget(footer=WysiwygFieldWidget)
    dexteritytextindexer.searchable('footer')
    footer = schema.Text(
        title=_(u"Footer"),
        required=False,
    )


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


class View(dexterity.DisplayForm):
    grok.context(IActa)
    grok.template('acta_view')

    def isReader(self):
        return utils.isReader(self)


class Edit(dexterity.EditForm):
    """A standard edit form.
    """
    grok.context(IActa)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        # Desactivem el hidden dels camps, sembla que no sigui necessari
        # self.widgets['dataSessio'].mode = HIDDEN_MODE
        # self.widgets['llocConvocatoria'].mode = HIDDEN_MODE
        # self.widgets['horaInici'].mode = HIDDEN_MODE
        # self.widgets['horaFi'].mode = HIDDEN_MODE
