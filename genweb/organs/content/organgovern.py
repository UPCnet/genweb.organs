# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import form
from plone.app.textfield import RichText
from genweb.organs import _
from collective import dexteritytextindexer
from plone.app.users.userdataschema import checkEmailAddress
from plone.namedfile.field import NamedBlobImage
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

organType = SimpleVocabulary(
    [SimpleTerm(value='Open', title=_(u'Open to everybody')),
     SimpleTerm(value='Members', title=_(u'Restricted to Members')),
     SimpleTerm(value='Affected', title=_(u'Restricted to Affected')),
     ]
)


class IOrgangovern(form.Schema):
    """ Tipus Organ de Govern
    """

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Title'),
        required=True
    )

    dexteritytextindexer.searchable('acronim')
    acronim = schema.TextLine(
        title=_(u'Acronym'),
        description=_(u"Acronym Description"),
        required=False
    )

    dexteritytextindexer.searchable('descripcioOrgan')
    descripcioOrgan = RichText(
        title=_(u"Organ Govern description"),
        required=False,
    )

    tipus = schema.Choice(
        title=_(u"Organ Govern type"),
        vocabulary=organType,
        default=_(u'Open'),
        required=True,
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
        description=_(u'Logo description'),
        required=False,
    )

    estatsLlista = schema.Text(
        title=_(u"Agreement and document labels"),
        description=_(u"Enter labels, separated by commas."),
        required=False,
    )

    bodyMailconvoquing = RichText(
        title=_(u"Body Mail convoquing"),
        description=_(u"Body Mail convoquing description"),
        required=False,
    )

    bodyMailSend = RichText(
        title=_(u"Body Mail send"),
        description=_(u"Body Mail send description"),
        required=False,
    )

    footerMail = RichText(
        title=_(u"footerMail"),
        description=_(u"footerMail description"),
        required=False,
    )


class View(grok.View):
    grok.context(IOrgangovern)
    grok.template('organgovern_view')
