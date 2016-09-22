# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import form
from plone.app.textfield import RichText
from genweb.organs import _
from plone.app.dexterity import PloneMessageFactory as _PMF
from collective import dexteritytextindexer
from plone.app.users.userdataschema import checkEmailAddress
from plone.namedfile.field import NamedBlobImage


class IOrgangovern(form.Schema):
    """ Tipus Organ de Govern
    """

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    """ Dubte: ha de searchable? required? si es fa servir per la URL"""
    dexteritytextindexer.searchable('acronim')
    acronim = schema.TextLine(
        title=_(u'Acronym'),
        required=False
    )

    dexteritytextindexer.searchable('descripcioOrgan')
    descripcioOrgan = RichText(
        title=_(u"Organ Govern description"),
        required=False,
    )

    membresOrgan = RichText(
        title=_(u"Organ Govern members"),
        required=False,
    )

    convidatsPermanentsOrgan = RichText(
        title=_(u"Organ permanently invited people"),
        required=False,
    )

    adrecaLlista = schema.Text(
        title=_(u"mail address"),
        description=_(u"Enter email lists adresses, separated by commas."),
        required=False,
    )

    adrecaAfectatsLlista = schema.Text(
        title=_(u"Stakeholders mail address"),
        description=_(u"Enter email lists adresses, separated by commas."),
        required=False,
    )

    fromMail = schema.TextLine(
        title=_(u'From mail'),
        description=_(u'Enter the from used in the mail form'),
        required=True,
        constraint=checkEmailAddress
    )

    logoOrgan = NamedBlobImage(
        title=_(u"Organ logo"),
        required=False,
    )

    estatsLlista = schema.Text(
        title=_(u"Agreement and document labels"),
        description=_(u"Enter labels, separated by commas."),
        required=False,
    )

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


class View(grok.View):
    grok.context(IOrgangovern)
    grok.template('organgovern_view')
