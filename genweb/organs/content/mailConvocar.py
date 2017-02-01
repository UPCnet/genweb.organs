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
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from genweb.organs.utils import addEntryLog

grok.templatedir("templates")


class IMessage(form.Schema):
    """ Define the fields of this form
    """
    sender = TextLine(
        title=_("Sender"),
        required=True,
        )

    recipients = TextLine(
        title=_("Recipients"),
        description=_("Mail address separated by commas."),
        required=True)

    fromTitle = TextLine(
        title=_("From"),
        required=True)

    directives.widget(message=WysiwygFieldWidget)
    message = schema.Text(
        title=_(u"Message"),
        required=False,
    )


class Message(form.SchemaForm):
    grok.name('mailConvocar')
    grok.context(ISessio)
    grok.template("mail_convocar")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    ignoreContext = True

    schema = IMessage

    def updateWidgets(self):
        super(Message, self).updateWidgets()
        session = self.context
        now = strftime("%d/%m/%Y %H:%M:%S")
        organ = self.context.aq_parent
        sessionLink = str(session.absolute_url())
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
        if session.dataSessio:
            sessiondate = str(session.dataSessio.strftime("%d/%m/%Y"))
        else:
            sessiondate = ''
        if session.horaInici:
            starthour = str(session.horaInici.strftime("%H:%M"))
        else:
            starthour = ''
        if session.horaFi:
            endHour = str(session.horaFi.strftime("%H:%M"))
        else:
            endHour = ''

        session.notificationDate = now
        fromMessage = "Convocatoria " + sessiontitle + ' - ' + sessiondate + ' - ' + starthour
        introData = "<br/><p>Podeu consultar tota la documentació de la sessió aquí: <a href=" + \
                    sessionLink + ">" + sessiontitle + "</a></p><br/>" + signatura
        moreData = html_content + \
            '<br/>' + customBody + '<strong>' + sessiontitle + \
            '</strong><br/><br/>Lloc: ' + place + "<br/>Data: " + sessiondate + \
            "<br/>Hora d'inici: " + starthour + \
            "<br/>Hora de fi: " + endHour + \
            '<br/><br/>'
        bodyMail = str(moreData) + str(introData)

        self.widgets["sender"].mode = DISPLAY_MODE
        self.widgets["sender"].value = str(organ.fromMail)
        self.widgets["fromTitle"].value = str(fromMessage)
        if session.adrecaAfectatsLlista:
            self.widgets["recipients"].value = str(session.adrecaLlista) + ' ' + str(session.adrecaAfectatsLlista)
        else:
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
        if 'recipients' not in formData or 'fromTitle' not in formData:
            if lang == 'ca':
                message = "Falten camps obligatoris: "
            if lang == 'es':
                message = "Faltan campos obligatorios: "
            if lang == 'en':
                message = "Required fields missing: "
            IStatusMessage(self.request).addStatusMessage(message, type="error")
            return
        sender = self.context.aq_parent.fromMail
        try:
            self.context.MailHost.send(
                formData['message'],
                mto=formData['recipients'],
                mfrom=sender,
                subject=formData['fromTitle'],
                encode=None,
                immediate=False,
                charset='utf8',
                msg_type='text/html')

            addEntryLog(self.context, None, _(u'Sending mail convocatoria'), formData['recipients'])
            self.context.plone_utils.addPortalMessage(
                _("Missatge enviat correctament"), 'info')
        except:
            addEntryLog(self.context, None, _(u'Missatge no enviat'), formData['recipients'])
            self.context.plone_utils.addPortalMessage(
                _("Missatge no enviat. Comprovi els destinataris del missatge"), 'error')

        return self.request.response.redirect(self.context.absolute_url())
