# -*- coding: utf-8 -*-
from plone import api
from zope.schema import TextLine
from z3c.form import button
from z3c.form import form
from Products.statusmessages.interfaces import IStatusMessage
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import _
from genweb.organs.content.sessio import ISessio
from plone.autoform import directives
from zope import schema
from z3c.form.interfaces import DISPLAY_MODE
from genweb.organs.utils import addEntryLog
from AccessControl import Unauthorized
from plone.event.interfaces import IEventAccessor
from genweb.organs import utils
import unicodedata
from plone.supermodel import model
from plone.app.textfield import RichText as RichTextField


class IMessage(model.Schema):
    """ Enviar missatge als membres /mail_message
    """

    sender = TextLine(
        title=_("Sender"),
        description=_("Sender organ help"),
        required=False)

    recipients = TextLine(
        title=_("Recipients"),
        description=_("Mail address separated by blanks."),
        required=True)

    fromTitle = TextLine(
        title=_(u"From"),
        required=True)

    message = RichTextField(
        title=_(u"Message"),
        required=True,
    )


class Message(form.Form):
    ignoreContext = True
    schema = IMessage

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
        organ = self.context.aq_parent
        self.widgets["sender"].mode = DISPLAY_MODE
        self.widgets["sender"].value = str(organ.fromMail)
        self.widgets["recipients"].value = self.context.adrecaLlista

        session = self.context
        sessiontitle = str(session.Title())
        # TRICK: si hacemos el regexp normal, nos crea mal las urls.
        sessionLink = '----@@----' + session.absolute_url()

        acc = IEventAccessor(self.context)
        if acc.start is None:
            sessiondate = ''
        else:
            sessiondate = str(acc.start.strftime("%d/%m/%Y"))

        lang = self.context.language
        if lang == 'ca':
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
            introData = "<p>Podeu consultar la convocatòria i la documentació de la sessió aquí: <a href=" + \
                sessionLink + ">" + sessiontitle + "</a></p><br/>"

        if lang == 'es':
            titleText = "Mensaje de la sesión: " + sessiontitle + ' (' + sessiondate + ')'
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
            introData = "<p>Puede consultar la convocatoria y la documentación de la sesión aquí: <a href=" + \
                sessionLink + ">" + sessiontitle + "</a></p><br/>"

        if lang == 'en':
            titleText = "Message from session: " + sessiontitle + ' (' + sessiondate + ')'
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
            introData = "<p>Information regarding the call and the documentation can be found here: <a href=" + \
                sessionLink + ">" + sessiontitle + "</a></p><br/>"
        self.widgets["message"].value = bodyMailOrgan.encode('utf-8') + introData + footerOrgan.encode('utf-8')

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

        # Replace hidden fields to maintain correct urls...
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
                immediate=True,
                charset='utf8',
                msg_type='text/html')

            addEntryLog(self.context, None, _(u'Sending mail new message'), formData['recipients'])
            self.context.plone_utils.addPortalMessage(
                _("Missatge enviat correctament"), 'info')
        except:
            addEntryLog(self.context, None, _(u'Missatge no enviat'), formData['recipients'])
            self.context.plone_utils.addPortalMessage(
                _("Missatge no enviat. Comprovi els destinataris del missatge"), 'error')

        return self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_('Cancel'))
    def handleCancel(self, action):
        message = _(u"Operation Cancelled.")
        IStatusMessage(self.request).addStatusMessage(message, type="warning")
        return self.request.response.redirect(self.context.absolute_url())
