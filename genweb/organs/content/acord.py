# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from cgi import escape
from collective import dexteritytextindexer
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from plone import api
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from plone.dexterity.utils import createContentInContainer
from z3c.form import form
from plone.indexer import indexer
from plone.supermodel.directives import fieldset
from z3c.form.interfaces import IAddForm
from zope import schema
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from plone.supermodel import model

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.content.sessio import ISessio
from genweb.organs.utils import addEntryLog
from genweb.organs.firma_documental.utils import UtilsFirmaDocumental
from genweb.organs.utils import checkHasOpenVote

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import ast
import datetime
import json
import transaction
import unicodedata


def llistaEstats(context):
    """ Create vocabulary from Estats Organ. """
    terms = []
    # Els ACORDS NOMES van dintre de sessio o de punt
    # Al ser acord he de mirar si està dintre d'una sessio o d'un punt

    # En mode add or en mode edit, mirar 1nivell(SESSIO) o 2nivells(PUNT)
    if context.aq_parent.portal_type == 'genweb.organs.sessio' or context.portal_type == 'genweb.organs.sessio':
        values = context.aq_parent.estatsLlista
    if context.aq_parent.portal_type == 'genweb.organs.punt' or context.portal_type == 'genweb.organs.punt':
        values = context.aq_parent.aq_parent.estatsLlista

    literals = []
    for value in values.split('</p>'):
        if value != '':
            item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
            estat = ' '.join(item_net.split()[:-1]).lstrip().encode('utf-8')
            literals.append(estat)

    for item in literals:
        if isinstance(item, str):
            flattened = unicodedata.normalize('NFKD', item.decode('utf-8')).encode('ascii', errors='ignore')
        else:
            flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')
        terms.append(SimpleVocabulary.createTerm(item, flattened, item))

    return SimpleVocabulary(terms)


directlyProvides(llistaEstats, IContextSourceBinder)


llistaEstatsVotacio = SimpleVocabulary(
    [SimpleTerm(value=u'open', title=_(u'Open')),
     SimpleTerm(value=u'close', title=_(u'Close'))]
)

llistaTipusVotacio = SimpleVocabulary(
    [SimpleTerm(value=u'public', title=_(u'Public')),
     SimpleTerm(value=u'secret', title=_(u'Secret'))]
)

# Define la función defaultFactory para el campo 'proposalPoint'
def proposal_point_default_factory(context):
    """Genera el valor predeterminado para el campo 'proposalPoint'."""
    portal_catalog = api.portal.get_tool(name='portal_catalog')
    path_url = context.getPhysicalPath()[1:]
    folder_path = "/" + "/".join(path_url)

    values = portal_catalog.searchResults(
        portal_type=['genweb.organs.punt', 'genweb.organs.acord', 'genweb.organs.subpunt'],
        path={'query': folder_path, 'depth': 1}
    )
    subpunt_id = len(values) + 1

    if context.portal_type == 'genweb.organs.sessio':
        return str(subpunt_id)
    else:
        punt_id = getattr(context, 'proposalPoint', 1) or 1
        return f"{punt_id}.{subpunt_id}"

class IAcord(model.Schema):
    """ Acord """

    fieldset('acord',
             label=_(u'Tab acord'),
             fields=['title', 'proposalPoint', 'agreement', 'defaultContent', 'estatsLlista']
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Acord Title'),
        required=True
    )
    directives.mode(proposalPoint='hidden')
    proposalPoint = schema.TextLine(
        title=_(u'Proposal point number'),
        required=False,
        defaultFactory=proposal_point_default_factory
    )

    directives.mode(agreement='hidden')
    dexteritytextindexer.searchable('agreement')
    agreement = schema.TextLine(
        title=_(u'Agreement number'),
        required=False,
    )

    directives.omitted('omitAgreement')
    omitAgreement = schema.Bool(
        title=_(u'Omit Agreement number'),
        required=False,
        default=False
    )

    directives.widget(defaultContent=WysiwygFieldWidget)
    dexteritytextindexer.searchable('defaultContent')
    defaultContent = schema.Text(
        title=_(u"Proposal description"),
        required=False,
    )

    estatsLlista = schema.Choice(
        title=_(u"Agreement and document label"),
        source=llistaEstats,
        required=True,
    )

    directives.omitted('estatVotacio')
    estatVotacio = schema.Choice(title=u'', source=llistaEstatsVotacio, required=False)

    directives.omitted('tipusVotacio')
    tipusVotacio = schema.Choice(title=u'', source=llistaTipusVotacio, required=False)

    directives.omitted('horaIniciVotacio')
    horaIniciVotacio = schema.Text(title=u'', required=False)

    directives.omitted('horaFiVotacio')
    horaFiVotacio = schema.Text(title=u'', required=False)

    directives.omitted('infoVotacio')
    infoVotacio = schema.Text(title=u'', required=False, default=u'{}')


# @form.default_value(field=IAcord['proposalPoint'])
# def proposalPointDefaultValue(data):
#     # assign default proposalPoint value to Punt
#     portal_catalog = api.portal.get_tool(name='portal_catalog')
#     path_url = data.context.getPhysicalPath()[1:]
#     folder_path = ""
#     for path in path_url:
#         folder_path += '/' + path

#     values = portal_catalog.searchResults(
#         portal_type=['genweb.organs.punt', 'genweb.organs.acord', 'genweb.organs.subpunt'],
#         path={'query': folder_path,
#               'depth': 1})
#     subpunt_id = int(len(values)) + 1
#     if data.context.portal_type == 'genweb.organs.sessio':
#         return subpunt_id
#     else:
#         if data.context.proposalPoint is None:
#             data.context.proposalPoint = 1
#             punt_id = 1
#         else:
#             punt_id = data.context.proposalPoint
#         return str(punt_id) + '.' + str(subpunt_id)


@indexer(IAcord)
def proposalPoint(obj):
    return obj.proposalPoint


@indexer(IAcord)
def agreement(obj):
    return obj.agreement


@indexer(IAcord)
def estatVotacio(obj):
    return obj.estatVotacio


class Edit(form.EditForm):
    def updateWidgets(self):
        super(Edit, self).updateWidgets()


class View(BrowserView, UtilsFirmaDocumental):
    index = ViewPageTemplateFile("templates/acord_view.pt")
    def __call__(self):
        return self.index()

    def canViewVotacionsInside(self):
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        estatSessio = utils.session_wf_state(self)
        if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
            return True
        elif estatSessio in ['convocada', 'realitzada', 'tancada', 'en_correccio'] and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre'], roles):
            return True
        else:
            return False

    def VotacionsInside(self):
        if self.canViewVotacionsInside():
            portal_catalog = api.portal.get_tool(name='portal_catalog')
            folder_path = '/'.join(self.context.getPhysicalPath())
            values = portal_catalog.unrestrictedSearchResults(
                portal_type=['genweb.organs.votacioacord'],
                sort_on='getObjPositionInParent',
                path={'query': folder_path,
                      'depth': 1})

            results = []
            for obj in values:
                results.append(dict(title=obj.Title,
                                    absolute_url=obj.getURL()))
            return results
        return []

    def FilesandDocumentsInside(self):
        return utils.FilesandDocumentsInside(self)

    def getColor(self):
        # assign custom colors on organ states
        estat = self.context.estatsLlista
        values = self.context.aq_parent.aq_parent.estatsLlista
        color = '#777777'
        for value in values.split('</p>'):
            if value != '':
                item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
                if isinstance(estat, bytes):
                    estat = estat.decode('utf-8')
                if estat == ' '.join(item_net.split()[:-1]).lstrip():
                    return item_net.split(' ')[-1:][0].rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' ')
        return color

    def AcordTitle(self):
        if self.context.agreement:
            return _(u'[Acord ') + self.context.agreement + ']'
        else:
            return _(u'[Acord sense numeracio]') if not getattr(self.context, 'omitAgreement', False) else ''

    def canView(self):
        # Permissions to view ACORDS. Poden estar a 1 i 2 nivells
        # If manager Show all
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
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


class OpenPublicVote(BrowserView):
    def render(self):
        self.context.estatVotacio = 'open'
        self.context.tipusVotacio = 'public'
        self.context.horaIniciVotacio = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        self.context.reindexObject()
        transaction.commit()
        addEntryLog(self.context.__parent__, None, _(u'Oberta votacio acord'), self.context.absolute_url())


class OpenOtherPublicVote(BrowserView):
    def render(self):
        if 'title' in self.request.form and self.request.form['title'] and self.request.form['title'] != '':
            item = createContentInContainer(self.context, "genweb.organs.votacioacord", title=self.request.form['title'])
            item.estatVotacio = 'open'
            item.tipusVotacio = 'public'
            item.horaIniciVotacio = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            item.reindexObject()
            transaction.commit()
            addEntryLog(self.context.__parent__, None, _(u'Oberta votacio esmena'), self.context.absolute_url())


# class OpenSecretVote(BrowserView):
#     def render(self):
#         self.context.estatVotacio = 'open'
#         self.context.tipusVotacio = 'secret'
#         self.context.horaIniciVotacio = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
#         self.context.reindexObject()
#         transaction.commit()


# class OpenSecretPublicVote(BrowserView):
#     def render(self):
#         if 'title' in self.request.form and self.request.form['title'] and self.request.form['title'] != '':
#             item = createContentInContainer(self.context, "genweb.organs.votacioacord", title=self.request.form['title'])
#             item.estatVotacio = 'open'
#             item.tipusVotacio = 'secret'
#             item.horaIniciVotacio = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
#             item.reindexObject()
#             transaction.commit()


class ReopenVote(BrowserView):
    def render(self):
        if checkHasOpenVote(self.context):
            return json.dumps({"status": 'error', "msg": _(u'Ja hi ha una votació oberta, no se\'n pot obrir una altra.')})

        if self.context.estatVotacio == 'close':
            self.context.estatVotacio = 'open'
            self.context.reindexObject()
            transaction.commit()
            addEntryLog(self.context.__parent__, None, _(u'Reoberta votacio acord'), self.context.absolute_url())
            return json.dumps({"status": 'success', "msg": ''})


class CloseVote(BrowserView):
    def render(self):
        self.context.estatVotacio = 'close'
        self.context.horaFiVotacio = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        self.context.reindexObject()
        transaction.commit()
        addEntryLog(self.context.__parent__, None, _(u'Tancada votacio acord'), self.context.absolute_url())


class FavorVote(BrowserView):
    def render(self):
        if self.context.estatVotacio == 'close':
            return json.dumps({"status": 'error', "msg": _(u'La votació ja està tancada, el seu vot no s\'ha registrat.')})

        if not isinstance(self.context.infoVotacio, dict):
            self.context.infoVotacio = ast.literal_eval(self.context.infoVotacio)

        user = api.user.get_current().id
        self.context.infoVotacio.update({user: 'favor'})
        self.context.reindexObject()
        transaction.commit()
        sendVoteEmail(self.context, 'a favor')
        return json.dumps({"status": 'success', "msg": ''})

class AgainstVote(BrowserView):
    def render(self):
        if self.context.estatVotacio == 'close':
            return json.dumps({"status": 'error', "msg": _(u'La votació ja està tancada, el seu vot no s\'ha registrat.')})

        if not isinstance(self.context.infoVotacio, dict):
            self.context.infoVotacio = ast.literal_eval(self.context.infoVotacio)

        user = api.user.get_current().id
        self.context.infoVotacio.update({user: 'against'})
        self.context.reindexObject()
        transaction.commit()
        sendVoteEmail(self.context, 'en contra')
        return json.dumps({"status": 'success', "msg": ''})


class WhiteVote(BrowserView):
    def render(self):
        if self.context.estatVotacio == 'close':
            return json.dumps({"status": 'error', "msg": _(u'La votació ja està tancada, el seu vot no s\'ha registrat.')})

        if not isinstance(self.context.infoVotacio, dict):
            self.context.infoVotacio = ast.literal_eval(self.context.infoVotacio)

        user = api.user.get_current().id
        self.context.infoVotacio.update({user: 'white'})
        self.context.reindexObject()
        transaction.commit()
        sendVoteEmail(self.context, 'en blanc')
        return json.dumps({"status": 'success', "msg": ''})


def sendVoteEmail(context, vote):
    context = aq_inner(context)

    # /acl_users/plugins/manage_plugins?plugin_type=IPropertiesPlugin
    # Move the ldapUPC to the top of the active plugins.
    # Otherwise member.getProperty('email') won't work properly.

    user_email = api.user.get_current().getProperty('email')
    if user_email:
        mailhost = getToolByName(context, 'MailHost')

        portal = api.portal.get()
        email_charset = portal.getProperty('email_charset')

        organ = utils.get_organ(context)
        sender_email = organ.fromMail

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = escape(safe_unicode(_(u'Votació Govern UPC')))
        msg['charset'] = email_charset

        message = """En data {data}, hora {hora}, has votat {vot} a l'acord {acord} de la sessió {sessio} de l'òrgan {organ}.

Missatge automàtic generat per https://govern.upc.edu/"""

        now = datetime.datetime.now()
        if context.aq_parent.portal_type == 'genweb.organs.sessio':

            data = {
                'data': now.strftime("%d/%m/%Y"),
                'hora': now.strftime("%H:%M"),
                'vot': vote,
                'acord': context.title,
                'sessio': context.aq_parent.title,
                'organ': context.aq_parent.aq_parent.title,
            }

            msg.attach(MIMEText(message.format(**data), 'plain', email_charset))
            mailhost.send(msg)

        elif context.aq_parent.portal_type == 'genweb.organs.punt':

            data = {
                'data': now.strftime("%d/%m/%Y"),
                'hora': now.strftime("%H:%M"),
                'vot': vote,
                'acord': context.title,
                'sessio': context.aq_parent.aq_parent.title,
                'organ': context.aq_parent.aq_parent.aq_parent.title,
            }

            msg.attach(MIMEText(message.format(**data), 'plain', email_charset))
            mailhost.send(msg)


def sendRemoveVoteEmail(context):
    context = aq_inner(context)
    mailhost = getToolByName(context, 'MailHost')

    portal = api.portal.get()
    email_charset = portal.getProperty('email_charset')

    organ = utils.get_organ(context)
    sender_email = organ.fromMail

    user_emails = []

    infoVotacio = context.infoVotacio
    if isinstance(infoVotacio, str) or isinstance(infoVotacio, unicode):
        infoVotacio = ast.literal_eval(infoVotacio)

    for key, value in infoVotacio.items():
        try:
            email = api.user.get(username=key).getProperty('email')
            if email:
                user_emails.append(email)
        except:
            pass

    if user_emails:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['Bcc'] = ', '.join(user_emails)
        msg['Subject'] = escape(safe_unicode(_(u'Votació anul·lada Govern UPC')))
        msg['charset'] = email_charset

        message = """En data {data}, hora {hora}, la votació de l'acord {acord} de la sessió {sessio} de l'òrgan {organ} ha estat anul·lada i el teu vot emès ha estat eliminat.

    Missatge automàtic generat per https://govern.upc.edu/"""

        now = datetime.datetime.now()
        if context.aq_parent.portal_type == 'genweb.organs.sessio':

            data = {
                'data': now.strftime("%d/%m/%Y"),
                'hora': now.strftime("%H:%M"),
                'acord': context.aq_parent.title,
                'sessio': context.aq_parent.aq_parent.title,
                'organ': context.aq_parent.aq_parent.aq_parent.title,
            }

            msg.attach(MIMEText(message.format(**data), 'plain', email_charset))
            mailhost.send(msg)

        elif context.aq_parent.portal_type == 'genweb.organs.punt':

            data = {
                'data': now.strftime("%d/%m/%Y"),
                'hora': now.strftime("%H:%M"),
                'esmena': context.title,
                'acord': context.aq_parent.title,
                'sessio': context.aq_parent.aq_parent.aq_parent.title,
                'organ': context.aq_parent.aq_parent.aq_parent.aq_parent.title,
            }

            msg.attach(MIMEText(message.format(**data), 'plain', email_charset))
            mailhost.send(msg)


class RemoveVote(BrowserView):
    def render(self):
        estatSessio = utils.session_wf_state(self)
        if estatSessio not in ['realitzada', 'tancada', 'en_correccio']:
            sendRemoveVoteEmail(self.context)

        self.context.estatVotacio = None
        self.context.tipusVotacio = None
        self.context.infoVotacio = '{}'
        self.context.horaIniciVotacio = None
        self.context.horaFiVotacio = None
        self.context.reindexObject()
        transaction.commit()
        addEntryLog(self.context.__parent__, None, _(u'Eliminada votacio acord'), self.context.absolute_url())



class HideAgreement(BrowserView):
    def getSessio(self, context):
        for obj in aq_chain(context):
            if ISessio.providedBy(obj):
                return obj
        return None

    def canModify(self):
        sessio = self.getSessio(self.context)

        # If item is migrated, it can't be modified
        migrated_property = hasattr(sessio, 'migrated')
        if migrated_property:
            if sessio.migrated is True:
                return False

        # But if not migrated, check permissions...
        username = api.user.get_current().id
        roles = utils.getUserRoles(self, sessio, username)
        review_state = api.content.get_state(sessio)
        value = False
        if review_state in ['planificada', 'convocada', 'realitzada', 'en_correccio'] and 'OG1-Secretari' in roles:
            value = True
        if review_state in ['planificada', 'convocada', 'realitzada'] and 'OG2-Editor' in roles:
            value = True
        return value or 'Manager' in roles

    def render(self):
        if not self.canModify():
            raise Unauthorized

        self.context.agreement = ''
        self.context.omitAgreement = True
        self.context.reindexObject()
        transaction.commit()
        return {"message": "OK"}, 200


class ShowAgreement(BrowserView):
    def render(self):
        self.context.omitAgreement = False
        self.context.reindexObject()
        transaction.commit()
