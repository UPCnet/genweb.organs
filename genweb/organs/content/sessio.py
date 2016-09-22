# -*- coding: utf-8 -*-
import datetime
from five import grok
from zope import schema
from plone import api
import re
from plone.indexer import indexer
from plone.directives import dexterity
from plone.directives import form
from plone.app.textfield import RichText
from zope.annotation.interfaces import IAnnotations
from genweb.organs import _
from plone.app.dexterity import PloneMessageFactory as _PMF
from collective import dexteritytextindexer
from Products.CMFCore.utils import getToolByName
from datetime import date


class InvalidEmailError(schema.ValidationError):
    __doc__ = u'Please enter a valid e-mail address.'


class ISessio(form.Schema):
    """ Tipus Sessio: Per a cada Òrgan de Govern es podran crear
        totes les sessions que es considerin oportunes
    """

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    ''' str(date.today().year) '''
    anySessio = schema.TextLine(
        title=_(u"Session year"),
        required=True
    )

    numSessio = schema.TextLine(
        title=_(u"Session number"),
        required=True,
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

    adrecaLlista = schema.Text(
        title=_(u"mail address"),
        description=_(u"Enter email lists adresses, separated by commas."),
        required=True,
    )

    adrecaAfectatsLlista = schema.Text(
        title=_(u"Stakeholders mail address"),
        description=_(u"Enter email lists adresses, separated by commas."),
        required=False,
    )

    dexteritytextindexer.searchable('membresConvocats')
    membresConvocats = RichText(
        title=_(u"Incoming members list"),
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

    ''' Eliminar
    dexteritytextindexer.searchable('ordreSessio')
    ordreSessio = RichText(
        title=_(u"Session order"),
        required=False,
    )
     '''

    dexteritytextindexer.searchable('bodyMail')
    bodyMail = RichText(
        title=_(u"Body Mail"),
        description=_(u"Body Mail description"),
        required=False,
    )

    dexteritytextindexer.searchable('signatura')
    signatura = RichText(
        title=_(u"Signatura"),
        description=_(u"Signatura description"),
        required=False,
    )

    '''Camps per enllaçar àudio i vídeo'''
    enllacVideo = schema.TextLine(
        title=_(u"Video link"),
        required=False,
    )

    enllacAudio = schema.TextLine(
        title=_(u"Audio link"),
        required=False,
    )

@form.default_value(field=ISessio['anySessio'])
def anySessioDefaultValue(data):
    return datetime.datetime.today().year


@form.default_value(field=ISessio['numSessio'])
def numSessioDefaultValue(data):
    return 666


@form.default_value(field=ISessio['dataSessio'])
def dataSessioDefaultValue(data):
    return datetime.datetime.today()


@form.default_value(field=ISessio['horaInici'])
def horaIniciDefaultValue(data):
    time = datetime.datetime.today()
    return time


@form.default_value(field=ISessio['horaFi'])
def horaFiDefaultValue(data):
    time = datetime.datetime.today() + datetime.timedelta(hours=1)
    return time


@form.default_value(field=ISessio['membresConvocats'])
def membresConvocatsDefaultValue(data):
    # copy members from Organ de Govern (parent object)
    return data.context.membresOrgan


@form.default_value(field=ISessio['adrecaLlista'])
def adrecaLlistaDefaultValue(data):
    # copy adrecaLlista from Organ de Govern (parent object)
    return data.context.adrecaLlista


@form.default_value(field=ISessio['adrecaAfectatsLlista'])
def adrecaAfectatsLlistaDefaultValue(data):
    # copy adrecaLlista from Organ de Govern (parent object)
    return data.context.adrecaAfectatsLlista


class View(grok.View):
    grok.context(ISessio)
    grok.template('sessio_view')


class Edit(dexterity.EditForm):
    """A standard edit form.
    """
    grok.context(ISessio)
