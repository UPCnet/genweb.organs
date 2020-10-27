# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from cgi import escape
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from five import grok
from plone import api
from plone.autoform import directives
from plone.directives import dexterity
from plone.directives import form
from zope import schema
from zope.schema import TextLine

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.content.acord import llistaEstatsVotacio
from genweb.organs.content.acord import llistaTipusVotacio

import ast
import datetime
import transaction


class IVotacioAcord(form.Schema):
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

    directives.omitted('infoVotacio')
    infoVotacio = schema.Text(title=u'', required=False, default=u'{}')


class Edit(dexterity.EditForm):
    grok.context(IVotacioAcord)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()


class VotacioAcordView(grok.View):
    grok.context(IVotacioAcord)
    grok.name('view')

    def render(self):
        self.template = ViewPageTemplateFile('templates/votacio_acord.pt')
        return self.template(self)

    def canView(self):
        # Permissions to view VOTACIOACORD
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
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
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
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                return True
            else:
                raise Unauthorized


class CloseVote(grok.View):
    grok.context(IVotacioAcord)
    grok.name('closeVote')
    grok.require('genweb.organs.manage.vote')

    def render(self):
        self.context.estatVotacio = 'close'
        self.context.reindexObject()
        transaction.commit()


class FavorVote(grok.View):
    grok.context(IVotacioAcord)
    grok.name('favorVote')
    grok.require('genweb.organs.add.vote')

    def render(self):
        if not isinstance(self.context.infoVotacio, dict):
            self.context.infoVotacio = ast.literal_eval(self.context.infoVotacio)

        user = api.user.get_current().id
        if user not in self.context.infoVotacio:
            self.context.infoVotacio.update({user: 'favor'})
            self.context.reindexObject()
            transaction.commit()
            sendVoteEmail(self.context, 'a favor')


class AgainstVote(grok.View):
    grok.context(IVotacioAcord)
    grok.name('againstVote')
    grok.require('genweb.organs.add.vote')

    def render(self):
        if not isinstance(self.context.infoVotacio, dict):
            self.context.infoVotacio = ast.literal_eval(self.context.infoVotacio)

        user = api.user.get_current().id
        if user not in self.context.infoVotacio:
            self.context.infoVotacio.update({user: 'against'})
            self.context.reindexObject()
            transaction.commit()
            sendVoteEmail(self.context, 'en contra')


class WhiteVote(grok.View):
    grok.context(IVotacioAcord)
    grok.name('whiteVote')
    grok.require('genweb.organs.add.vote')

    def render(self):
        if not isinstance(self.context.infoVotacio, dict):
            self.context.infoVotacio = ast.literal_eval(self.context.infoVotacio)

        user = api.user.get_current().id
        if user not in self.context.infoVotacio:
            self.context.infoVotacio.update({user: 'white'})
            self.context.reindexObject()
            transaction.commit()
            sendVoteEmail(self.context, 'en blanc')


def sendVoteEmail(context, vote):
    context = aq_inner(context)

    user_email = api.user.get_current().getProperty('email')
    if user_email:
        mailhost = getToolByName(context, 'MailHost')

        portal = api.portal.get()
        sender_email = portal.getProperty('email_from_address')
        sender_name = portal.getProperty('email_from_name').encode('utf-8')
        email_charset = portal.getProperty('email_charset')
        sender_name + ' ' + '<' + sender_email + '>'

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = escape(safe_unicode(_(u'Votació Govern UPC')))
        msg['charset'] = email_charset

        message = """En data {data}, hora {hora}, has votat {vot} l'esmena {esmena} de l'acord {acord} de la sessió {sessio} de l'òrgan {organ}.

Missatge automàtic generat per https://govern.upc.edu/"""

        now = datetime.datetime.now()
        if context.aq_parent.portal_type == 'genweb.organs.sessio':

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

        elif context.aq_parent.portal_type == 'genweb.organs.punt':

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


class RemoveVote(grok.View):
    grok.context(IVotacioAcord)
    grok.name('removeVote')
    grok.require('genweb.organs.manage.vote')

    def render(self):
        parent = self.context.aq_parent
        parent.manage_delObjects([self.context.getId()])
        transaction.commit()
