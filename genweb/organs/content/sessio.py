
# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName

from collective import dexteritytextindexer
from five import grok
from operator import itemgetter
from plone import api
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from plone.directives import dexterity
from plone.directives import form
from plone.directives import form
from plone.event.interfaces import IEventAccessor
from plone.supermodel.directives import fieldset
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import HIDDEN_MODE  # INPUT_MODE
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.i18n import translate

from genweb.organs import _
from genweb.organs import utils

import ast
import datetime
import transaction

grok.templatedir("templates")


class ISessio(form.Schema):
    """ Sessio
    """

    fieldset('assistents',
             label=_(u'Assistents'),
             fields=['membresConvocats', 'membresConvidats', 'llistaExcusats', 'assistents', 'noAssistents', 'adrecaLlista']
             )

    fieldset('afectats',
             label=_(u'Afectats'),
             fields=['adrecaAfectatsLlista'],
             )

    fieldset('plantilles',
             label=_(u'Plantilles'),
             fields=['bodyMail', 'signatura'],
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Session Title'),
        required=True,
    )

    form.mode(IAddForm, numSessioShowOnly='display')
    form.mode(IEditForm, numSessioShowOnly='hidden')
    numSessioShowOnly = schema.TextLine(
        title=_(u"Session number"),
        required=False,
    )

    form.mode(IAddForm, numSessio='hidden')
    numSessio = schema.TextLine(
        title=_(u"Session number"),
        required=True,
    )

    llocConvocatoria = schema.TextLine(
        title=_(u"Session location"),
        required=False,
    )

    linkSala = schema.TextLine(
        title=_(u"Enllac a la sala"),
        required=False,
    )

    adrecaLlista = schema.Text(
        title=_(u"mail address"),
        description=_(u"notification_mail_help"),
        required=True,
    )

    adrecaAfectatsLlista = schema.Text(
        title=_(u"Stakeholders mail address"),
        description=_(u"Stakeholders mail address help."),
        required=False,
    )

    directives.widget(membresConvocats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('membresConvocats')
    membresConvocats = schema.Text(
        title=_(u"Incoming members list"),
        description=_(u"Incoming members list help"),
        required=False,
    )

    directives.widget(membresConvidats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('membresConvidats')
    membresConvidats = schema.Text(
        title=_(u"Invited members"),
        description=_(u"Invited members help"),
        required=False,
    )

    directives.widget(llistaExcusats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('llistaExcusats')
    llistaExcusats = schema.Text(
        title=_(u"Excused members"),
        description=_(u"Excused members help"),
        required=False,
    )

    directives.widget(assistents=WysiwygFieldWidget)
    dexteritytextindexer.searchable('assistents')
    assistents = schema.Text(
        title=_(u"Assistants"),
        description=_(u"Assistants help"),
        required=False,
    )

    directives.widget(noAssistents=WysiwygFieldWidget)
    dexteritytextindexer.searchable('noAssistents')
    noAssistents = schema.Text(
        title=_(u"No assistents"),
        description=_(u"No assistents help"),
        required=False,
    )

    directives.widget(bodyMail=WysiwygFieldWidget)
    dexteritytextindexer.searchable('bodyMail')
    bodyMail = schema.Text(
        title=_(u"Body Mail"),
        description=_(u"Body Mail convoquing description"),
        required=False,
    )

    directives.widget(signatura=WysiwygFieldWidget)
    dexteritytextindexer.searchable('signatura')
    signatura = schema.Text(
        title=_(u"Signatura"),
        description=_(u"Signatura description"),
        required=False,
    )

    directives.omitted('infoQuorums')
    infoQuorums = schema.Text(title=u'', required=False, default=u'{}')


@form.default_value(field=ISessio['numSessio'])
def numSessioDefaultValue(data):
    # Agafem sessions ordenades
    # Les comptem i assignem el següent valor
    sessions = api.content.find(
        portal_type='genweb.organs.sessio',
        context=data.context)
    total = 0
    year = datetime.datetime.today().strftime('%Y')
    for session in sessions:
        if session.getObject().start.strftime('%Y') == year:
            total = total + 1
    return '{0}'.format(str(total + 1).zfill(2))


@form.default_value(field=ISessio['numSessioShowOnly'])
def numSessioShowOnlyDefaultValue(data):
    # Agafem sessions ordenades
    # Les comptem i assignem el següent valor.
    # Aquest camp és només READONLY
    sessions = api.content.find(
        portal_type='genweb.organs.sessio',
        context=data.context)
    total = 0
    year = datetime.datetime.today().strftime('%Y')
    for session in sessions:
        if session.getObject().start.strftime('%Y') == year:
            total = total + 1
    return '{0}'.format(str(total + 1).zfill(2))


@form.default_value(field=ISessio['membresConvocats'])
def membresConvocatsDefaultValue(data):
    # copy Convocats from Organ de Govern (parent object)
    return data.context.membresOrgan


@form.default_value(field=ISessio['membresConvidats'])
def membresConvidatsDefaultValue(data):
    # copy Convidats from Organ de Govern (parent object)
    return data.context.convidatsPermanentsOrgan


@form.default_value(field=ISessio['adrecaLlista'])
def adrecaLlistaDefaultValue(data):
    # copy adrecaLlista from Organ de Govern (parent object)
    return data.context.adrecaLlista


@form.default_value(field=ISessio['adrecaAfectatsLlista'])
def adrecaAfectatsLlistaDefaultValue(data):
    # copy adrecaAfectats from Organ de Govern (parent object)
    return data.context.adrecaAfectatsLlista


@form.default_value(field=ISessio['bodyMail'])
def bodyMailDefaultValue(data):
    # copy bodyMail from Organ de Govern (parent object)
    return data.context.bodyMailconvoquing


@form.default_value(field=ISessio['signatura'])
def signaturaDefaultValue(data):
    # copy signatura from Organ de Govern (parent object)
    return data.context.footerMail


class Edit(dexterity.EditForm):
    """ Session edit form
    """
    grok.context(ISessio)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["numSessioShowOnly"].mode = HIDDEN_MODE


class View(grok.View):
    grok.context(ISessio)
    grok.template('sessio_view')

    def viewHistory(self):
        # Només els Secretaris i Managers podem veure el LOG
        if utils.isSecretari(self) or utils.isManager(self):
            return True
        else:
            return False

    def viewExcusesAndPoints(self):
        # Només els Secretaris i Editors poden veure les excuses
        if utils.isSecretari(self) or utils.isEditor(self) or utils.isManager(self):
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
        review_state = api.content.get_state(self.context)
        value = False
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and utils.isSecretari(self):
            value = True
        if review_state in ['planificada', 'convocada', 'realitzada'] and utils.isEditor(self):
            value = True
        return value or utils.isManager(self)

    def showOrdreDiaIAssistencia(self):
        review_state = api.content.get_state(self.context)
        value = False
        roles = utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isManager(self)
        if review_state in ['planificada', 'convocada'] and roles:
            value = True
        return value

    def showEnviarButton(self):
        review_state = api.content.get_state(self.context)
        value = False
        roles = utils.isSecretari(self) or utils.isEditor(self) or utils.isManager(self)
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and roles:
            value = True
        return value

    def showPresentacionButton(self):
        estatSessio = utils.session_wf_state(self)
        if utils.isManager(self):
            return True
        elif estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        else:
            return False

    def showPublicarButton(self):
        review_state = api.content.get_state(self.context)
        value = False
        roles = utils.isSecretari(self) or utils.isEditor(self) or utils.isManager(self)
        if review_state in ['realitzada', 'en_correccio'] and roles:
            value = True
        return value

    def getColor(self, data):
        # assign custom colors on organ states
        return utils.getColor(data)

    def estatsCanvi(self, data):
        return utils.estatsCanvi(data)

    def hihaPunts(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
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
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []

        for obj in values:

            canOpenVote = False
            canCloseVote = False
            canReopenVote = False
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
                                    classe='hidden',
                                    show=False,
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
                if utils.isSecretari(self) or utils.isEditor(self) or utils.isManager(self):
                    classe = "ui-state-grey"
                else:
                    classe = "ui-state-grey-not_move"
                # Els acords tenen camp agreement, la resta no
                if obj.portal_type == 'genweb.organs.acord':
                    if item.agreement:
                        agreement = item.agreement
                    else:
                        agreement = _(u"sense numeracio")
                    isPunt = False

                    acord = obj.getObject()
                    votacio = acord
                    canOpenVote = acord.estatVotacio == None
                    canCloseVote = acord.estatVotacio == 'open'

                    if acord.estatVotacio == 'close':
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

                        if not canRecloseVote:
                            canReopenVote = True

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
                        classVote = 'fa fa-bar-chart'
                    else:
                        if votacio.tipusVotacio == 'public':
                            classVote = 'fa fa-pie-chart'
                        else:
                            classVote = 'fa fa-user-chart'

                else:
                    agreement = False
                    isPunt = True

                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=item.absolute_url(),
                                    item_path=item.absolute_url_path(),
                                    proposalPoint=item.proposalPoint,
                                    agreement=agreement,
                                    state=item.estatsLlista,
                                    css=self.getColor(obj),
                                    estats=self.estatsCanvi(obj),
                                    id=obj.id,
                                    show=True,
                                    isPunt=isPunt,
                                    classe=classe,
                                    canOpenVote=canOpenVote,
                                    canCloseVote=canCloseVote,
                                    canReopenVote=canReopenVote,
                                    canRecloseVote=canRecloseVote,
                                    titleEsmena=titleEsmena,
                                    hasVote=hasVote,
                                    classVote=classVote,
                                    favorVote=favorVote,
                                    againstVote=againstVote,
                                    whiteVote=whiteVote,
                                    items_inside=inside))
        return results

    def SubpuntsInside(self, data):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + data['id']
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        results = []
        for obj in values:
            item = obj.getObject()
            if obj.portal_type == 'genweb.organs.acord':
                if item.agreement:
                    agreement = item.agreement
                else:
                    agreement = _(u"sense numeracio")
            else:
                agreement = False
            results.append(dict(title=obj.Title,
                                portal_type=obj.portal_type,
                                absolute_url=item.absolute_url(),
                                proposalPoint=item.proposalPoint,
                                item_path=item.absolute_url_path(),
                                state=item.estatsLlista,
                                agreement=agreement,
                                estats=self.estatsCanvi(obj),
                                css=self.getColor(obj),
                                id='/'.join(item.absolute_url_path().split('/')[-2:])))
        return results

    def canViewTabActes(self):
        # Permissions to view acta
        estatSessio = utils.session_wf_state(self)
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif utils.isManager(self):
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
                    portal_catalog = getToolByName(self, 'portal_catalog')
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
                items = annotations['genweb.organs.logMail']
                return sorted(items, key=itemgetter('index'), reverse=True)
            except:
                return False

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
                      organTitle=self.context.aq_parent.Title(),
                      sessionNumber=sessionNumber,
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
        session_path = '/'.join(self.context.getPhysicalPath()) + '/' + item['id']
        portal_catalog = getToolByName(self, 'portal_catalog')

        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file', 'genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': session_path,
                  'depth': 1})
        results = []
        for obj in values:
            value = obj.getObject()
            if utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self):
                # Editor i Secretari veuen contingut. NO obren en finestra nova
                if obj.portal_type == 'genweb.organs.file':
                    classCSS = 'fa fa-file-pdf-o'  # Es un file
                    if value.visiblefile and value.hiddenfile:
                        classCSS = 'fa fa-file-pdf-o text-success double-icon'
                    elif value.hiddenfile:
                        classCSS = 'fa fa-file-pdf-o text-error'
                    elif value.visiblefile:
                        classCSS = 'fa fa-file-pdf-o text-success'
                else:
                    classCSS = 'fa fa-file-text-o'  # Es un DOC
                    if value.defaultContent and value.alternateContent:
                        classCSS = 'fa fa-file-text-o text-success double-icon'
                    elif value.alternateContent:
                        classCSS = 'fa fa-file-text-o text-error'
                    elif value.defaultContent:
                        classCSS = 'fa fa-file-text-o text-success'
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
                    classCSS = 'fa fa-file-text-o'
                    if value.defaultContent and value.alternateContent:
                        if utils.isMembre(self):
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
                        if utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self):
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL(),
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                # es un fitxer, mostrem part publica si la té
                if obj.portal_type == 'genweb.organs.file':
                    classCSS = 'fa fa-file-pdf-o'
                    if value.visiblefile and value.hiddenfile:
                        if utils.isMembre(self):
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL() + '/@@display-file/hiddenfile/' + value.hiddenfile.filename,
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                        else:
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL() + '/@@display-file/visiblefile/' + value.visiblefile.filename,
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
                    elif value.visiblefile:
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL() + '/@@display-file/visiblefile/' + value.visiblefile.filename,
                                            new_tab=True,
                                            classCSS=classCSS,
                                            id=str(item['id']) + '/' + obj.id))
                    elif value.hiddenfile:
                        if utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self):
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=obj.getURL() + '/@@display-file/hiddenfile/' + value.hiddenfile.filename,
                                                new_tab=True,
                                                classCSS=classCSS,
                                                id=str(item['id']) + '/' + obj.id))
        return results

    def AcordsInside(self):
        # If acords in site, publish the tab and the contents...
        results = []
        portal_catalog = getToolByName(self, 'portal_catalog')
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
        if utils.isManager(self):
            return True
        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'tancada':
                return True
            elif estatSessio == 'en_correccio':
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_members_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_affected_organ':
            if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return True
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                return True
            else:
                raise Unauthorized

    def canViewManageVote(self):
        # estatSessio = utils.session_wf_state(self)
        # return estatSessio == 'convocada' and (utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self))
        if self.context.aq_parent.id == 'consell-de-govern':
            return utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self)
        return False

    def canViewVoteButtons(self):
        # estatSessio = utils.session_wf_state(self)
        # return estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isMembre(self))
        if self.context.aq_parent.id == 'consell-de-govern':
            return utils.isSecretari(self) or utils.isMembre(self)
        return False

    def canViewResultsVote(self):
        # estatSessio = utils.session_wf_state(self)
        # return estatSessio == 'convocada' and (utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self))
        if self.context.aq_parent.id == 'consell-de-govern':
            return utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)
        return False

    def canViewLinkSala(self):
        return utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)

    def getAllResultsVotes(self):
        if self.context.aq_parent.id != 'consell-de-govern':
            return []

        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())

        acords = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 3})

        results = []
        for acord in acords:
            acordObj = acord._unrestrictedGetObject()

            if acordObj.estatVotacio in ['open', 'close']:
                data = {'UID': acord.UID,
                        'URL': acordObj.absolute_url(),
                        'title': acordObj.title,
                        'code': acordObj.agreement if acordObj.agreement else '',
                        'state': _(u'open') if acordObj.estatVotacio == 'open' else _(u'close'),
                        'isOpen': acordObj.estatVotacio == 'open',
                        'isPublic': acordObj.tipusVotacio == 'public' and self.canViewManageVote(),
                        'favorVote': 0,
                        'againstVote': 0,
                        'whiteVote': 0,
                        'totalVote': 0,
                        'isEsmena': False}

                infoVotacio = acordObj.infoVotacio
                if isinstance(infoVotacio, str) or isinstance(infoVotacio, unicode):
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

                if data['favorVote'] == 0 and data['againstVote'] == 0 and data['whiteVote'] == 0:
                    data['isPublic'] = False

                results.append(data)

                acord_folder_path = '/'.join(acordObj.getPhysicalPath())
                esmenas = portal_catalog.unrestrictedSearchResults(
                    portal_type=['genweb.organs.votacioacord'],
                    sort_on='getObjPositionInParent',
                    path={'query': acord_folder_path,
                          'depth': 1})

                for esmena in esmenas:
                    esmenaObj = esmena._unrestrictedGetObject()

                    data = {'UID': esmena.UID,
                            'URL': esmenaObj.absolute_url(),
                            'title': esmenaObj.title,
                            'state': _(u'open') if esmenaObj.estatVotacio == 'open' else _(u'close'),
                            'isPublic': esmenaObj.tipusVotacio == 'public' and self.canViewManageVote(),
                            'isOpen': esmenaObj.estatVotacio == 'open',
                            'favorVote': 0,
                            'againstVote': 0,
                            'whiteVote': 0,
                            'totalVote': 0,
                            'isEsmena': True}

                    infoVotacio = esmenaObj.infoVotacio
                    if isinstance(infoVotacio, str) or isinstance(infoVotacio, unicode):
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

                    if data['favorVote'] == 0 and data['againstVote'] == 0 and data['whiteVote'] == 0:
                        data['isPublic'] = False

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
        if self.context.aq_parent.id == 'consell-de-govern':
            return utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self)
        return False

    def canViewAddQuorumButtons(self):
        if self.context.aq_parent.id == 'consell-de-govern':
            return utils.isSecretari(self) or utils.isMembre(self)
        return False

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


class OpenQuorum(grok.View):
    grok.context(ISessio)
    grok.name('openQuorum')
    grok.require('genweb.organs.manage.quorum')

    def render(self):
        if not isinstance(self.context.infoQuorums, dict):
            self.context.infoQuorums = ast.literal_eval(self.context.infoQuorums)

        lenQuorums = len(self.context.infoQuorums)
        if lenQuorums == 0 or self.context.infoQuorums[lenQuorums]['end']:
            idQuorum = lenQuorums + 1
            self.context.infoQuorums.update({
                idQuorum: {
                    'start': datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'end': None,
                    'people': [api.user.get_current().id],
                    'total': 1,
                }
            })

        transaction.commit()


class CloseQuorum(grok.View):
    grok.context(ISessio)
    grok.name('closeQuorum')
    grok.require('genweb.organs.manage.quorum')

    def render(self):
        if not isinstance(self.context.infoQuorums, dict):
            self.context.infoQuorums = ast.literal_eval(self.context.infoQuorums)

        lenQuorums = len(self.context.infoQuorums)
        if lenQuorums > 0 and not self.context.infoQuorums[lenQuorums]['end']:
            self.context.infoQuorums[lenQuorums]['end'] = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')

        transaction.commit()


class RemoveQuorums(grok.View):
    grok.context(ISessio)
    grok.name('removeQuorums')
    grok.require('genweb.organs.remove.quorum')

    def render(self):
        self.context.infoQuorums = {}
        transaction.commit()


class AddQuorum(grok.View):
    grok.context(ISessio)
    grok.name('addQuorum')
    grok.require('genweb.organs.add.quorum')

    def render(self):
        if not isinstance(self.context.infoQuorums, dict):
            self.context.infoQuorums = ast.literal_eval(self.context.infoQuorums)

        lenQuorums = len(self.context.infoQuorums)
        if lenQuorums > 0 and not self.context.infoQuorums[lenQuorums]['end']:
            username = api.user.get_current().id
            if username not in self.context.infoQuorums[lenQuorums]['people']:
                self.context.infoQuorums[lenQuorums]['people'].append(username)
                self.context.infoQuorums[lenQuorums]['total'] = len(self.context.infoQuorums[lenQuorums]['people'])

        transaction.commit()
