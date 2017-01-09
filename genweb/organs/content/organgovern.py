# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import form
from genweb.organs import _
from collective import dexteritytextindexer
from plone.app.users.userdataschema import checkEmailAddress
from plone.namedfile.field import NamedBlobImage
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.CMFCore.utils import getToolByName
from plone.autoform import directives
from plone.supermodel.directives import fieldset
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.directives import dexterity

organType = SimpleVocabulary(
    [SimpleTerm(value='Open', title=_(u'Open')),
     SimpleTerm(value='Restricted_to_Members', title=_(u'Restricted_to_Members')),
     SimpleTerm(value='Restricted_to_Affected', title=_(u'Restricted_to_Affected')),
     ]
)

grok.templatedir("templates")

defaultEstats = _(u"Esborrany green <br/>Pendent d'aprovació grey <br/>Aprovat blue <br/>Informat brown <br/>No aprovat red <br/>Derogat blueviolet <br/>Informatiu chocolate")


class IOrgangovern(form.Schema):
    """ Tipus Organ de Govern
    """

    fieldset('assistents',
             label=_(u'Assistents'),
             fields=['membresOrgan', 'convidatsPermanentsOrgan']
             )

    fieldset('notificacions',
             label=_(u'Notifications'),
             fields=['adrecaAfectatsLlista', 'bodyMailconvoquing', 'bodyMailSend', 'footerMail'],
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Organ Title'),
        required=True
    )

    dexteritytextindexer.searchable('acronim')
    acronim = schema.TextLine(
        title=_(u'Acronym'),
        description=_(u"Acronym Description"),
        required=False
    )

    dexteritytextindexer.searchable('descripcioOrgan')
    directives.widget(descripcioOrgan=WysiwygFieldWidget)
    descripcioOrgan = schema.Text(
        title=_(u"Organ Govern description"),
        required=False,
    )

    tipus = schema.Choice(
        title=_(u"Organ Govern type"),
        vocabulary=organType,
        required=True,
    )

    directives.widget(membresOrgan=WysiwygFieldWidget)
    membresOrgan = schema.Text(
        title=_(u"Organ Govern members"),
        required=False,
    )

    directives.widget(convidatsPermanentsOrgan=WysiwygFieldWidget)
    convidatsPermanentsOrgan = schema.Text(
        title=_(u"Organ permanently invited people"),
        description=_(u"Organ permanently invited people description."),
        required=False,
    )

    fromMail = schema.TextLine(
        title=_(u'From mail'),
        description=_(u'Enter the from used in the mail form'),
        required=True,
        constraint=checkEmailAddress
    )

    adrecaLlista = schema.Text(
        title=_(u"mail address"),
        description=_(u"Mail address help"),
        required=True,
    )

    adrecaAfectatsLlista = schema.Text(
        title=_(u"Stakeholders mail address"),
        description=_(u"Stakeholders mail address help."),
        required=False,
    )

    logoOrgan = NamedBlobImage(
        title=_(u"Organ logo"),
        description=_(u'Logo description'),
        required=False,
    )

    directives.widget(estatsLlista=WysiwygFieldWidget)
    estatsLlista = schema.Text(
        title=_(u"Agreement and document labels"),
        description=_(u"Enter labels, separated by commas."),
        default=defaultEstats,
        required=False,
    )

    directives.widget(bodyMailconvoquing=WysiwygFieldWidget)
    bodyMailconvoquing = schema.Text(
        title=_(u"Body Mail convoquing"),
        description=_(u"Body Mail convoquing description"),
        required=False,
    )

    directives.widget(bodyMailSend=WysiwygFieldWidget)
    bodyMailSend = schema.Text(
        title=_(u"Body Mail send"),
        description=_(u"Body Mail send description"),
        required=False,
    )

    directives.widget(footerMail=WysiwygFieldWidget)
    footerMail = schema.Text(
        title=_(u"footerMail"),
        description=_(u"footerMail description"),
        required=False,
    )


class Edit(dexterity.EditForm):
    """A standard edit form.
    """
    grok.context(IOrgangovern)


class View(grok.View):
    grok.context(IOrgangovern)
    grok.template('organgovern_view')

    def selectedOrganType(self):
        value = self.context.estatsLlista
        return value

    def nomembers(self):
        # If no members, hide the tab
        if self.context.membresOrgan is None and self.context.convidatsPermanentsOrgan is None:
            return False
        return True

    def SessionsInside(self):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.sessio',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            # value = obj.getObject()
            value = obj._unrestrictedGetObject()
            results.append(dict(title=value.title,
                                absolute_url=value.absolute_url(),
                                dataSessio=value.dataSessio.strftime('%d/%m/%Y'),
                                llocConvocatoria=value.llocConvocatoria,
                                horaInici=value.horaInici.strftime('%H:%M'),
                                review_state=obj.review_state))
        return results

    def getAcords(self):
        # If acords in site, publish the tab and the contents...
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.subpunt'],
            sort_on='modified',
            sort_order='reverse',
            acordOrgan=True,
            path={'query': folder_path,
                  'depth': 3})
        results = []

        for obj in values:
            # value = obj.getObject()
            value = obj._unrestrictedGetObject()
            if obj.portal_type == "genweb.organs.punt":
                organTitle = value.aq_parent.Title()
            elif obj.portal_type == "genweb.organs.subpunt":
                organTitle = value.aq_parent.aq_parent.Title()
            else:
                organTitle = ''

            results.append(dict(title=value.title,
                                title_organ=organTitle,
                                absolute_url=value.absolute_url(),
                                proposalPoint=value.proposalPoint,
                                agreement=value.agreement,
                                estatsLlista=value.estatsLlista))
        return results
