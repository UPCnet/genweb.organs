# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.indexer import indexer
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
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from plone.event.utils import default_timezone as fallback_default_timezone
from plone.event.utils import validated_timezone
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import datetime
from plone.app.event.base import localized_now
from plone.app.event.dx.interfaces import IDXEvent

from plone.event.interfaces import IEventAccessor

import pytz
from zope.component.hooks import getSite

grok.templatedir("templates")

DEFAULT_END_DELTA = 2  # hours


@provider(IContextAwareDefaultFactory)
def default_start(context=None):
    """Return the default start as python datetime for prefilling forms.
    :returns: Default start datetime.
    :rtype: Python datetime
    """
    now = localized_now(context=context)
    return now.replace(minute=0, second=0, microsecond=0)


@provider(IContextAwareDefaultFactory)
def default_end(context):
    """Return the default end as python datetime for prefilling forms.
    :returns: Default end datetime.
    :rtype: Python datetime
    """
    return default_start(context=context) + datetime.timedelta(hours=DEFAULT_END_DELTA)


class ISessio(form.Schema):
    """ Tipus Sessio: Per a cada Òrgan de Govern es podran crear
        totes les sessions que es considerin oportunes
    """

    fieldset('assistents',
             label=_(u'Assistents'),
             fields=['membresConvocats', 'membresConvidats', 'llistaExcusats', 'noAssistents']
             )

    fieldset('notificacions',
             label=_(u'Notifications'),
             fields=['adrecaLlista', 'adrecaAfectatsLlista', 'bodyMail', 'signatura'],
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Session Title'),
        required=True,
    )

    numSessio = schema.TextLine(
        title=_(u"Session number"),
        required=False,
    )

    llocConvocatoria = schema.TextLine(
        title=_(u"Session location"),
        required=False,
    )

    horaInici = schema.Datetime(
        title=_(u'label_event_start'),
        required=True,
        defaultFactory=default_start
    )
    # from zope.schema import Datetime
    # DateTime('2017/02/13 13:00:00 Europe/Madrid')
    # datetime.datetime(2017, 3, 14, 12, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>)

    horaFi = schema.Datetime(
        title=_(u'label_event_end'),
        required=True,
        defaultFactory=default_end
    )

    adrecaLlista = schema.Text(
        title=_(u"mail address"),
        description=_(u"notification_mail_help"),
        required=True,
    )

    adrecaAfectatsLlista = schema.Text(
        title=_(u"Stakeholders mail address"),
        description=_(u"affected_mail_help"),
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
        description=_(u"Body Mail description"),
        required=False,
    )

    directives.widget(signatura=WysiwygFieldWidget)
    dexteritytextindexer.searchable('signatura')
    signatura = schema.Text(
        title=_(u"Signatura"),
        description=_(u"Signatura description"),
        required=False,
    )

    # @invariant
    # def validate_start_end(data):
    #     if (data.start and data.end and data.start > data.end):
    #         raise Invalid("Error, invalid date range")


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
                username = api.user.get_current().getProperty('id')
                roles = api.user.get_roles(username=username, obj=self.context)
                return roles
        except:
            return False

    def isAnonim(self):
        return utils.isAnonim(self)

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

    def canModify(self):
        review_state = api.content.get_state(self.context)
        value = False
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and utils.isSecretari(self):
            value = True
        if review_state in ['planificada', 'convocada', 'realitzada'] and utils.isEditor(self):
            value = True
        return value or self.isManager()

    def dataSessio(self):
        if self.context.start:
            return self.context.start.strftime('%d/%m/%Y')
        else:
            return None

    def horaInici(self):
        if self.context.start:
            return self.context.start.strftime('%H:%M')
        else:
            return None

    def horaFi(self):
        if self.context.end:
            return self.context.end.strftime('%H:%M')
        else:
            return None

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
        values = api.content.find(context=self.context, depth=1, portal_type='genweb.organs.punt')
        if values:
            return True
        else:
            return False

    def PuntsInside(self):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            if obj.portal_type == 'genweb.organs.acta' or obj.portal_type == 'genweb.organs.audio':
                # add actas to template for oredering but dont show
                item = obj.getObject()
                results.append(dict(id=obj.id,
                                    classe='hidden',
                                    show=False,
                                    agreement=False))
            else:
                item = obj.getObject()
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

                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=item.absolute_url(),
                                    item_path=item.absolute_url_path(),
                                    proposalPoint=item.proposalPoint,
                                    agreement=item.agreement,
                                    state=item.estatsLlista,
                                    css=self.getColor(obj),
                                    estats=self.estatsCanvi(obj),
                                    id=obj.id,
                                    show=True,
                                    classe=classe,
                                    items_inside=inside))
        return results

    def SubpuntsInside(self, data):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + data['id']
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.subpunt',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        results = []
        for obj in values:
            item = obj.getObject()
            results.append(dict(title=obj.Title,
                                portal_type=obj.portal_type,
                                absolute_url=item.absolute_url(),
                                proposalPoint=item.proposalPoint,
                                item_path=item.absolute_url_path(),
                                state=item.estatsLlista,
                                agreement=item.agreement,
                                estats=self.estatsCanvi(obj),
                                css=self.getColor(obj),
                                id='/'.join(item.absolute_url_path().split('/')[-2:])))
        return results

    def ActesInside(self):
        """ Retorna les actes creades aquí dintre (sense tenir compte estat)
        """
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
                objecte = obj.getObject()
                if objecte.start:
                    dataSessio = objecte.start.strftime('%d/%m/%Y')
                else:
                    dataSessio = ''
                results.append(dict(title=obj.Title,
                                    absolute_url=obj.getURL(),
                                    date=dataSessio))
            return results
        else:
            return False

    def AudioInside(self):
        """ Retorna els fitxers d'audio creats aquí dintre (sense tenir compte estat)
        """
        folder_path = '/'.join(self.context.getPhysicalPath())
        portal_catalog = getToolByName(self, 'portal_catalog')
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.audio',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        if values:
            results = []
            for obj in values:
                results.append(dict(title=obj.Title,
                                    absolute_url=obj.getURL()))
            return results
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
                return sorted(annotations['genweb.organs.logMail'], reverse=True)
            except:
                return False

    def valuesTable(self):
        if self.context.start:
            dataSessio = self.context.start.strftime('%d/%m/%Y')
            horaInici = self.context.start.strftime('%H:%M')
        else:
            dataSessio = ''
            horaInici = ''
        if self.context.end:
            horaFi = self.context.end.strftime('%H:%M')
        else:
            horaFi = ''

        if self.context.llocConvocatoria is None:
            llocConvocatoria = ''
        else:
            llocConvocatoria = self.context.llocConvocatoria

        values = dict(dataSessio=dataSessio,
                      horaInici=horaInici,
                      horaFi=horaFi,
                      llocConvocatoria=llocConvocatoria,
                      organTitle=self.OrganTitle(),
                      )
        return values

    def OrganTitle(self):
        """ Retorna el títol de l'òrgan """
        title = self.context.aq_parent.Title()
        return title

    def hihaPersones(self):
        if self.context.membresConvocats or self.context.membresConvidats or self.context.llistaExcusats:
            return True
        else:
            return False

    def showActaTab(self):
        if self.AudioInside() or self.ActesInside():
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
            if obj.portal_type == 'genweb.organs.file':
                if obj.hiddenfile is True:
                    try:
                        username = api.user.get_current().getProperty('id')
                        roles = api.user.get_roles(username=username, obj=self.context)
                        if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'Manager' in roles:
                            tipus = 'fa fa-file-pdf-o'
                            document = _(u'Fitxer intern')
                            labelClass = 'label label-danger'
                        else:
                            continue
                    except:
                        continue
                else:
                    tipus = 'fa fa-file-pdf-o'
                    document = _(u'Fitxer públic')
                    labelClass = 'label label-default'

            else:
                tipus = 'fa fa-file-text-o'
                document = _(u'Document')
                labelClass = 'label label-default'
                obj.hiddenfile = False

            results.append(dict(title=obj.Title,
                                portal_type=obj.portal_type,
                                absolute_url=obj.getURL(),
                                classCSS=tipus,
                                hidden=obj.hiddenfile,
                                labelClass=labelClass,
                                content=document,
                                id=str(item['id']) + '/' + obj.id))
        return results


@indexer(ISessio)
def horaInici(context):
    """Create a catalogue indexer, registered as an adapter, which can
    populate the ``horaInici`` value count it and index.
    """
    return get_session_datetime(context)
grok.global_adapter(horaInici, name='start')


def get_session_datetime(session):
    session_time = session.horaInici
    if type(session_time) is not datetime.time:
        session_time = datetime.time()
    # return datetime.datetime.combine(session.horaInici, session_time)
    # return localized_now(context=session).replace(minute=0, second=0, microsecond=0)
    return session.horaInici.strftime('%Y/%m/%d %H:%M:%S')


@indexer(ISessio)
def horaFi(context):
    """Create a catalogue indexer, registered as an adapter, which can
    populate the ``horaFi`` value count it and index.
    """
    return get_session_datetime_fi(context)
grok.global_adapter(horaFi, name='end')


def get_session_datetime_fi(session):
    session_time = session.horaFi
    if type(session_time) is not datetime.time:
        session_time = datetime.time()
    # return datetime.datetime.combine(session.horaFi, session_time)
    return session.horaFi.strftime('%Y/%m/%d %H:%M:%S')
