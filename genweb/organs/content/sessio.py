# -*- coding: utf-8 -*-
import datetime
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


class InvalidEmailError(schema.ValidationError):
    __doc__ = u'Please enter a valid e-mail address.'

grok.templatedir("templates")


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

    any = schema.TextLine(
        title=_(u"Year"),
        required=False,
    )

    numSessio = schema.TextLine(
        title=_(u"Session number"),
        required=False,
    )

    dataSessio = schema.Date(
        title=_(u"Session date"),
        required=True,
    )

    llocConvocatoria = schema.TextLine(
        title=_(u"Session location"),
        required=False,
    )

    horaInici = schema.Time(
        title=_(u"Session start time"),
        required=False,
    )

    horaFi = schema.Time(
        title=_(u"Session end time"),
        required=False,
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
        required=False,
    )

    directives.widget(membresConvidats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('membresConvidats')
    membresConvidats = schema.Text(
        title=_(u"Invited members"),
        required=False,
    )

    directives.widget(llistaExcusats=WysiwygFieldWidget)
    dexteritytextindexer.searchable('llistaExcusats')
    llistaExcusats = schema.Text(
        title=_(u"Excused members"),
        required=False,
    )

    directives.widget(noAssistents=WysiwygFieldWidget)
    dexteritytextindexer.searchable('noAssistents')
    noAssistents = schema.Text(
        title=_(u"No assistents"),
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
        required=False,
    )

    enllacVideo = schema.TextLine(
        title=_(u"Video link"),
        required=False,
    )

    enllacAudio = schema.TextLine(
        title=_(u"Audio link"),
        required=False,
    )


@form.default_value(field=ISessio['dataSessio'])
def dataSessioDefaultValue(data):
    return datetime.datetime.today()


@form.default_value(field=ISessio['horaInici'])
def horaIniciDefaultValue(data):
    time = datetime.datetime.today()
    return time


@form.default_value(field=ISessio['horaFi'])
def horaFiDefaultValue(data):
    time = datetime.datetime.today() + datetime.timedelta(hours=1)
    return time


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

    def isEditor(self):
        """ Show send message button if user is editor """
        return utils.isEditor(self)

    def isReader(self):
        return utils.isReader(self)

    def isAffectat(self):
        return utils.isAffectat(self)

    def isManager(self):
        return utils.isManager(self)

    def showEnviarButton(self):
        review_state = api.content.get_state(self.context)
        value = False
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] or self.isManager:
            value = True
        return value

    def showPresentacionButton(self):
        review_state = api.content.get_state(self.context)
        value = False
        if review_state in ['convocada', 'realitzada', 'en_correccio'] or self.isManager:
            value = True
        return value

    def showPublicarButton(self):
        review_state = api.content.get_state(self.context)
        value = False
        if review_state in ['realitzada', 'en_correccio'] or self.isManager:
            value = True
        return value

    def getColor(self, data):
        # assign custom colors on organ states
        estat = data.getObject().estatsLlista
        values = data.estatsLlista
        color = '#777777'
        for value in values.split('<br />'):
            if estat.decode('utf-8') == ' '.join(value.split(' ')[:-1]).rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' '):
                return value.split(' ')[-1:][0].rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' ')
        return color

    def estatsCanvi(self, data):
        values = data.estatsLlista
        items = []
        for value in values.split('<br />'):
            estat = ' '.join(value.split(' ')[:-1]).rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' ')
            items.append(estat)
        return items

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
            if obj.portal_type == 'genweb.organs.acta':
                # add actas to template for oredering but doesnt show
                item = obj.getObject()
                results.append(dict(id=obj.id,
                                    classe='hidden',
                                    show=False))
            else:
                item = obj.getObject()
                if len(item.objectIds()) > 0:
                    inside = True
                else:
                    inside = False
                results.append(dict(title=obj.Title,
                                    portal_type=obj.portal_type,
                                    absolute_url=item.absolute_url(),
                                    item_path=obj.getPath(),
                                    proposalPoint=item.proposalPoint,
                                    agreement=item.agreement,
                                    state=item.estatsLlista,
                                    css=self.getColor(obj),
                                    estats=self.estatsCanvi(obj),
                                    id=obj.id,
                                    show=True,
                                    classe="ui-state-grey",
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
                                item_path=obj.getPath(),
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

        results = []
        for obj in values:
            results.append(dict(title=obj.Title,
                                absolute_url=obj.getURL(),
                                date=obj.getObject().dataSessio.strftime('%d/%m/%Y')))
        return results

    def LogInformation(self):
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
        values = dict(dataSessio=self.context.dataSessio.strftime('%d/%m/%Y'),
                      horaInici=self.context.horaInici.strftime('%H:%M'),
                      horaFi=self.context.horaFi.strftime('%H:%M'),
                      llocConvocatoria=self.context.llocConvocatoria,
                      organTitle=self.OrganTitle(),
                      )
        return values

    def OrganTitle(self):
        """ Retorna el títol de l'òrgan
        """
        title = self.context.aq_parent.Title()
        return title

    def hihaMultimedia(self):
        if self.context.enllacVideo or self.context.enllacAudio:
            return True
        else:
            return False

    def hihaPersones(self):
        if self.context.membresConvocats or self.context.membresConvidats or self.context.llistaExcusats:
            return True
        else:
            return False

    def showActaTab(self):
        if self.hihaMultimedia() or self.ActesInside():
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
                    tipus = 'fa fa-file-pdf-o'
                    document = _(u'Fitxer intern')
                    labelClass = 'label label-danger'
                else:
                    tipus = 'fa fa-file-pdf-o'
                    document = _(u'Fitxer públic')
                    labelClass = 'label label-default'
            else:
                tipus = 'fa fa-file-text-o'
                document = _(u'Document')
                labelClass = 'label label-default'
            results.append(dict(title=obj.Title,
                                portal_type=obj.portal_type,
                                absolute_url=obj.getURL(),
                                classCSS=tipus,
                                hidden=obj.hiddenfile,
                                labelClass=labelClass,
                                content=document,
                                id=str(item['id']) + '/' + obj.id))
        return results

    def filesinsideSubPunt(self, item):
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + item['id']

        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file', 'genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 2})
        results = []
        for obj in values:
            if obj.portal_type == 'genweb.organs.file':
                if obj.hiddenfile is True:
                    tipus = 'fa fa-file-pdf-o'
                    document = _(u'Fitxer intern')
                    labelClass = 'label label-danger'
                else:
                    tipus = 'fa fa-file-pdf-o'
                    document = _(u'Fitxer públic')
                    labelClass = 'label label-default'
            else:
                tipus = 'fa fa-file-text-o'
                document = _(u'Document')
                labelClass = 'label label-default'

            results.append(dict(title=obj.Title,
                                portal_type=obj.portal_type,
                                absolute_url=obj.getURL(),
                                classCSS=tipus,
                                hidden=obj.hiddenfile,
                                labelClass=labelClass,
                                content=document,
                                id=str(item['id']) + '/' + obj.id))
        return results
