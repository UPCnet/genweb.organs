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
from AccessControl import Unauthorized
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from genweb.organs.utils import addEntryLog

from zope import schema

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
        required=False)

    directives.widget(message=WysiwygFieldWidget)
    message = schema.Text(
        title=_(u"Message"),
        description=_("This content will be used as message content"),
        required=False,
    )


class Message(form.SchemaForm):
    grok.name('informar_sessio')
    grok.context(ISessio)
    grok.template("informar_view")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    ignoreContext = True

    schema = IMessage

    def updateWidgets(self):
        super(Message, self).updateWidgets()
        organ = self.context.aq_parent
        self.widgets["sender"].mode = DISPLAY_MODE
        self.widgets["sender"].value = str(organ.fromMail)
        session = self.context
        if session.adrecaAfectatsLlista:
            self.widgets["recipients"].value = str(session.adrecaLlista) + ' ' + str(session.adrecaAfectatsLlista)
        else:
            self.widgets["recipients"].value = str(session.adrecaLlista)

        lang = self.context.language
        if lang == 'ca':
            text = 'Enllaç a la sessió: '
        if lang == 'es':
            text = 'Enlace a la sessión: '
        if lang == 'en':
            text = 'Link to this session: '
        else:
            text = 'Enllaç a la sessió: '
        self.widgets["message"].value = text + '<a href="' + self.context.absolute_url() + '"> ' + self.context.Title() + ' </a>'

    @button.buttonAndHandler(_("Send"))
    def action_send(self, action):
        """ Send the email to the configured mail address
            in properties and redirect to the
            front page, showing a status message to say
            the message was received. """
        emptyfields = []
        formData, errors = self.extractData()
        lang = self.context.language

        if 'recipients' not in formData or 'message' not in formData:
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
        sender = self.context.aq_parent.fromMail
        addEntryLog(self.context, sender, _(u'Sending mail informar sessio'), toMail)
        sessio_sendMail(self.context, toMail, body)  # Send mail

        return self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
