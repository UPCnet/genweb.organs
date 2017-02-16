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
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from genweb.organs import utils

organType = SimpleVocabulary(
    [SimpleTerm(value='Open', title=_(u'Open')),
     SimpleTerm(value='Restricted_to_Members', title=_(u'Restricted_to_Members')),
     SimpleTerm(value='Restricted_to_Affected', title=_(u'Restricted_to_Affected')),
     ]
)

grok.templatedir("templates")

defaultEstats = _(u"<p>Esborrany Yellow</p><p>Pendent d'aprovació Orange</p><p>Aprovat Green</p><p>No aprovat Red</p><p>Derogat DarkRed</p><p>Informatiu LightSkyBlue</p><p>Informat MediumBlue</p>")


class IOrgangovern(form.Schema):
    """ Tipus Organ de Govern
    """

    fieldset('assistents',
             label=_(u'Assistents'),
             fields=['membresOrgan', 'convidatsPermanentsOrgan']
             )

    fieldset('notificacions',
             label=_(u'Notifications'),
             fields=['adrecaAfectatsLlista', 'bodyMailconvoquing', 'bodyMailSend', 'footerMail', 'footer'],
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Organ Title'),
        required=True
    )

    # TODO: When create the WS, activate this value
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
        description=_(u"Organ Govern description help"),
        required=False,
    )

    directives.mode(tipus='hidden')
    tipus = schema.Choice(
        title=_(u"Organ Govern type"),
        vocabulary=organType,
        default=_(u'Open'),
        required=False,
    )

    directives.widget(membresOrgan=WysiwygFieldWidget)
    membresOrgan = schema.Text(
        title=_(u"Organ Govern members"),
        description=_(u"Organ Govern members Description"),
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

    adrecaLlista = schema.TextLine(
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

    directives.widget(footer=WysiwygFieldWidget)
    dexteritytextindexer.searchable('footer')
    footer = schema.Text(
        title=_(u"Footer"),
        description=_(u"Footer help"),
        required=False,
    )


class Edit(dexterity.EditForm):
    """A standard edit form.
    """
    grok.context(IOrgangovern)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets['tipus'].mode = HIDDEN_MODE


class View(grok.View):
    grok.context(IOrgangovern)
    grok.template('organgovern_view')

    def selectedOrganType(self):
        value = self.context.estatsLlista
        return value

    def members(self):
        # If no members, hide the tab
        if self.context.membresOrgan is None and self.context.convidatsPermanentsOrgan is None:
            return False
        return True

    def checkRoles(self):
        return utils.checkRoles(self)

    def SessionsInside(self):
        """ Retorna les sessions internes (sense tenir compte estat)
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
            if value.start:
                valuedataSessio = value.start.strftime('%d/%m/%Y')
                valueHoraInici = value.start.strftime('%H:%M')
            else:
                valuedataSessio = ''
                valueHoraInici = ''

            results.append(dict(title=value.title,
                                absolute_url=value.absolute_url(),
                                dataSessio=valuedataSessio,
                                llocConvocatoria=value.llocConvocatoria,
                                horaInici=valueHoraInici,
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
