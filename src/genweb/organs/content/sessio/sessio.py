# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from io import StringIO

from plone.app.dexterity import textindexer
from operator import itemgetter
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.autoform import directives
from z3c.form import form
from plone.event.interfaces import IEventAccessor
from plone.supermodel.directives import fieldset
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import HIDDEN_MODE  # INPUT_MODE
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.i18n import translate
from zope.interface import Invalid
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from plone.supermodel import model
from plone.supermodel import directives as model_directives
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.interface import provider
from plone.app.textfield import RichText as RichTextField

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental.utils import hasFirmaActa, estatFirmaActa

import ast
import csv
import datetime
import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


sessionModalities = SimpleVocabulary(
    [SimpleTerm(value=u'attended', title=_(u'attended')),
     SimpleTerm(value=u'mixed', title=_(u'mixed')),
     SimpleTerm(value=u'distance', title=_(u'distance')),
     SimpleTerm(value=u'asynchronous', title=_(u'asynchronous'))]
)


def is_numeric(value):
    if not value.isdigit():
        raise Invalid(_(u'El valor ha de ser numèric.'))
    return True


@provider(IContextAwareDefaultFactory)
def numSessio(context):
    sessions = api.content.find(
        portal_type='genweb.organs.sessio',
        context=context)
    total = 0
    year = datetime.datetime.today().strftime('%Y')
    for session in sessions:
        if session.getObject().start.strftime('%Y') == year:
            total = total + 1
    return '{0}'.format(str(total + 1).zfill(2))


@provider(IContextAwareDefaultFactory)
def numSessioShowOnly(context):
    sessions = api.content.find(
        portal_type='genweb.organs.sessio',
        context=context)
    total = 0
    year = datetime.datetime.today().strftime('%Y')
    for session in sessions:
        if session.getObject().start.strftime('%Y') == year:
            total = total + 1
    return '{0}'.format(str(total + 1).zfill(2))


@provider(IContextAwareDefaultFactory)
def bodyMail(context):
    if hasattr(context, 'bodyMailconvoquing') and getattr(context.bodyMailconvoquing, 'raw', None):
        return context.bodyMailconvoquing.raw
    return getattr(context, 'bodyMailconvoquing', '')


@provider(IContextAwareDefaultFactory)
def signatura(context):
    if hasattr(context, 'footerMail') and getattr(context.footerMail, 'raw', None):
        return context.footerMail.raw
    return getattr(context, 'footerMail', '')


class ISessio(model.Schema):
    """ Sessio
    """

    fieldset('assistents',
             label=_(u'Assistents'),
             fields=['infoAssistents' ,'membresConvocats', 'membresConvidats', 'llistaExcusats', 'assistents', 'noAssistents', 'adrecaLlista']
             )

    fieldset('afectats',
             label=_(u'Afectats'),
             fields=['infoAfectats' ,'adrecaAfectatsLlista'],
             )

    fieldset('plantilles',
             label=_(u'Plantilles'),
             fields=['bodyMail', 'signatura'],
             )

    textindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Session Title'),
        required=True,
    )

    directives.mode(IAddForm, numSessioShowOnly='display')
    directives.mode(IEditForm, numSessioShowOnly='hidden')
    numSessioShowOnly = schema.TextLine(
        title=_(u"Session number"),
        required=False,
        defaultFactory=numSessioShowOnly
    )

    directives.mode(IAddForm, numSessio='hidden')
    numSessio = schema.TextLine(
        title=_(u"Session number"),
        required=True,
        constraint=is_numeric,
        defaultFactory=numSessio
    )

    llocConvocatoria = schema.TextLine(
        title=_(u"Session location"),
        required=False,
    )

    linkSala = schema.TextLine(
        title=_(u"Enllac a la sala"),
        required=False,
    )

    modality = schema.Choice(
        title=_(u"Modality of meet"),
        source=sessionModalities,
        required=True,
    )

    directives.mode(IAddForm, adrecaLlista='display')
    adrecaLlista = schema.Text(
        title=_(u"mail address"),
        description=_(u"notification_mail_help"),
        required=True,
    )

    directives.mode(IAddForm, infoAfectats='display')
    directives.mode(IEditForm, infoAfectats='display')
    infoAfectats = schema.Text(
        title=_(u"Informació"),
        description=_(u"Aquestes dades podran ser omplertes una vegada convocada la sessió."),
        required=False,
    )

    directives.mode(IAddForm, adrecaAfectatsLlista='display')
    adrecaAfectatsLlista = schema.Text(
        title=_(u"Stakeholders mail address"),
        description=_(u"Stakeholders mail address help."),
        required=False,
    )

    directives.mode(IAddForm, infoAssistents='display')
    directives.mode(IEditForm, infoAssistents='display')
    infoAssistents = schema.Text(
        title=_(u"Informació"),
        description=_(u"Aquestes dades podran ser omplertes una vegada convocada la sessió."),
        required=False,
    )

    directives.mode(IAddForm, membresConvocats='display')
    textindexer.searchable('membresConvocats')
    membresConvocats = RichTextField(
        title=_(u"Incoming members list"),
        description=_(u"Incoming members list help"),
        required=False,
    )

    directives.mode(IAddForm, membresConvidats='display')
    textindexer.searchable('membresConvidats')
    membresConvidats = RichTextField(
        title=_(u"Invited members"),
        description=_(u"Invited members help"),
        required=False,
    )

    directives.mode(IAddForm, llistaExcusats='display')
    textindexer.searchable('llistaExcusats')
    llistaExcusats = RichTextField(
        title=_(u"Excused members"),
        description=_(u"Excused members help"),
        required=False,
    )

    directives.mode(IAddForm, assistents='display')
    textindexer.searchable('assistents')
    assistents = RichTextField(
        title=_(u"Assistants"),
        description=_(u"Assistants help"),
        required=False,
    )

    directives.mode(IAddForm, noAssistents='display')
    textindexer.searchable('noAssistents')
    noAssistents = RichTextField(
        title=_(u"No assistents"),
        description=_(u"No assistents help"),
        required=False,
    )

    textindexer.searchable('bodyMail')
    bodyMail = RichTextField(
        title=_(u"Body Mail"),
        description=_(u"Body Mail convoquing description"),
        required=False,
        defaultFactory=bodyMail
    )

    textindexer.searchable('signatura')
    signatura = RichTextField(
        title=_(u"Signatura"),
        description=_(u"Signatura description"),
        required=False,
        defaultFactory=signatura
    )

    directives.omitted('infoQuorums')
    infoQuorums = schema.Text(title=u'', required=False, default=u'{}')

    directives.mode(IAddForm, unitatDocumental='display')
    directives.mode(IEditForm, unitatDocumental='display')
    unitatDocumental = schema.TextLine(
        title=u'Unitat documental',
        description=_(u'Aquesta informació es generada automàticament pel gDOC'),
        required=False,
        default=u''
    )


class Edit(form.EditForm):
    """ Session edit form
    """
    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["numSessioShowOnly"].mode = HIDDEN_MODE
        review_state = api.content.get_state(self.context)
        if review_state == 'planificada':
            self.groups[0].fields._data['assistents'].mode = DISPLAY_MODE
            self.groups[0].fields._data["adrecaLlista"].mode = DISPLAY_MODE
            self.groups[0].fields._data["membresConvocats"].mode = DISPLAY_MODE
            self.groups[0].fields._data["membresConvidats"].mode = DISPLAY_MODE
            self.groups[0].fields._data["llistaExcusats"].mode = DISPLAY_MODE
            self.groups[0].fields._data["assistents"].mode = DISPLAY_MODE
            self.groups[0].fields._data["noAssistents"].mode = DISPLAY_MODE
            self.groups[1].fields._data["adrecaAfectatsLlista"].mode = DISPLAY_MODE
        else:
            self.groups[1].fields._data['infoAfectats'].mode = HIDDEN_MODE
            self.groups[0].fields._data['infoAssistents'].mode = HIDDEN_MODE


class View(BrowserView):
    index = ViewPageTemplateFile('sessio.pt')

    def render(self):
        return self.index()

    def viewHistory(self):
        # Només els Secretaris i Managers poden veure el LOG
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        if utils.checkhasRol(['Manager', 'OG1-Secretari'], roles):
            return True
        else:
            return False

    def viewExcusesAndPoints(self):
        # Només els Secretaris i Editors poden veure les excuses
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles):
            return True
        else:
            return False

    def canModify(self):
        # If item is migrated, it can't be modified
        migrated_property = hasattr(self.context, 'migrated')
        if migrated_property:
            if self.context.migrated is True:
                return False

        # But if not migrated, check permissions...
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        review_state = api.content.get_state(self.context)
        value = False
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and 'OG1-Secretari' in roles:
            value = True
        if review_state in ['planificada', 'convocada', 'realitzada'] and 'OG2-Editor' in roles:
            value = True
        return value or 'Manager' in roles

    def showOrdreDiaIAssistencia(self):
        review_state = api.content.get_state(self.context)
        value = False
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        has_roles = utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles)
        if review_state in ['planificada', 'convocada'] and has_roles:
            value = True
        return value

    def showEnviarButton(self):
        review_state = api.content.get_state(self.context)
        value = False
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        has_roles = utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and has_roles:
            value = True
        return value

    def showPresentacionButton(self):
        estatSessio = utils.session_wf_state(self)
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        if 'Manager' in roles:
            return True
        elif estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
            return True
        elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
            return True
        else:
            return False

    def showPublicarButton(self):
        review_state = api.content.get_state(self.context)
        value = False
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        has_roles = utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)
        if review_state in ['realitzada', 'en_correccio'] and has_roles:
            value = True
        return value

    def getColor(self, data):
        # assign custom colors on organ states
        return utils.getColor(data)

    def estatsCanvi(self, data):
        return utils.estatsCanvi(data)

    def hihaPunts(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            path={'query': folder_path,
                  'depth': 1})
        if values:
            return True
        else:
            return False

    def PuntsInside(self):
        """ Retorna punts i acords d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []

        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        for obj in values:

            canOpenVote = False
            canCloseVote = False
            canRecloseVote = False
            titleEsmena = ''
            classVote = False
            hasVote = False
            favorVote = False
            againstVote = False
            whiteVote = False

            if obj.portal_type == 'genweb.organs.acta' or obj.portal_type == 'genweb.organs.audio':
                # add actas to view_template for ordering but dont show them
                item = obj._unrestrictedGetObject()
                results.append(dict(id=obj.id,
                                    classe='d-none',
                                    show=False,
                                    isAcord=False,
                                    agreement=False))

            elif obj.portal_type == 'Folder':
                #la carpeta es pels punts proposats!
                continue

            else:
                item = obj._unrestrictedGetObject()
                if len(item.objectIds()) > 0:
                    inside = True
                else:
                    inside = False
                # TODO !
                # review_state = api.content.get_state(self.context)
                # if review_state in ['realitzada', 'en_correccio']
                if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles):
                    classe = "ui-state-grey"
                else:
                    classe = "ui-state-grey-not_move"
                # Els acords tenen camp agreement, la resta no
                if obj.portal_type == 'genweb.organs.acord':
                    if item.agreement:
                        agreement = item.agreement
                    else:
                        agreement = _(u"sense numeracio") if not getattr(item, 'omitAgreement', False) else False

                    isPunt = False
                    isAcord = True
                    omitAgreement = getattr(item, 'omitAgreement', False)

                    acord = obj.getObject()
                    votacio = acord
                    canOpenVote = acord.estatVotacio == None
                    canCloseVote = acord.estatVotacio == 'open'

                    acord_folder_path = '/'.join(item.getPhysicalPath())
                    esmenas = portal_catalog.unrestrictedSearchResults(
                        portal_type=['genweb.organs.votacioacord'],
                        sort_on='getObjPositionInParent',
                        path={'query': acord_folder_path,
                                'depth': 1})

                    for esmena in esmenas:
                        if esmena.getObject().estatVotacio == 'open':
                            canRecloseVote = acord.id + '/' + esmena.id
                            titleEsmena = esmena.Title
                            votacio = esmena.getObject()
                            canOpenVote = False

                    currentUser = api.user.get_current().id

                    if not isinstance(votacio.infoVotacio, dict):
                        if votacio.infoVotacio == None or votacio.infoVotacio == "":
                            votacio.infoVotacio = {}
                        else:
                            votacio.infoVotacio = ast.literal_eval(votacio.infoVotacio)

                    hasVote = currentUser in votacio.infoVotacio
                    if hasVote:
                        favorVote = votacio.infoVotacio[currentUser] == 'favor'
                        againstVote = votacio.infoVotacio[currentUser] == 'against'
                        whiteVote = votacio.infoVotacio[currentUser] == 'white'

                    if votacio.estatVotacio == None:
                        classVote = 'bi bi-bar-chart'
                    else:
                        if votacio.tipusVotacio == 'public':
                            classVote = 'bi bi-pie-chart'
                        else:
                            classVote = 'bi bi-graph-up-arrow'

                else:
                    agreement = False
                    isPunt = True
                    isAcord = False
                    omitAgreement = False

                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=item.absolute_url(),
                                    item_path=item.absolute_url_path(),
                                    proposalPoint=item.proposalPoint,
                                    agreement=agreement,
                                    omitAgreement=omitAgreement,
                                    state=item.estatsLlista,
                                    css=self.getColor(obj),
                                    estats=self.estatsCanvi(obj),
                                    id=obj.id,
                                    show=True,
                                    isPunt=isPunt,
                                    isAcord=isAcord,
                                    classe=classe,
                                    canOpenVote=canOpenVote,
                                    canCloseVote=canCloseVote,
                                    canRecloseVote=canRecloseVote,
                                    titleEsmena=titleEsmena,
                                    hasVote=hasVote,
                                    classVote=classVote,
                                    favorVote=favorVote,
                                    againstVote=againstVote,
                                    whiteVote=whiteVote,
                                    items_inside=inside,
                                    info_firma=item.info_firma if hasattr(item, 'info_firma') else None))
        return results

    def SubpuntsInside(self, data):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + data['id']
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        results = []
        for obj in values:

            canOpenVote = False
            canCloseVote = False
            canRecloseVote = False
            titleEsmena = ''
            classVote = False
            hasVote = False
            favorVote = False
            againstVote = False
            whiteVote = False

            item = obj.getObject()
            if obj.portal_type == 'genweb.organs.acord':
                if item.agreement:
                    agreement = item.agreement
                else:
                    agreement = _(u"sense numeracio") if not getattr(item, 'omitAgreement', False) else ''

                isAcord = True
                omitAgreement = getattr(item, 'omitAgreement', False)

                votacio = item
                canOpenVote = item.estatVotacio == None
                canCloseVote = item.estatVotacio == 'open'

                acord_folder_path = '/'.join(item.getPhysicalPath())
                esmenas = portal_catalog.unrestrictedSearchResults(
                    portal_type=['genweb.organs.votacioacord'],
                    sort_on='getObjPositionInParent',
                    path={'query': acord_folder_path,
                            'depth': 1})

                for esmena in esmenas:
                    if esmena.getObject().estatVotacio == 'open':
                        canRecloseVote = '/'.join(item.absolute_url_path().split('/')[-2:]) + '/' + esmena.id
                        titleEsmena = esmena.Title
                        votacio = esmena.getObject()
                        canOpenVote = False

                currentUser = api.user.get_current().id

                if not isinstance(votacio.infoVotacio, dict):
                    if votacio.infoVotacio == None or votacio.infoVotacio == "":
                        votacio.infoVotacio = {}
                    else:
                        votacio.infoVotacio = ast.literal_eval(votacio.infoVotacio)

                hasVote = currentUser in votacio.infoVotacio
                if hasVote:
                    favorVote = votacio.infoVotacio[currentUser] == 'favor'
                    againstVote = votacio.infoVotacio[currentUser] == 'against'
                    whiteVote = votacio.infoVotacio[currentUser] == 'white'

                if votacio.estatVotacio == None:
                    classVote = 'bi bi-bar-chart'
                else:
                    if votacio.tipusVotacio == 'public':
                        classVote = 'bi bi-pie-chart'
                    else:
                        classVote = 'bi bi-graph-up-arrow'
            else:
                agreement = False
                isAcord = False
                omitAgreement = False

            results.append(dict(title=obj.Title,
                                portal_type=obj.portal_type,
                                absolute_url=item.absolute_url(),
                                proposalPoint=item.proposalPoint,
                                item_path=item.absolute_url_path(),
                                state=item.estatsLlista,
                                agreement=agreement,
                                omitAgreement=omitAgreement,
                                isAcord=isAcord,
                                estats=self.estatsCanvi(obj),
                                css=self.getColor(obj),
                                canOpenVote=canOpenVote,
                                canCloseVote=canCloseVote,
                                canRecloseVote=canRecloseVote,
                                titleEsmena=titleEsmena,
                                hasVote=hasVote,
                                classVote=classVote,
                                favorVote=favorVote,
                                againstVote=againstVote,
                                whiteVote=whiteVote,
                                id='/'.join(item.absolute_url_path().split('/')[-2:]),
                                info_firma=item.info_firma if hasattr(item, 'info_firma') else None))
        return results

    def canModifyPunt(self, item):
        # If send to sign or signed, it can't be modified
        info_firma = item.get('info_firma')
        if info_firma:
            # Si info_firma es un string (JSON), convertirlo a diccionario
            if isinstance(info_firma, str):
                try:
                    info_firma = ast.literal_eval(info_firma)
                except (ValueError, SyntaxError):
                    # Si no se puede parsear, asumir que no hay fitxers
                    info_firma = {}

            # Ahora verificar si tiene fitxers
            if isinstance(info_firma, dict) and info_firma.get('fitxers', None):
                return False
        # else check if can modify session
        return self.canModify()

    def canViewTabActes(self):
        # Permissions to view acta
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        if 'Manager' in roles:
            return True
        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            else:
                return False
        else:
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            else:
                return False

    def ActesInside(self):
        """ Retorna les actes creades aquí dintre (sense tenir compte estat)
            Nomes ho veuen els Managers / Editors / Secretari
            Els anonymus no les veuen
        """
        if not api.user.is_anonymous():
            username = api.user.get_current().id
            if username:
                canViewActes = self.canViewTabActes()
                if canViewActes:
                    folder_path = '/'.join(self.context.getPhysicalPath())
                    portal_catalog = api.portal.get_tool(name='portal_catalog')
                    values = portal_catalog.searchResults(
                        portal_type='genweb.organs.acta',
                        sort_on='getObjPositionInParent',
                        path={'query': folder_path,
                              'depth': 1})
                    if values:
                        results = []
                        for obj in values:
                            acc = IEventAccessor(self.context)
                            if acc.start:
                                dataSessio = acc.start.strftime('%d/%m/%Y')
                            else:
                                dataSessio = ''
                            results.append(dict(title=obj.Title,
                                                absolute_url=obj.getURL(),
                                                date=dataSessio))

                        return results
                    else:
                        return False
            else:
                return False
        else:
            return False

    def getAnnotations(self):
        """ Get send mail annotations
        """
        try:
            if api.user.is_anonymous():
                return []
            annotations = IAnnotations(self.context)
            try:
                items = annotations.get('genweb.organs.logMail', [])
                if not items:
                    return []
                return sorted(items, key=itemgetter('index'), reverse=True)
            except (KeyError, AttributeError):
                return []
        except:
            return []

    def getAnnotationsExcuse(self):

        if api.user.is_anonymous():
            return False
        else:
            annotations = IAnnotations(self.context)
            # This is used to remove log entries manually
            # import ipdb;ipdb.set_trace()
            # aaa = annotations['genweb.organs.logMail']
            # pp(aaa)       # Search the desired entry position
            # aaa.pop(0)    # remove the entry
            # annotations['genweb.organs.logMail'] = aaa
            try:
                items = annotations['genweb.organs.excuse']
                return sorted(items, key=itemgetter('index'), reverse=True)
            except:
                return False

    def getAnnotationsPoints(self):

        if api.user.is_anonymous():
            return False
        else:
            annotations = IAnnotations(self.context)
            # This is used to remove log entries manually
            # import ipdb;ipdb.set_trace()
            # aaa = annotations['genweb.organs.logMail']
            # pp(aaa)       # Search the desired entry position
            # aaa.pop(0)    # remove the entry
            # annotations['genweb.organs.logMail'] = aaa
            try:
                items = annotations['genweb.organs.point']
                return sorted(items, key=itemgetter('index'), reverse=True)
            except:
                return False

    def valuesTable(self):
        acc = IEventAccessor(self.context)
        if acc.start:
            horaInici = acc.start.strftime('%d/%m/%Y %H:%M')
            year = acc.start.strftime('%Y') + '/'
        else:
            horaInici = ''
            year = ''

        if acc.end:
            horaFi = acc.end.strftime('%d/%m/%Y %H:%M')
        else:
            horaFi = ''

        if self.context.llocConvocatoria is None:
            llocConvocatoria = ''
        else:
            llocConvocatoria = self.context.llocConvocatoria

        session = self.context.numSessio
        organ = self.context.aq_parent.acronim
        sessionNumber = str(organ) + '/' + str(year) + str(session)

        value = api.content.get_state(obj=self.context)
        lang = self.context.language
        status = translate(msgid=value, domain='genweb', target_language=lang)

        values = dict(horaInici=horaInici,
                      horaFi=horaFi,
                      llocConvocatoria=llocConvocatoria,
                      linkSala=self.context.linkSala,
                      modality=self.context.modality,
                      organTitle=self.context.aq_parent.Title(),
                      sessionNumber=sessionNumber,
                      state=value,
                      status=status,
                      )
        return values

    def hihaPersones(self):
        if self.context.membresConvocats or self.context.membresConvidats or self.context.llistaExcusats or self.context.assistents or self.context.assistents:
            return True
        else:
            return False

    def showActaTab(self):
        if self.ActesInside():
            return True
        else:
            return False

    def showAcordsTab(self):
        if self.AcordsInside():
            return True
        else:
            return False

    @property
    def context_base_url(self):
        return self.context.absolute_url()

    def filesinsidePunt(self, item):
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        session_path = '/'.join(self.context.getPhysicalPath()) + '/' + item['id']
        portal_catalog = api.portal.get_tool(name='portal_catalog')

        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file', 'genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': session_path,
                  'depth': 1})
        results = []
        for obj in values:
            value = obj.getObject()

            if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles:
                # Editor i Secretari veuen contingut. NO obren en finestra nova
                if obj.portal_type == 'genweb.organs.file':
                    classCSS = 'bi bi-file-earmark-pdf'  # Es un file
                    if value.visiblefile and value.hiddenfile:
                        classCSS = 'bi bi-file-earmark-pdf text-success double-icon'
                    elif value.hiddenfile:
                        classCSS = 'bi bi-file-earmark-pdf text-danger'
                    elif value.visiblefile:
                        classCSS = 'bi bi-file-earmark-pdf text-success'
                else:
                    classCSS = 'bi bi-file-earmark-text'  # Es un DOC
                    if value.defaultContent and value.alternateContent:
                        classCSS = 'bi bi-file-earmark-text text-success double-icon'
                    elif value.alternateContent:
                        classCSS = 'bi bi-file-earmark-text text-danger'
                    elif value.defaultContent:
                        classCSS = 'bi bi-file-earmark-text text-success'
                # si està validat els mostrem tots
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=obj.getURL(),
                                    new_tab=False,
                                    classCSS=classCSS,
                                    id=str(item['id']) + '/' + obj.id))
            else:
                # Anonim / Afectat / Membre veuen obrir en finestra nova dels fitxers.
                # Es un document, mostrem part publica si la té
                if obj.portal_type == 'genweb.organs.document':
                    classCSS = 'bi bi-file-earmark-text'
                    if value.defaultContent and value.alternateContent:
                        if 'OG3-Membre' in roles:
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL(),
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                        else:
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL(),
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                    elif value.defaultContent:
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL(),
                                            new_tab=True,
                                            classCSS=classCSS,
                                            id=str(item['id']) + '/' + obj.id))
                    elif value.alternateContent:
                        if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG5-Convidat' in roles:
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL(),
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                # es un fitxer, mostrem part publica si la té
                if obj.portal_type == 'genweb.organs.file':
                    info_firma = getattr(value, 'info_firma', None) or {}
                    if not isinstance(info_firma, dict):
                        info_firma = ast.literal_eval(info_firma)

                    classCSS = 'bi bi-file-earmark-pdf'
                    if value.visiblefile and value.hiddenfile:
                        if 'OG3-Membre' in roles:
                            if info_firma.get('private', {}).get('uploaded', False):
                                absolute_url = obj.getURL() + '/viewFileGDoc?visibility=private'
                            else:
                                absolute_url = obj.getURL() + '/@@display-file/hiddenfile/' + value.hiddenfile.filename
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=absolute_url,
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                        else:
                            if info_firma.get('public', {}).get('uploaded', False):
                                absolute_url = obj.getURL() + '/viewFileGDoc?visibility=public'
                            else:
                                absolute_url = obj.getURL() + '/@@display-file/visiblefile/' + value.visiblefile.filename
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=absolute_url,
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                    elif value.visiblefile:
                        if info_firma.get('public', {}).get('uploaded', False):
                            absolute_url = obj.getURL() + '/viewFileGDoc?visibility=public'
                        else:
                            absolute_url = obj.getURL() + '/@@display-file/visiblefile/' + value.visiblefile.filename
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=absolute_url,
                                            new_tab=True,
                                            classCSS=classCSS,
                                            id=str(item['id']) + '/' + obj.id))
                    elif value.hiddenfile:
                        if 'Manager' in roles or 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG5-Convidat' in roles:
                            if info_firma.get('private', {}).get('uploaded', False):
                                absolute_url = obj.getURL() + '/viewFileGDoc?visibility=private'
                            else:
                                absolute_url = obj.getURL() + '/@@display-file/hiddenfile/' + value.hiddenfile.filename
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=absolute_url,
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
        return results

    def AcordsInside(self):
        # If acords in site, publish the tab and the contents...
        results = []
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.acord'],
            sort_on='modified',
            path={'query': folder_path,
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

            results.append(dict(title=value.title,
                                absolute_url=value.absolute_url(),
                                agreement=value.agreement,
                                hiddenOrder=any + num,
                                estatsLlista=value.estatsLlista,
                                color=self.getColor(obj)))
        return sorted(results, key=itemgetter('hiddenOrder'), reverse=True)

    def canView(self):
        # Permissions to view SESSIONS
        # If manager Show all
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        if 'Manager' in roles:
            return True
        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and ('OG1-Secretari' in roles or 'OG2-Editor' in roles):
                return True
            elif estatSessio == 'convocada':
                return True
            elif estatSessio == 'realitzada':
                return True
            elif estatSessio == 'tancada':
                return True
            elif estatSessio == 'en_correccio':
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_members_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_affected_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized

    def canViewManageVote(self):
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        return utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)

    def canViewVoteButtons(self):
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        return utils.checkhasRol(['OG1-Secretari', 'OG3-Membre'], roles)

    def canViewResultsVote(self):
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        return 'Manager' in roles or utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre'], roles)

    def canViewLinkSala(self):
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        return 'Manager' in roles or utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles)

    def getAllResultsVotes(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())

        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.acord', 'genweb.organs.punt'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        acords = []
        for item in items:
            if item.portal_type == 'genweb.organs.acord':
                acords.append(item)
            else:
                items_within_punt = portal_catalog.unrestrictedSearchResults(
                    portal_type=['genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': '/'.join(item.getObject().getPhysicalPath()),
                          'depth': 1})

                for item_within_punt in items_within_punt:
                    acords.append(item_within_punt)

        results = []
        for acord in acords:
            acordObj = acord._unrestrictedGetObject()

            acord_folder_path = '/'.join(acordObj.getPhysicalPath())
            esmenas = portal_catalog.unrestrictedSearchResults(
                portal_type=['genweb.organs.votacioacord'],
                sort_on='getObjPositionInParent',
                path={'query': acord_folder_path,
                      'depth': 1})

            if acordObj.estatVotacio in ['open', 'close']:
                data = {'UID': acord.UID,
                        'URL': acordObj.absolute_url(),
                        'title': acordObj.title,
                        'code': acordObj.agreement,
                        'state': _(u'open') if acordObj.estatVotacio == 'open' else _(u'close'),
                        'isOpen': acordObj.estatVotacio == 'open',
                        'isPublic': acordObj.tipusVotacio == 'public' and self.canViewManageVote(),
                        'hourOpen': acordObj.horaIniciVotacio,
                        'hourClose': acordObj.horaFiVotacio,
                        'favorVote': 0,
                        'againstVote': 0,
                        'whiteVote': 0,
                        'totalVote': 0,
                        'isEsmena': False,
                        'isVote': True,
                        'canReopen': True }

                if acordObj.estatVotacio == 'open':
                    data['canReopen'] = False
                else:
                    for esmena in esmenas:
                        esmenaObj = esmena._unrestrictedGetObject()
                        if esmenaObj.estatVotacio == 'open':
                            data['canReopen'] = False
                            break

                canReopen = data['canReopen']

                infoVotacio = acordObj.infoVotacio
                if isinstance(infoVotacio, str):
                    infoVotacio = ast.literal_eval(infoVotacio)

                if data['isPublic']:
                    data.update({'favorVoteList': []})
                    data.update({'againstVoteList': []})
                    data.update({'whiteVoteList': []})
                    data.update({'totalVoteList': []})

                    for key, value in infoVotacio.items():
                        data['totalVote'] += 1
                        data['totalVoteList'].append(key)
                        if value == 'favor':
                            data['favorVote'] += 1
                            data['favorVoteList'].append(key)
                        elif value == 'against':
                            data['againstVote'] += 1
                            data['againstVoteList'].append(key)
                        elif value == 'white':
                            data['whiteVote'] += 1
                            data['whiteVoteList'].append(key)
                else:
                    for key, value in infoVotacio.items():
                        data['totalVote'] += 1
                        if value == 'favor':
                            data['favorVote'] += 1
                        elif value == 'against':
                            data['againstVote'] += 1
                        elif value == 'white':
                            data['whiteVote'] += 1

                results.append(data)

            if esmenas and acordObj.estatVotacio == None:
                data = {'UID': acord.UID,
                        'URL': acordObj.absolute_url(),
                        'title': acordObj.title,
                        'code': acordObj.agreement,
                        'state': '',
                        'isOpen': False,
                        'isPublic': False,
                        'hourOpen': acordObj.horaIniciVotacio,
                        'hourClose': acordObj.horaFiVotacio,
                        'favorVote': '',
                        'againstVote': '',
                        'whiteVote': '',
                        'totalVote': '',
                        'isEsmena': False,
                        'isVote': False,
                        'canReopen': False }

                results.append(data)

                canReopen = True
                for esmena in esmenas:
                    esmenaObj = esmena._unrestrictedGetObject()
                    if esmenaObj.estatVotacio == 'open':
                        canReopen = False
                        break

            for esmena in esmenas:
                esmenaObj = esmena._unrestrictedGetObject()

                data = {'UID': esmena.UID,
                        'URL': esmenaObj.absolute_url(),
                        'title': esmenaObj.title,
                        'state': _(u'open') if esmenaObj.estatVotacio == 'open' else _(u'close'),
                        'isPublic': esmenaObj.tipusVotacio == 'public' and self.canViewManageVote(),
                        'isOpen': esmenaObj.estatVotacio == 'open',
                        'hourOpen': esmenaObj.horaIniciVotacio,
                        'hourClose': esmenaObj.horaFiVotacio,
                        'favorVote': 0,
                        'againstVote': 0,
                        'whiteVote': 0,
                        'totalVote': 0,
                        'isEsmena': True,
                        'isVote': True,
                        'canReopen': canReopen }

                infoVotacio = esmenaObj.infoVotacio
                if isinstance(infoVotacio, str):
                    infoVotacio = ast.literal_eval(infoVotacio)

                if data['isPublic']:
                    data.update({'favorVoteList': []})
                    data.update({'againstVoteList': []})
                    data.update({'whiteVoteList': []})
                    data.update({'totalVoteList': []})

                    for key, value in infoVotacio.items():
                        data['totalVote'] += 1
                        data['totalVoteList'].append(key)
                        if value == 'favor':
                            data['favorVote'] += 1
                            data['favorVoteList'].append(key)
                        elif value == 'against':
                            data['againstVote'] += 1
                            data['againstVoteList'].append(key)
                        elif value == 'white':
                            data['whiteVote'] += 1
                            data['whiteVoteList'].append(key)
                else:
                    for key, value in infoVotacio.items():
                        data['totalVote'] += 1
                        if value == 'favor':
                            data['favorVote'] += 1
                        elif value == 'against':
                            data['againstVote'] += 1
                        elif value == 'white':
                            data['whiteVote'] += 1

                results.append(data)

        return results

    def getTitlePrompt(self):
        return _(u'title_prompt_votacio')

    def getErrorPrompt(self):
        return _(u'error_prompt_votacio')

    def getInfoQuorums(self):
        if not isinstance(self.context.infoQuorums, dict):
            self.context.infoQuorums = ast.literal_eval(self.context.infoQuorums)

        return self.context.infoQuorums

    def canViewManageQuorumButtons(self):
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        return utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)

    def canViewAddQuorumButtons(self):
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        return utils.checkhasRol(['OG1-Secretari', 'OG3-Membre'], roles)

    def checkHasQuorum(self):
        if not isinstance(self.context.infoQuorums, dict):
            self.context.infoQuorums = ast.literal_eval(self.context.infoQuorums)

        lenQuorums = len(self.context.infoQuorums)
        if lenQuorums > 0 and not self.context.infoQuorums[lenQuorums]['end']:
            return api.user.get_current().id in self.context.infoQuorums[lenQuorums]['people']

        return False

    def showOpenQuorum(self):
        if not isinstance(self.context.infoQuorums, dict):
            self.context.infoQuorums = ast.literal_eval(self.context.infoQuorums)

        lenQuorums = len(self.context.infoQuorums)
        if lenQuorums == 0 or self.context.infoQuorums[lenQuorums]['end']:
            return True

        return False

    def hasFirma(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        actes = portal_catalog.searchResults(
            portal_type=['genweb.organs.acta'],
            path={'query': folder_path, 'depth': 1}
        )
        return any(hasFirmaActa(acta.getObject()) for acta in actes)

    def estatFirma(self):
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        actes = portal_catalog.searchResults(
            portal_type=['genweb.organs.acta'],
            sort_on='created',
            sort_order='reverse',
            path={'query': folder_path, 'depth': 1}
        )
        for acta in actes:
            acta_obj = acta.getObject()
            if hasFirmaActa(acta_obj):
                return estatFirmaActa(acta_obj)

        return None

    def canViewSignButton(self):
        estatSessio = utils.session_wf_state(self)
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, self.context, username)
        organ = utils.get_organ(self.context)
        return (
            organ.visiblegdoc
            and estatSessio in ['realitzada', 'en_correccio']
            and utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles)
        )


class OpenQuorum(BrowserView):

    def __call__(self):
        if not isinstance(self.context.infoQuorums, dict):
            self.context.infoQuorums = ast.literal_eval(self.context.infoQuorums)

        lenQuorums = len(self.context.infoQuorums)
        if lenQuorums == 0 or self.context.infoQuorums[lenQuorums]['end']:
            idQuorum = lenQuorums + 1
            # username = api.user.get_current().id
            # roles = utils.getUserRoles(self, self.context, username)
            # if 'OG1-Secretari' in roles:
            #     self.context.infoQuorums.update({
            #         idQuorum: {
            #             'start': datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
            #             'end': None,
            #             'people': [api.user.get_current().id],
            #             'total': 1,
            #         }
            #     })
            # else:
            self.context.infoQuorums.update({
                idQuorum: {
                    'start': datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'end': None,
                    'people': [],
                    'total': 0,
                }
            })

        self.context.reindexObject()
        transaction.commit()


class CloseQuorum(BrowserView):

    def __call__(self):
        if not isinstance(self.context.infoQuorums, dict):
            self.context.infoQuorums = ast.literal_eval(self.context.infoQuorums)

        lenQuorums = len(self.context.infoQuorums)
        if lenQuorums > 0 and not self.context.infoQuorums[lenQuorums]['end']:
            self.context.infoQuorums[lenQuorums]['end'] = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')

        self.context.reindexObject()
        transaction.commit()


class RemoveQuorums(BrowserView):

    def __call__(self):
        self.context.infoQuorums = {}
        self.context.reindexObject()
        transaction.commit()


class AddQuorum(BrowserView):

    def __call__(self):
        if not isinstance(self.context.infoQuorums, dict):
            self.context.infoQuorums = ast.literal_eval(self.context.infoQuorums)

        lenQuorums = len(self.context.infoQuorums)
        if lenQuorums > 0 and not self.context.infoQuorums[lenQuorums]['end']:
            username = api.user.get_current().id
            if username not in self.context.infoQuorums[lenQuorums]['people']:
                self.context.infoQuorums[lenQuorums]['people'].append(username)
                self.context.infoQuorums[lenQuorums]['total'] = len(self.context.infoQuorums[lenQuorums]['people'])

        self.context.reindexObject()
        transaction.commit()


class ExportCSV(BrowserView):

    data_header_columns = [
        "Tipus d'unitat",
        "Unitat",
        "Nom de l'òrgan",
        "Tipus d'òrgan de govern",
        "Secretaris",
        "Editors",
        "Membres",
        "Afectats",
        "Sessions obertes l'últim any"]

    def __call__(self):
        output_file = StringIO()
        # Write the BOM of the text stream to make its charset explicit
        output_file.write(u'\ufeff')
        self.write_data(output_file)

        header_content_type = 'text/csv'
        header_filename = 'ordre_del_dia_' + self.context.id + '.csv'
        self.request.response.setHeader('Content-Type', header_content_type)
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="{0}"'.format(header_filename))
        return output_file.getvalue()

    def write_data(self, output_file):
        writer = csv.writer(output_file, dialect='excel', delimiter=',')
        writer.writerow(self.data_header_columns)

        info = []
        writer.writerow(['',
                         self.context.Title(),
                         self.context.portal_type.split('.')[2].capitalize(),
                         '',
                         translate(msgid=api.content.get_state(self.context), domain='genweb', target_language='ca'),
                         self.context.absolute_url()])

        writer.writerow(['', '', '', '', '', ''])

        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            sort_on='getObjPositionInParent',
            portal_type=['genweb.organs.acord', 'genweb.organs.punt'],
            path={'query': folder_path,
                  'depth': 1})

        results = []

        for brain in values:
            obj = brain.getObject()

            acord = ''
            if brain.portal_type == 'genweb.organs.acord':
                acord = obj.agreement

            writer.writerow([obj.proposalPoint,
                             '' + brain.Title,
                             brain.portal_type.split('.')[2].capitalize(),
                             acord,
                             translate(msgid=obj.estatsLlista, domain='genweb.organs', target_language='ca'),
                             obj.absolute_url()])

            self.write_data_inside(obj, output_file)

    def write_data_inside(self, context, output_file, last_lvl=False):
        writer = csv.writer(output_file, dialect='excel', delimiter=',')

        portal_catalog = api.portal.get_tool(name='portal_catalog')
        folder_path = '/'.join(context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            sort_on='getObjPositionInParent',
            portal_type=['genweb.organs.acord', 'genweb.organs.subpunt'],
            path={'query': folder_path,
                  'depth': 1})

        results = []

        for brain in values:
            obj = brain.getObject()

            if not last_lvl:
                title = '-- ' + brain.Title
            else:
                title = '-- -- ' + brain.Title

            acord = ''
            if brain.portal_type == 'genweb.organs.acord':
                acord = obj.agreement

            proposalPoint = ''
            state = ''
            if brain.portal_type in ['genweb.organs.acord', 'genweb.organs.subpunt']:
                proposalPoint = obj.proposalPoint
                state = obj.estatsLlista

            writer.writerow([proposalPoint,
                             title,
                             brain.portal_type.split('.')[2].capitalize(),
                             acord,
                             translate(msgid=state, domain='genweb.organs', target_language='ca'),
                             obj.absolute_url()])

            self.write_data_inside(obj, output_file, True)
