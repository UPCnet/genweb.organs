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
from genweb.organs.browser.views import sessio_sendMail
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from zope import schema
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from genweb.organs.utils import addEntryLog

grok.templatedir("templates")


class IMessage(form.Schema):

    sender = TextLine(
        title=_("Sender"),
        description=_("Sender message help"),
        required=False,
        )

    recipients = TextLine(
        title=_("Recipients"),
        description=_("Mail address separated by blanks."),
        required=False)

    directives.widget(message=WysiwygFieldWidget)
    message = schema.Text(
        title=_(u"Message"),
        required=False,
    )


class Message(form.SchemaForm):
    grok.name('send_message')
    grok.context(ISessio)
    grok.template("message_view")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    ignoreContext = True
    schema = IMessage

    # fields = field.Fields(IMessage)

    def updateWidgets(self):
        super(Message, self).updateWidgets()
        username = api.user.get_current().getId()
        self.widgets["sender"].mode = DISPLAY_MODE
        self.widgets["sender"].value = str(username)
        self.widgets["recipients"].value = self.context.adrecaLlista
        if self.context.aq_parent.bodyMailSend is None:
            bodyMailOrgan = '<br/>'
        else:
            bodyMailOrgan = self.context.aq_parent.bodyMailSend + '<br/>'
        if self.context.signatura is None:
            footerOrgan = '<br/>'
        else:
            footerOrgan = self.context.signatura + '<br/>'
        self.widgets["message"].value = bodyMailOrgan + footerOrgan

    @button.buttonAndHandler(_("Send"))
    def action_send(self, action):
        """ Send the email to the configured mail address
            in properties and redirect to the
            front page, showing a status message to say
            the message was received. """
        emptyfields = []
        formData, errors = self.extractData()
        lang = self.context.language
        if formData['recipients'] is None or formData['message'] is None:
            if formData['recipients'] is None:
                if lang == 'ca':
                    emptyfields.append("Destinataris")
                elif lang == 'es':
                    emptyfields.append("Destinatarios")
                else:
                    emptyfields.append("Recipients")

            if formData['message'] is None:
                if lang == 'ca':
                    emptyfields.append("Missatge")
                elif lang == 'es':
                    emptyfields.append("Mensaje")
                else:
                    emptyfields.append("Message")

            empty = ', '.join(emptyfields) + '.'
            if lang == 'ca':
                message = "Falten camps obligatoris: "
            if lang == 'es':
                message = "Faltan campos obligatorios: "
            if lang == 'en':
                message = "Required fields missing: "
            IStatusMessage(self.request).addStatusMessage(message + empty, type="error")
            return

        """ Adding send mail information to context in annotation format """
        toMessage = formData['recipients'].encode('utf-8').decode('ascii', 'ignore')
        noBlanks = ' '.join(toMessage.split())
        toMail = noBlanks.replace(' ', ',')
        body = formData['message'].encode('utf-8')
        sender = api.user.get_current().getId()
        addEntryLog(self.context, sender, _(u'Sending mail new message'), toMail)
        sessio_sendMail(self.context, toMail, body)  # Send mail

        return self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
