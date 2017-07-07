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
from operator import itemgetter


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

    fieldset('organ',
             label=_(u'Tab organ'),
             fields=['title', 'acronim', 'descripcioOrgan', 'fromMail', 'tipus', 'logoOrgan', 'estatsLlista']
             )

    fieldset('assistents',
             label=_(u'Assistents'),
             fields=['membresOrgan', 'convidatsPermanentsOrgan', 'adrecaLlista']
             )

    fieldset('afectats',
             label=_(u'Afectats'),
             fields=['adrecaAfectatsLlista'],
             )

    fieldset('plantilles',
             label=_(u'Plantilles'),
             fields=['bodyMailconvoquing', 'bodyMailSend', 'footerMail', 'footer'],
             )

    dexterity.write_permission(title='genweb.webmaster')
    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Organ Title'),
        required=True
    )

    dexterity.write_permission(acronim='genweb.webmaster')
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

    # TODO: Enable this quan es facin la resta d'organs (restricted, etc...)
    directives.omitted('tipus')
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

    dexterity.write_permission(estatsLlista='genweb.webmaster')
    directives.widget(estatsLlista=WysiwygFieldWidget)
    estatsLlista = schema.Text(
        title=_(u"Agreement and document labels"),
        description=_(u"Enter labels, separated by commas."),
        default=defaultEstats,
        required=False,
    )

    directives.widget(bodyMailconvoquing=WysiwygFieldWidget)
    bodyMailconvoquing = schema.Text(
        title=_(u"Body Mail"),
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


class View(grok.View):
    grok.context(IOrgangovern)
    grok.template('organgovern_view')

    def selectedOrganType(self):
        return self.context.estatsLlista

    def members(self):
        # If no members, hide the tab
        if self.context.membresOrgan is None and self.context.convidatsPermanentsOrgan is None:
            return False
        return True

    def activeClassMembres(self):
        if self.context.membresOrgan and self.context.convidatsPermanentsOrgan is None:
            return 'in active'
        elif self.context.membresOrgan and self.context.convidatsPermanentsOrgan:
            return 'in active'
        else:
            return ''

    def activeClassConvidats(self):
        if self.context.membresOrgan is None and self.context.convidatsPermanentsOrgan:
            return 'in active'
        elif self.context.membresOrgan and self.context.convidatsPermanentsOrgan:
            return ''
        else:
            return ''

    def SessionsInside(self):
        """ Retorna les sessions internes (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.sessio',
            sort_on='getObjPositionInParent',
            sort_order='reverse',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            # value = obj.getObject()
            value = obj._unrestrictedGetObject()
            if obj.start:
                valuedataSessio = obj.start.strftime('%d/%m/%Y')
                valueHoraInici = obj.start.strftime('%H:%M')
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
        results = []
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())

        sessions = portal_catalog.searchResults(
            portal_type='genweb.organs.sessio',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        paths = []
        for session in sessions:
            paths.append(session.getPath())

        for path in paths:
            values = portal_catalog.searchResults(
                portal_type=['genweb.organs.acord'],
                sort_on='modified',
                sort_order='reverse',
                path={'query': path,
                      'depth': 3})

            for obj in values:
                value = obj.getObject()
                # value = obj._unrestrictedGetObject()
                num = value.agreement.split('/')[0].zfill(3)
                any = value.agreement.split('/')[1].zfill(3)
                results.append(dict(title=value.title,
                                    absolute_url=value.absolute_url(),
                                    agreement=value.agreement,
                                    hiddenOrder=any + num,
                                    estatsLlista=value.estatsLlista))
        return sorted(results, key=itemgetter('hiddenOrder'))
