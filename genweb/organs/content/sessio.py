# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from collective import dexteritytextindexer
from Products.CMFCore.utils import getToolByName
from plone import api
from zope.annotation.interfaces import IAnnotations
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.supermodel.directives import fieldset
from genweb.organs import utils
from zope.i18n import translate
from z3c.form.interfaces import HIDDEN_MODE  # INPUT_MODE, DISPLAY_MODE
from plone.event.interfaces import IEventAccessor
from operator import itemgetter


grok.templatedir("templates")


class ISessio(form.Schema):
    """ Tipus Sessio: Per a cada Òrgan de Govern es podran crear
        totes les sessions que es considerin oportunes
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

    directives.mode(numSessioShowOnly='display')
    numSessioShowOnly = schema.TextLine(
        title=_(u"Session number"),
        required=False,
    )

    directives.mode(numSessio='hidden')
    numSessio = schema.TextLine(
        title=_(u"Session number"),
        required=False,
    )

    llocConvocatoria = schema.TextLine(
        title=_(u"Session location"),
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


@form.default_value(field=ISessio['numSessio'])
def numSessioDefaultValue(data):
    # agafo sessions ordenats!
    # Saves the value in object
    sessions = api.content.find(
        portal_type='genweb.organs.sessio',
        context=data.context)
    total = len(sessions)
    return '{0}'.format(str(total + 1).zfill(2))


@form.default_value(field=ISessio['numSessioShowOnly'])
def numSessioShowOnlyDefaultValue(data):
    # agafo sessions ordenats!
    # only shows the value in readonly
    sessions = api.content.find(
        portal_type='genweb.organs.sessio',
        context=data.context)
    total = len(sessions)
    return '{0}'.format(str(total + 1).zfill(2))


@form.default_value(field=ISessio['membresConvocats'])
def membresConvocatsDefaultValue(data):
    # copy members from Organ de Govern (parent object)
    return data.context.membresOrgan


@form.default_value(field=ISessio['membresConvidats'])
def membresConvidatsDefaultValue(data):
    # copy members from Organ de Govern (parent object)
    return data.context.convidatsPermanentsOrgan


@form.default_value(field=ISessio['adrecaLlista'])
def adrecaLlistaDefaultValue(data):
    # copy adrecaLlista from Organ de Govern (parent object)
    return data.context.adrecaLlista


@form.default_value(field=ISessio['adrecaAfectatsLlista'])
def adrecaAfectatsLlistaDefaultValue(data):
    # copy adrecaLlista from Organ de Govern (parent object)
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
    """A standard edit form.
    """
    grok.context(ISessio)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["numSessioShowOnly"].mode = HIDDEN_MODE


class View(grok.View):
    grok.context(ISessio)
    grok.template('sessio_view')

    def objectState(self):
        # while debugging...
        return api.content.get_state(obj=self.context)

    def roles(self):
        # while debugging...
        try:
            if api.user.is_anonymous():
                return 'Annonymous'
            else:
                username = api.user.get_current().id
                roles = api.user.get_roles(username=username, obj=self.context)
                return roles
        except:
            return False

    def isAfectat(self):
        return utils.isAfectat(self)

    def isMembre(self):
        return utils.isMembre(self)

    def isEditor(self):
        return utils.isEditor(self)

    def isSecretari(self):
        return utils.isSecretari(self)

    def isManager(self):
        return utils.isManager(self)

    def viewHistory(self):
        value = False
        if utils.isSecretari(self):
            value = True
        return value or self.isManager()

    def canModify(self):
        # If item is migrated, it can't be modified
        migrated = hasattr(self.context, 'migrated')
        if migrated is True:
            return False
        # But if not migrated, check permissions...
        review_state = api.content.get_state(self.context)
        value = False
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and utils.isSecretari(self):
            value = True
        if review_state in ['planificada', 'convocada', 'realitzada'] and utils.isEditor(self):
            value = True
        return value or self.isManager()

    def showEnviarButton(self):
        review_state = api.content.get_state(self.context)
        value = False
        roles = utils.isSecretari(self) or utils.isEditor(self) or utils.isManager(self)
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and roles:
            value = True
        return value

    def showPresentacionButton(self):
        review_state = api.content.get_state(self.context)
        value = False
        roles = utils.isSecretari(self) or utils.isEditor(self) or utils.isManager(self)
        if review_state in ['convocada', 'realitzada', 'en_correccio'] and roles:
            value = True
        return value

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
            if obj.portal_type == 'genweb.organs.acta' or obj.portal_type == 'genweb.organs.audio':
                # add actas to view_template for ordering but dont show them
                item = obj._unrestrictedGetObject()
                results.append(dict(id=obj.id,
                                    classe='hidden',
                                    show=False,
                                    agreement=False))
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
            item = obj._unrestrictedGetObject()
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

            anonymous = api.user.is_anonymous()
            if anonymous:
                # Es un document, mostrem part publica si la té
                if obj.portal_type == 'genweb.organs.document':
                    classCSS = 'fa fa-file-text-o'
                    if obj.getObject().defaultContent:
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL(),
                                            classCSS=classCSS,
                                            id=str(item['id']) + '/' + obj.id))
                # es un fitxer, mostrem part publica si la té
                if obj.portal_type == 'genweb.organs.file':
                    classCSS = 'fa fa-file-pdf-o'
                    if obj.getObject().visiblefile:
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL(),
                                            classCSS=classCSS,
                                            id=str(item['id']) + '/' + obj.id))
            else:
                if obj.portal_type == 'genweb.organs.file':
                    # És un File
                    classCSS = 'fa fa-file-pdf-o'
                else:
                    # És un document
                    classCSS = 'fa fa-file-text-o'
                # si està validat els mostrem tots
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=obj.getURL(),
                                    classCSS=classCSS,
                                    id=str(item['id']) + '/' + obj.id))

        return results

    def AcordsInside(self):
        # If acords in site, publish the tab and the contents...
        results = []
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())

        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.acord'],
            sort_on='modified',
            path={'query': folder_path,
                  'depth': 3})

        for obj in values:
            value = obj.getObject()
            # value = obj._unrestrictedGetObject()
            if value.agreement:
                if len(value.agreement.split('/')) > 2:
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
                                estatsLlista=value.estatsLlista))
        return sorted(results, key=itemgetter('hiddenOrder'))
