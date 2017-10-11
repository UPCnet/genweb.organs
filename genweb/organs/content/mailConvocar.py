# -*- coding: utf-8 -*-
from plone import api
from five import grok
from zope.schema import TextLine
from z3c.form import button
from plone.directives import form
from Products.statusmessages.interfaces import IStatusMessage
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from AccessControl import Unauthorized
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from zope import schema
from time import strftime
from z3c.form.interfaces import DISPLAY_MODE
from genweb.organs.utils import addEntryLog
from plone.event.interfaces import IEventAccessor
import unicodedata

grok.templatedir("templates")


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


class Message(form.SchemaForm):
    grok.name('mail_convocar')
    grok.context(ISessio)
    grok.template("mail_convocar")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    ignoreContext = True
    schema = IMessage

    # Disable the view if no roles in username
    def update(self):
        """ Return true if user is Editor or Manager """
        username = api.user.get_current().id
        if username:
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'OG2-Editor' in roles or 'OG1-Secretari' in roles or 'Manager' in roles:
                self.request.set('disable_border', True)
                super(Message, self).update()
            else:
                raise Unauthorized
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
            introData = "<br/><p>Podeu consultar la convocatòria i la documentació de la sessió aquí: <a href=" + \
                        sessionLink + ">" + sessiontitle + "</a></p><br/>" + signatura
            moreData = html_content + \
                '<br/>' + customBody + '<strong>' + sessiontitle + \
                '</strong><br/><br/>Lloc: ' + place + "<br/>Data: " + sessiondate + \
                "<br/>Hora d'inici: " + starthour + \
                "<br/>Hora de fi: " + endHour + \
                '<br/><br/>'
            bodyMail = str(moreData) + str(introData)

        if lang == 'es':
            titleText = "Convocatoria " + sessiontitle + ' - ' + sessiondate + ' - ' + starthour
            fromMessage = unicodedata.normalize('NFKD', titleText.decode('utf-8'))
            introData = "<br/><p>Puede consultar la convocatoria y la documentación de la sesión aquí: <a href=" + \
                        sessionLink + ">" + sessiontitle + "</a></p><br/>" + signatura
            moreData = html_content + \
                '<br/>' + customBody + '<strong>' + sessiontitle + \
                '</strong><br/><br/>Lugar: ' + place + "<br/>Fecha: " + sessiondate + \
                "<br/>Hora de inicio: " + starthour + \
                "<br/>Hora de finalización: " + endHour + \
                '<br/><br/>'
            bodyMail = str(moreData) + str(introData)

        if lang == 'en':
            titleText = "Call " + sessiontitle + ' - ' + sessiondate + ' - ' + starthour
            fromMessage = unicodedata.normalize('NFKD', titleText.decode('utf-8'))
            introData = "<br/><p>Information regarding the call and the documentation can be found here: <a href=" + \
                        sessionLink + ">" + sessiontitle + "</a></p><br/>" + signatura
            moreData = html_content + \
                '<br/>' + customBody + '<strong>' + sessiontitle + \
                '</strong><br/><br/>Place: ' + place + "<br/>Date: " + sessiondate + \
                "<br/>Start date: " + starthour + \
                "<br/>End date: " + endHour + \
                '<br/><br/>'
            bodyMail = str(moreData) + str(introData)

        self.widgets["sender"].mode = DISPLAY_MODE
        self.widgets["sender"].value = str(organ.fromMail)
        self.widgets["fromTitle"].value = fromMessage
        self.widgets["recipients"].value = str(session.adrecaLlista)
        self.widgets["message"].value = bodyMail

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

        return self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
