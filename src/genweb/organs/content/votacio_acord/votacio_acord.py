# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from html import escape
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from plone import api
from plone.autoform import directives
from z3c.form import form
from zope import schema
from zope.schema import TextLine
from plone.supermodel import model

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.content.acord.acord import llistaEstatsVotacio
from genweb.organs.content.acord.acord import llistaTipusVotacio
from genweb.organs.utils import addEntryLog
from genweb.organs.utils import checkHasOpenVote

import ast
import datetime
import json
import transaction


class IVotacioAcord(model.Schema):
    """ Enviar missatge als membres /mail_message
    """
    title = TextLine(
        title=_("Titol votacio"),
        required=True
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


class Edit(form.EditForm):

    def updateWidgets(self):
        super(Edit, self).updateWidgets()


class VotacioAcordView(BrowserView):

    def render(self):
        self.template = ViewPageTemplateFile('votacio_acord.pt')
        return self.template(self)

    def canView(self):
        # Permissions to view VOTACIOACORD
        # If manager Show all
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)

        if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
            return True
        elif estatSessio in ['convocada', 'realitzada', 'tancada', 'en_correccio'] and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre'], roles):
            return True
        else:
            raise Unauthorized


class ReopenVote(BrowserView):

    def __call__(self):
        if checkHasOpenVote(self.context):
            return json.dumps({"status": 'error', "msg": _(u'Ja hi ha una votació oberta, no se\'n pot obrir una altra.')})

        if self.context.estatVotacio == 'close':
            self.context.estatVotacio = 'open'
            self.context.reindexObject()
            transaction.commit()
            addEntryLog(self.context.__parent__.__parent__, None, _(u'Reoberta votacio esmena'), self.context.__parent__.absolute_url())
            return json.dumps({"status": 'success', "msg": ''})


class CloseVote(BrowserView):

    def __call__(self):
        self.context.estatVotacio = 'close'
        self.context.horaFiVotacio = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        self.context.reindexObject()
        transaction.commit()
        addEntryLog(self.context.__parent__.__parent__, None, _(u'Tancada votacio esmena'), self.context.__parent__.absolute_url())


class FavorVote(BrowserView):

    def __call__(self):
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

    def __call__(self):
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

    def __call__(self):
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

        message = """En data {data}, hora {hora}, has votat {vot} l'esmena {esmena} de l'acord {acord} de la sessió {sessio} de l'òrgan {organ}.

Missatge automàtic generat per https://govern.upc.edu/"""

        now = datetime.datetime.now()
        if context.aq_parent.aq_parent.portal_type == 'genweb.organs.sessio':

            data = {
                'data': now.strftime("%d/%m/%Y"),
                'hora': now.strftime("%H:%M"),
                'vot': vote,
                'esmena': context.title,
                'acord': context.aq_parent.title,
                'sessio': context.aq_parent.aq_parent.title,
                'organ': context.aq_parent.aq_parent.aq_parent.title,
            }

            msg.attach(MIMEText(message.format(**data), 'plain', email_charset))
            mailhost.send(msg)

        elif context.aq_parent.aq_parent.portal_type == 'genweb.organs.punt':

            data = {
                'data': now.strftime("%d/%m/%Y"),
                'hora': now.strftime("%H:%M"),
                'vot': vote,
                'esmena': context.title,
                'acord': context.aq_parent.title,
                'sessio': context.aq_parent.aq_parent.aq_parent.title,
                'organ': context.aq_parent.aq_parent.aq_parent.aq_parent.title,
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
    if isinstance(infoVotacio, str):
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

        message = """En data {data}, hora {hora}, la votació de l'esmena {esmena} de l'acord {acord} de la sessió {sessio} de l'òrgan {organ} ha estat anul·lada i el teu vot emès ha estat eliminat.

    Missatge automàtic generat per https://govern.upc.edu/"""

        now = datetime.datetime.now()
        if context.aq_parent.aq_parent.portal_type == 'genweb.organs.sessio':

            data = {
                'data': now.strftime("%d/%m/%Y"),
                'hora': now.strftime("%H:%M"),
                'esmena': context.title,
                'acord': context.aq_parent.title,
                'sessio': context.aq_parent.aq_parent.title,
                'organ': context.aq_parent.aq_parent.aq_parent.title,
            }

            msg.attach(MIMEText(message.format(**data), 'plain', email_charset))
            mailhost.send(msg)

        elif context.aq_parent.aq_parent.portal_type == 'genweb.organs.punt':

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
    
    def __call__(self):
        estatSessio = utils.session_wf_state(self)
        if estatSessio not in ['realitzada', 'tancada', 'en_correccio']:
            sendRemoveVoteEmail(self.context)

        parent = self.context.aq_parent
        parent.manage_delObjects([self.context.getId()])
        transaction.commit()
        addEntryLog(self.context.__parent__.__parent__, None, _(u'Eliminada votacio esmena'), self.context.__parent__.absolute_url())
