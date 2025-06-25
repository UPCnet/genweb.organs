# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.statusmessages.interfaces import IStatusMessage
from io import StringIO

from plone.app.dexterity import textindexer
from operator import itemgetter
from plone import api
from plone.app.textfield import RichText as RichTextField
from plone.app.users.schema import checkEmailAddress
from plone.autoform import directives
from plone.indexer import indexer
from plone.namedfile.field import NamedBlobImage
from plone.supermodel.directives import fieldset
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.supermodel import model
from z3c.form import form

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.z3cwidget import SelectUsersInputFieldWidget

import csv
import transaction

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


types = SimpleVocabulary(
    [SimpleTerm(value='open_organ', title=_(u'open_organ')),
     SimpleTerm(value='restricted_to_affected_organ', title=_(u'restricted_to_affected_organ')),
     SimpleTerm(value='restricted_to_members_organ', title=_(u'restricted_to_members_organ')),
     ]
)


defaultEstats = _(u"<p>Esborrany Yellow</p><p>Pendent d'aprovació Orange</p><p>Aprovat Green</p><p>No aprovat Red</p><p>Derogat DarkRed</p><p>Informatiu LightSkyBlue</p><p>Informat MediumBlue</p>")


class IOrgangovern(model.Schema):
    """ Organ de Govern
    """

    fieldset('organ',
             label=_(u'Tab organ'),
             fields=['title', 'acronim', 'descripcioOrgan', 'fromMail', 'organType', 'logoOrgan', 'visiblefields', 'eventsColor', 'estatsLlista', 'FAQmembres']
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

    fieldset('gdoc',
             label=_(u'gDOC'),
             fields=['visiblegdoc', 'serie', 'signants', 'author'],
             )

    textindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Organ Title'),
        required=True
    )

    textindexer.searchable('acronim')
    acronim = schema.TextLine(
        title=_(u'Acronym'),
        description=_(u"Acronym Description"),
        required=True
    )

    textindexer.searchable('descripcioOrgan')
    descripcioOrgan = RichTextField(
        title=_(u"Organ Govern description"),
        description=_(u"Organ Govern description help"),
        required=False,
    )

    directives.write_permission(organType='genweb.webmaster')
    organType = schema.Choice(
        title=_(u"Organ Govern type"),
        vocabulary=types,
        default=_(u'open_organ'),
        required=True,
    )

    membresOrgan = RichTextField(
        title=_(u"Organ Govern members"),
        description=_(u"Organ Govern members Description"),
        required=False,
    )

    convidatsPermanentsOrgan = RichTextField(
        title=_(u"Invited members"),
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

    eventsColor = schema.TextLine(
        title=_(u"Color del esdeveniments"),
        description=_(u"Events color help"),
        required=False,
    )

    directives.write_permission(estatsLlista='genweb.organs.add.organs')
    directives.write_permission(estatsLlista='genweb.organs.add.organs')
    estatsLlista = RichTextField(
        title=_(u"Agreement and document labels"),
        description=_(u"Enter labels, separated by commas."),
        default=defaultEstats,
        required=False,
    )

    bodyMailconvoquing = RichTextField(
        title=_(u"Body Mail"),
        description=_(u"Body Mail convoquing description"),
        required=False,
    )

    bodyMailSend = RichTextField(
        title=_(u"Body Mail send"),
        description=_(u"Body Mail send description"),
        required=False,
    )

    footerMail = RichTextField(
        title=_(u"footerMail"),
        description=_(u"footerMail description"),
        required=False,
    )

    textindexer.searchable('footer')
    footer = RichTextField(
        title=_(u"Footer"),
        description=_(u"Footer help"),
        required=False,
    )

    directives.read_permission(visiblefields='genweb.organs.add.organs')
    directives.write_permission(visiblefields='genweb.organs.add.organs')
    visiblefields = schema.Bool(
        title=_(u"Visible fields"),
        description=_(u"Make the sessions and composition members fields visibles to everyone, omitting the security systems."),
        required=False,
    )

    FAQmembres = RichTextField(
        title=_(u"FAQ membres"),
        description=_(u'Preguntes freqüents de membres'),
        required=False,
    )

    visiblegdoc = schema.Bool(
        title=_(u"Activar signat i desat d'actes de les reunions"),
        description=_(u"Al activar aquesta opcio habilita un nou boto per enviar l'acta a signar i desar."),
        required=False,
    )

    serie = schema.TextLine(
        title=_(u"Serie"),
        description=_(u"Identificador utilitzat per saber on es vol pujar la documentació"),
        required=False,
    )

    directives.widget('signants', SelectUsersInputFieldWidget)
    signants = schema.TextLine(
        title=_(u'Signants'),
        description=_(u"Identifica totes les persones que han de signar i en l'ordre en el es tramitarà en  el Portafirmes UPC"),
        required=False,
    )

    author = schema.TextLine(
        title=_(u"Autor"),
        description=_(u"Identificador utilitzat per saber qui es el autor que puja la documentació al gDOC"),
        required=False,
    )


@indexer(IOrgangovern)
def organType(obj):
    return obj.organType


class Edit(form.EditForm):
    """ Organ de govern EDIT form
    """

    def update(self):
        super(Edit, self).update()
        try:
            if self.context.visiblefields:
                folder_title = self.context.aq_parent.aq_parent.title.lower()
                if folder_title in ['centres docents', 'departaments', 'instituts de recerca', 'escola de doctorat']:
                    self.context.visiblefields = False
                    self.context.reindexObject()
                    transaction.commit()
                    IStatusMessage(self.request).addStatusMessage(_(u'Visible fields disabled: In the calendar visible on the public cover, it only shows the planned sessions of certain public governing bodies of the UPC.'), 'info')
        except:
            pass

    def updateWidgets(self):
        super(Edit, self).updateWidgets()


class View(BrowserView):
    """ Organ de govern VIEW form """
    index = ViewPageTemplateFile('templates/organgovern_view.pt')
    def __call__(self):
        return self.index()

    def activeClassMembres(self):
        if self.context.membresOrgan and self.context.convidatsPermanentsOrgan is None:
            return ' active'
        elif self.context.membresOrgan and self.context.convidatsPermanentsOrgan:
            return ' active'
        else:
            return ''

    def activeClassMembresTab(self):
        if self.context.membresOrgan and self.context.convidatsPermanentsOrgan is None:
            return ' show active'
        elif self.context.membresOrgan and self.context.convidatsPermanentsOrgan:
            return ' show active'
        else:
            return ''

    def activeClassConvidats(self):
        if self.context.membresOrgan is None and self.context.convidatsPermanentsOrgan:
            return ' active'
        elif self.context.membresOrgan and self.context.convidatsPermanentsOrgan:
            return ''
        else:
            return ''

    def activeClassConvidatsTab(self):
        if self.context.membresOrgan is None and self.context.convidatsPermanentsOrgan:
            return ' show active'
        elif self.context.membresOrgan and self.context.convidatsPermanentsOrgan:
            return ''
        else:
            return ''

    def hihaPersones(self):
        if self.context.membresOrgan or self.context.convidatsPermanentsOrgan:
            return True
        else:
            return False

    def multipleTab(self):
        if self.context.membresOrgan and self.context.convidatsPermanentsOrgan:
            return True
        else:
            return False

    def SessionsInside(self):
        """ Retorna les sessions internes (sense tenir compte estat)
        """
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.sessio',
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
            num = value.numSessio.zfill(3)
            any = value.start.strftime('%Y%m%d')
            sessionNumber = value.aq_parent.acronim + '/' + value.start.strftime('%Y') + '/' + value.numSessio
            results.append(dict(title=value.title,
                                absolute_url=value.absolute_url(),
                                dataSessio=valuedataSessio,
                                llocConvocatoria=value.llocConvocatoria,
                                horaInici=valueHoraInici,
                                hiddenOrder=int(any + num),
                                sessionNumber=sessionNumber,
                                review_state=obj.review_state))
        return sorted(results, key=itemgetter('hiddenOrder'), reverse=True)

    # def getAcords(self):
    #     """ La llista d'acords i el tab el veu tothom.
    #         Després s'aplica el permís per cada rol a la vista de l'acord """
    #     results = []

    #     portal_catalog = api.portal.get_tool(name='portal_catalog')
    #     folder_path = '/'.join(self.context.getPhysicalPath())

    #     # Només veu els acords de les sessions que pot veure
    #     sessions = portal_catalog.unrestrictedSearchResults(
    #         portal_type='genweb.organs.sessio',
    #         sort_on='getObjPositionInParent',
    #         path={'query': folder_path,
    #               'depth': 1})

    #     paths = []
    #     if api.user.is_anonymous():
    #         username = None
    #     else:
    #         username = api.user.get_current().id

    #     organ_type = self.context.organType
    #     for session in sessions:
    #         paths.append(session.getPath())

    #     for path in paths:
    #         values = portal_catalog.unrestrictedSearchResults(
    #             portal_type=['genweb.organs.acord'],
    #             sort_on='modified',
    #             path={'query': path,
    #                   'depth': 3})

    #         for obj in values:
    #             value = obj.getObject()
    #             if value.agreement:
    #                 if len(value.agreement.split('/')) > 2:
    #                     try:
    #                         num = value.agreement.split('/')[1].zfill(3) + value.agreement.split('/')[2].zfill(3) + value.agreement.split('/')[3].zfill(3)
    #                     except:
    #                         num = value.agreement.split('/')[1].zfill(3) + value.agreement.split('/')[2].zfill(3)
    #                     any = value.agreement.split('/')[0]
    #                 else:
    #                     num = value.agreement.split('/')[0].zfill(3)
    #                     any = value.agreement.split('/')[1]
    #             else:
    #                 num = ''
    #                 any = ''
    #             if value.aq_parent.aq_parent.portal_type == 'genweb.organs.sessio':
    #                 wf_state = api.content.get_state(obj=value.aq_parent.aq_parent)
    #                 if username:
    #                     roles = api.user.get_roles(username=username, obj=value.aq_parent.aq_parent)
    #                 else:
    #                     roles = []
    #             else:
    #                 wf_state = api.content.get_state(obj=value.aq_parent)
    #                 if username:
    #                     roles = api.user.get_roles(username=username, obj=value.aq_parent)
    #                 else:
    #                     roles = []
    #             # Oculta acords from table depending on role and state
    #             add_acord = False
    #             if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles:
    #                 add_acord = True
    #             elif 'OG3-Membre' in roles:
    #                 if 'planificada' not in wf_state:
    #                     add_acord = True
    #             elif 'OG4-Afectat' in roles:
    #                 if organ_type == 'open_organ' or organ_type == 'restricted_to_affected_organ':
    #                     if 'realitzada' in wf_state or 'tancada' in wf_state or 'en_correccio' in wf_state:
    #                         add_acord = True
    #             else:
    #                 if 'tancada' in wf_state or 'en_correccio' in wf_state:
    #                     add_acord = True

    #             if add_acord:
    #                 results.append(dict(title=value.title,
    #                                     absolute_url=value.absolute_url(),
    #                                     agreement=value.agreement,
    #                                     hiddenOrder=any + num,
    #                                     estatsLlista=value.estatsLlista,
    #                                     color=utils.getColor(obj)))

    #     return sorted(results, key=itemgetter('hiddenOrder'), reverse=True)

    # def getActes(self):
    #     """ Si es Manager/Secretari/Editor/Membre show actas
    #         Affectat i altres NO veuen MAI les ACTES """
    #     roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
    #     if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
    #         results = []
    #         portal_catalog = api.portal.get_tool(name='portal_catalog')
    #         folder_path = '/'.join(self.context.getPhysicalPath())

    #         sessions = portal_catalog.searchResults(
    #             portal_type='genweb.organs.sessio',
    #             sort_on='getObjPositionInParent',
    #             path={'query': folder_path,
    #                   'depth': 1})

    #         paths = []
    #         for session in sessions:
    #             paths.append(session.getPath())

    #         for path in paths:
    #             values = portal_catalog.searchResults(
    #                 portal_type=['genweb.organs.acta'],
    #                 sort_on='modified',
    #                 path={'query': path,
    #                       'depth': 3})

    #             for obj in values:
    #                 value = obj.getObject()
    #                 results.append(dict(title=value.title,
    #                                     absolute_url=value.absolute_url(),
    #                                     data=value.horaInici.strftime('%d/%m/%Y'),
    #                                     hiddenOrder=value.horaInici.strftime('%Y%m%d')))
    #         return sorted(results, key=itemgetter('hiddenOrder'), reverse=True)
    #     else:
    #         return None

    def viewActes(self):
        """ Si es Manager/Secretari/Editor/Membre show actas
            Affectat i altres NO veuen MAI les ACTES """
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        else:
            return False

    def getFAQs(self):
        if self.canViewFAQs():
            try:
                faqm = self.context.FAQmembres.raw
            except:
                faqm = ""

            return faqm
        return None

    def canViewFAQs(self):
        if not api.user.is_anonymous():
            user = api.user.get_current()
            userPermissions = api.user.get_roles(user=user, obj=self)
            for permission in ['Manager', 'WebMaster', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat']:
                if permission in userPermissions:
                    return True
        return False

    def canView(self):
        # Permissions to view ORGANS DE GOVERN
        # Bypass if manager
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        organType = self.context.organType

        # If Obert
        if organType == 'open_organ':
            return True
        # if restricted_to_members_organ
        elif organType == 'restricted_to_members_organ':
            if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized
        # if restricted_to_affected_organ
        elif organType == 'restricted_to_affected_organ':
            if utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized
        else:
            raise Unauthorized

    def canModify(self):
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        return utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)

    def viewOrdena(self):
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        return utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)

    def viewExportAcords(self):
        # Només els Secretaris i Editors poden veure les excuses
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        return utils.checkhasRol(['Manager', 'OG1-Secretari'], roles)


class exportActas(BrowserView):
    # Registrar en ZCML: name='exportAcordsCSV', for='genweb.organs.content.organgovern.IOrgangovern', permission='cmf.ManagePortal'
    data_header_columns = [
        "Titol",
        "NumAcord",
        "Estats",
        "Contingut",
        "Fitxers"]

    def render(self):
        output_file = StringIO()
        # Write the BOM of the text stream to make its charset explicit
        output_file.write(u'\ufeff'.encode('utf8'))
        self.write_data(output_file)

        header_content_type = 'text/csv'
        header_filename = 'llista_acords_' + self.context.id + '.csv'
        self.request.response.setHeader('Content-Type', header_content_type)
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="{0}"'.format(header_filename))
        return output_file.getvalue()

    def listAcords(self):
        # If acords in site, publish the tab and the contents...
        results = []

        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())

        # Només veu els acords de les sessions que pot veure
        sessions = portal_catalog.unrestrictedSearchResults(
            portal_type='genweb.organs.sessio',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        paths = []
        if api.user.is_anonymous():
            username = None
        else:
            username = api.user.get_current().id

        organ_type = self.context.organType
        for session in sessions:
            paths.append(session.getPath())

        for path in paths:
            values = portal_catalog.unrestrictedSearchResults(
                portal_type=['genweb.organs.acord'],
                sort_on='modified',
                path={'query': path,
                      'depth': 3})
            for obj in values:
                # value = obj.getObject()
                value = obj._unrestrictedGetObject()
                if value.agreement:
                    if len(value.agreement.split('/')) > 2:
                        try:
                            num = value.agreement.split('/')[1].zfill(3) + value.agreement.split('/')[2].zfill(3) + value.agreement.split('/')[3].zfill(3)
                        except:
                            num = value.agreement.split('/')[1].zfill(3) + value.agreement.split('/')[2].zfill(3)
                        any = value.agreement.split('/')[0]
                    else:
                        num = value.agreement.split('/')[0].zfill(3)
                        any = value.agreement.split('/')[1]
                else:
                    num = any = ''

                sons_string = ""
                for son in value.getChildNodes():
                    sons_string += "- " + son.Title() + "\n"

                results.append(dict(title=value.title,
                                    absolute_url=value.absolute_url(),
                                    agreement=value.agreement,
                                    hiddenOrder=any + num,
                                    estatsLlista=value.estatsLlista,
                                    contingut=value.defaultContent,
                                    sons=sons_string))

        return sorted(results, key=itemgetter('hiddenOrder'), reverse=True)

    def write_data(self, output_file):
        writer = csv.writer(output_file, dialect='excel', delimiter=',')
        writer.writerow(self.data_header_columns)

        for acord in self.listAcords():

            try:
                title = acord['title'].encode('utf-8')
            except:
                title = acord['title']

            if acord['contingut']:
                acord['contingut'] = unicode(acord['contingut']).encode('utf-8')

            writer.writerow([title,
                             acord['agreement'],
                             acord['estatsLlista'].encode('utf-8'),
                             acord['contingut'],
                             acord['sons']
            ])
