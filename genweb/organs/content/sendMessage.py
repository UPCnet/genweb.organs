# -*- coding: utf-8 -*-
from plone import api
from five import grok
from datetime import datetime
from zope.schema import TextLine
from z3c.form import button
from plone.directives import form
from Products.statusmessages.interfaces import IStatusMessage
from genweb.organs.interfaces import IGenwebOrgansLayer
from plone.app.textfield import RichText
from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from zope.annotation.interfaces import IAnnotations
from genweb.organs.browser.views import sessio_sendMail
from AccessControl import Unauthorized

grok.templatedir("send_templates")


class IMessage(form.Schema):
    """ Define the fields of this form
    """

    recipients = TextLine(
        title=_("Recipients"),
        description=_("Mail address separated by commas."),
        required=False)

    message = RichText(
        title=_('Message'),
        description=_("This content will be used as message content"),
        required=False)


class Message(form.SchemaForm):
    grok.name('send_message')
    grok.context(ISessio)
    grok.template("message_view")
    grok.require('zope2.View')
    grok.layer(IGenwebOrgansLayer)

    ignoreContext = True

    schema = IMessage

    # fields = field.Fields(IMessage)

    # This trick hides the editable border and tabs in Plone
    def update(self):
        """ Return true if user is Editor or Manager """
        try:
            username = api.user.get_current().getId()
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Editor' in roles or 'Manager' in roles:
                self.request.set('disable_border', True)
                super(Message, self).update()
            else:
                raise Unauthorized
        except:
            raise Unauthorized

    def updateWidgets(self):
        super(Message, self).updateWidgets()
        self.widgets["recipients"].value = self.context.adrecaLlista

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

        """ Adding send mail information to context in annotation format
        """
        KEY = 'genweb.organs.logMail'
        annotations = IAnnotations(self.context)

        if annotations is not None:
            logData = annotations.get(KEY, None)
            try:
                len(logData)
                # Get data and append values
                data = annotations.get(KEY)
            except:
                # If it's empty, initialize data
                data = []
            dateMail = datetime.now()

            anon = api.user.is_anonymous()
            if not anon:
                username = api.user.get_current().id
            else:
                username = ''

            toMessage = formData['recipients'].encode('utf-8').decode('ascii', 'ignore')
            noBlanks = ' '.join(toMessage.split())
            toMail = noBlanks.replace(' ', ',')

            body = str(formData['message'].output.encode('utf-8'))

            values = dict(dateMail=dateMail,
                          fromMail=_("Missatge enviat per: ") + username,
                          toMail=toMail)

            data.append(values)
            annotations[KEY] = data

            sessio_sendMail(self.context, toMail, body)  # Send mail

        return self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
