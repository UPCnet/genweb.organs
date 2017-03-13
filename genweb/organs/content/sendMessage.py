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
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from zope import schema
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from genweb.organs.utils import addEntryLog
from AccessControl import Unauthorized
import unicodedata

grok.templatedir("templates")


class IMessage(form.Schema):

    sender = TextLine(
        title=_("Sender"),
        description=_("Sender organ help"),
        required=False,
        )

    recipients = TextLine(
        title=_("Recipients"),
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
    grok.name('mail_message')
    grok.context(ISessio)
    grok.template("message_view")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    ignoreContext = True
    schema = IMessage

    # Disable the view if no roles in username
    def update(self):
        """ Return true if user is Editor or Manager """
        username = api.user.get_current().getId()
        if username:
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Editor' in roles or 'Manager' in roles:
                self.request.set('disable_border', True)
                super(Message, self).update()
            else:
                raise Unauthorized
        else:
            raise Unauthorized

    def updateWidgets(self):
        super(Message, self).updateWidgets()
        organ = self.context.aq_parent
        self.widgets["sender"].mode = DISPLAY_MODE
        self.widgets["sender"].value = str(organ.fromMail)
        self.widgets["recipients"].value = self.context.adrecaLlista

        session = self.context
        sessiontitle = str(session.Title())

        if session.start is None:
            sessiondate = ''
        else:
            sessiondate = str(session.start.strftime("%d/%m/%Y"))

        titleText = "Missatge de la sessió: " + sessiontitle + ' (' + sessiondate + ')'
        fromMessage = unicodedata.normalize('NFKD', titleText.decode('utf-8'))
        self.widgets["fromTitle"].value = fromMessage
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

        sender = self.context.aq_parent.fromMail
        user = api.user.get_current().getId()
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

            addEntryLog(self.context, user, _(u'Sending mail new message'), formData['recipients'])
            self.context.plone_utils.addPortalMessage(
                _("Missatge enviat correctament"), 'info')
        except:
            addEntryLog(self.context, user, _(u'Missatge no enviat'), formData['recipients'])
            self.context.plone_utils.addPortalMessage(
                _("Missatge no enviat. Comprovi els destinataris del missatge"), 'error')

        return self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
