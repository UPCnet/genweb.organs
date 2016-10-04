# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedFile
from plone.formwidget.multifile import MultiFileFieldWidget
from plone.directives import dexterity
from genweb.organs import _
from plone.app.dexterity import PloneMessageFactory as _PMF
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from collective import dexteritytextindexer
from genweb.organs import utils


class IActa(form.Schema):
    """ Tipus Sessio: Per a cada Òrgan de Govern es podran crear
        totes les sessions que es considerin oportunes
    """
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
        title=_(u"Session place"),
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

    dexteritytextindexer.searchable('membresConvocats')
    membresConvocats = RichText(
        title=_(u"Attending members"),
        required=False,
    )

    dexteritytextindexer.searchable('membresConvidats')
    membresConvidats = RichText(
        title=_(u"Invited members"),
        required=False,
    )

    dexteritytextindexer.searchable('llistaExcusats')
    llistaExcusats = RichText(
        title=_(u"Excused members"),
        required=False,
    )

    dexteritytextindexer.searchable('llistaNoAssistens')
    llistaNoAssistens = RichText(
        title=_(u"Missing members"),
        required=False,
    )

    dexteritytextindexer.searchable('ordreSessio')
    ordreSessio = RichText(
        title=_(u"Session order"),
        required=False,
    )

    dexteritytextindexer.searchable('actaBody')
    actaBody = RichText(
        title=_(u"Acta Body"),
        required=False,
    )

    dexteritytextindexer.searchable('footer')
    footer = RichText(
        title=_(u"Footer"),
        required=False,
    )

    dexteritytextindexer.searchable('OriginalFiles')
    form.widget(OriginalFiles=MultiFileFieldWidget)
    OriginalFiles = schema.List(title=_(u"Files"),
                                description=_(u"Attached files description"),
                                value_type=NamedFile(),
                                required=False,)


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


@form.default_value(field=IActa['actaBody'])
def actaBodyDefaultValue(data):
    # copy ordreSessio from Session in Acta
    return data.context.ordreSessio


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
