# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from z3c.form import form
from plone.event.interfaces import IEventAccessor
from time import strftime
from z3c.form import button
from z3c.form.interfaces import DISPLAY_MODE
from zope import schema
from zope.i18n import translate
from zope.schema import TextLine

from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs.utils import addEntryLog
from genweb.organs import utils

import transaction
import unicodedata


class IMessage(form.Schema):
    """ Convocar la sessió: /mail_convocar
    """

    sender = TextLine(
        title=_("Sender"),
        description=_("Sender organ help"),
        required=False)

    recipients = TextLine(
        title=_(u"Recipients"),
        description=_("Mail address separated by blanks."),
        required=True)

    fromTitle = TextLine(
        title=_(u"From"),
        required=True)

    directives.widget(message=WysiwygFieldWidget)
    message = schema.Text(
        title=_(u"Message"),
        required=True,
    )

    directives.widget(membresConvocats=WysiwygFieldWidget)
    membresConvocats = schema.Text(
        title=_(u"Incoming members list"),
        description=_(u"Incoming members list help"),
        required=False,
    )

    directives.widget(membresConvidats=WysiwygFieldWidget)
    membresConvidats = schema.Text(
        title=_(u"Invited members"),
        description=_(u"Invited members help"),
        required=False,
    )

    adrecaAfectatsLlista = schema.Text(
        title=_(u"Stakeholders mail address"),
        description=_(u"Stakeholders mail address help."),
        required=False,
    )


class Message(form.SchemaForm):
    ignoreContext = True
    schema = IMessage

    # Disable the view if no roles in username
    def update(self):
        """  Disable the view if username has no roles.
             Send Message if user is Editor / Secretari / Manager """
        if api.user.is_anonymous() is True:
            raise Unauthorized
        else:
            username = api.user.get_current().id
            roles = api.user.get_roles(username=username, obj=self.context)
            if utils.checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles):
                self.request.set('disable_border', True)
                super(Message, self).update()
            else:
                raise Unauthorized

    def updateWidgets(self):
        super(Message, self).updateWidgets()
        session = self.context
        now = strftime("%d/%m/%Y %H:%M:%S")
        organ = self.context.aq_parent
        sessionLink = '----@@----' + session.absolute_url()

        if session.signatura is None:
            signatura = ''
        else:
            signatura = str(session.signatura.encode('utf-8'))

        if session.llocConvocatoria is None:
            place = ''
        else:
            place = str(session.llocConvocatoria.encode('utf-8'))

        if session.bodyMail is None:
            customBody = ''
        else:
            customBody = str(session.bodyMail.encode('utf-8'))

        html_content = ''
        sessiontitle = str(session.Title())

        acc = IEventAccessor(self.context)
        if acc.start is None:
            sessiondate = ''
        else:
            sessiondate = str(acc.start.strftime("%d/%m/%Y"))

        if acc.start is None:
            starthour = ''
        else:
            starthour = str(acc.start.strftime("%H:%M"))

        if acc.end is None:
            endHour = ''
        else:
            endHour = str(acc.end.strftime("%H:%M"))

        session.notificationDate = now
        lang = self.context.language
        if lang == 'ca':
            titleText = "Convocatòria " + sessiontitle + ' - ' + sessiondate + ' - ' + starthour
            fromMessage = unicodedata.normalize('NFKD', titleText.decode('utf-8'))
            introData = "<p>Podeu consultar la convocatòria i la documentació de la sessió aquí: <a href=" + \
                        sessionLink + ">" + sessiontitle + "</a></p>" +\
                        "<p>Podeu excusar l'absència a la sessió aquí: <a href=" +\
                        sessionLink + "/excusar_assist_sessio>Excusar l'absència</a></p><br/> " + signatura

            moreData = html_content + '<br/>' + customBody + '<strong>' + sessiontitle + '</strong>'

            if session.modality is not None:
                moreData += "<br/>Modalitat de la sessió: " + translate(msgid=session.modality, domain='genweb.organs', target_language='ca')

            moreData += '<br/>Lloc: ' + place

            if session.linkSala is not None:
                moreData += "<br/>Enllaç a la sessió: <a href='" + session.linkSala + "' target='_blank'>" + session.linkSala + "</a>"

            moreData += "<br/>Data: " + sessiondate + \
                "<br/>Hora d'inici: " + starthour + \
                "<br/>Hora de fi: " + endHour + \
                '<br/>'
            bodyMail = str(moreData) + str(introData)

        if lang == 'es':
            titleText = "Convocatoria " + sessiontitle + ' - ' + sessiondate + ' - ' + starthour
            fromMessage = unicodedata.normalize('NFKD', titleText.decode('utf-8'))
            introData = "<p>Puede consultar la convocatoria y la documentación de la sesión aquí: <a href=" + \
                        sessionLink + ">" + sessiontitle + "</a></p>" +\
                        "<p>Puedes escusar tu ausencia a la sesión aquí: <a href=" +\
                        sessionLink + "/excusar_assist_sessio>Escusar ausencia</a></p><br/> " + signatura

            moreData = html_content + '<br/>' + customBody + '<strong>' + sessiontitle + '</strong>'

            if session.modality is not None:
                "<br/>Modalidad de la sesión: " + translate(msgid=session.modality, domain='genweb.organs', target_language='es')

            moreData += '<br/>Lugar: ' + place

            if session.linkSala is not None:
                moreData += "<br/>Enlace a la sesión: <a href='" + session.linkSala + "' target='_blank'>" + session.linkSala + "</a>"

            moreData += "<br/>Fecha: " + sessiondate + \
                "<br/>Hora de inicio: " + starthour + \
                "<br/>Hora de finalización: " + endHour + \
                '<br/>'
            bodyMail = str(moreData) + str(introData)

        if lang == 'en':
            titleText = "Call " + sessiontitle + ' - ' + sessiondate + ' - ' + starthour
            fromMessage = unicodedata.normalize('NFKD', titleText.decode('utf-8'))
            introData = "<p>Information regarding the call and the documentation can be found here: <a href=" + \
                        sessionLink + ">" + sessiontitle + "</a></p>" +\
                        "<p>You can apologise for you absence here: <a href=" +\
                        sessionLink + "/excusar_assist_sessio>apologise</a></p><br/> " + signatura

            moreData = html_content + '<br/>' + customBody + '<strong>' + sessiontitle + '</strong>'

            if session.modality is not None:
                moreData += "<br/>Session modality: " + translate(msgid=session.modality, domain='genweb.organs', target_language='en')

            moreData += '<br/>Place: ' + place

            if session.linkSala is not None:
                moreData += "<br/>Link to the session: <a href='" + session.linkSala + "' target='_blank'>" + session.linkSala + "</a>"

            moreData += "<br/>Date: " + sessiondate + \
                "<br/>Start date: " + starthour + \
                "<br/>End date: " + endHour + \
                '<br/>'
            bodyMail = str(moreData) + str(introData)

        self.widgets["sender"].mode = DISPLAY_MODE
        self.widgets["sender"].value = str(organ.fromMail) if organ.fromMail else ""
        self.widgets["fromTitle"].value = fromMessage
        self.widgets["recipients"].value = str(organ.adrecaLlista) if organ.adrecaLlista else ""
        self.widgets["message"].value = bodyMail

        self.widgets["membresConvocats"].value = str(organ.membresOrgan) if organ.membresOrgan else ""
        self.widgets["membresConvidats"].value = str(organ.convidatsPermanentsOrgan) if organ.convidatsPermanentsOrgan else ""
        self.widgets["adrecaAfectatsLlista"].value = str(organ.adrecaAfectatsLlista) if organ.adrecaAfectatsLlista else ""

    @button.buttonAndHandler(_("Send"))
    def action_send(self, action):
        """ Send the email to the configured mail address
            in properties and redirect to the
            front page, showing a status message to say
            the message was received. """
        formData, errors = self.extractData()
        lang = self.context.language
        if 'recipients' not in formData or 'fromTitle' not in formData or 'message' not in formData:
            if lang == 'ca':
                message = "Falten camps obligatoris: "
            if lang == 'es':
                message = "Faltan campos obligatorios: "
            if lang == 'en':
                message = "Required fields missing: "
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            return
        # replace hidden fields to maintain correct urls...
        body = formData['message'].replace('----@@----http:/', 'http://').replace('----@@----https:/', 'https://').encode('utf-8')

        root_url = api.portal.get().absolute_url() + "/" + lang
        body = body.replace('resolveuid/', root_url + "/resolveuid/")

        sender = self.context.aq_parent.fromMail
        try:
            self.context.MailHost.send(
                body,
                mto=formData['recipients'],
                mfrom=sender,
                subject=formData['fromTitle'],
                encode=None,
                immediate=False,
                charset='utf8',
                msg_type='text/html')

            api.content.transition(obj=self.context, transition='convocar')
            addEntryLog(self.context, None, _(u'Sending mail convocatoria'), formData['recipients'])
            self.context.plone_utils.addPortalMessage(
                _(u"Missatge enviat correctament"), 'info')
        except:
            addEntryLog(self.context, None, _(u'Missatge no enviat'), formData['recipients'])
            self.context.plone_utils.addPortalMessage(
                _(u"Missatge no enviat. Comprovi els destinataris del missatge"), 'error')

        session = self.context
        session.membresConvocats = formData['membresConvocats']
        session.membresConvidats = formData['membresConvidats']
        session.adrecaAfectatsLlista = formData['adrecaAfectatsLlista']
        session.adrecaLlista = formData['recipients']
        session.reindexObject()
        transaction.commit()

        return self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
