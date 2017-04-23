# -*- coding: utf-8 -*-
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
from z3c.form.interfaces import DISPLAY_MODE
from genweb.organs.utils import addEntryLog
from Products.CMFCore.utils import getToolByName
import unicodedata

from zope import schema

grok.templatedir("templates")


class IMessage(form.Schema):
    """ Define the fields of this form
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

    directives.widget(message=WysiwygFieldWidget)
    message = schema.Text(
        title=_(u"Message"),
        required=True,
    )


class Message(form.SchemaForm):
    grok.name('mail_informar')
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

        start = getattr(session, 'start', None)
        end = getattr(session, 'end', None)
        if start is None:
            sessiondate = ''
        else:
            sessiondate = start.strftime("%d/%m/%Y")
        if start is None:
            starthour = ''
        else:
            starthour = start.strftime("%H:%M")
        if end is None:
            endHour = ''
        else:
            endHour = end.strftime("%H:%M")
        organ = session.aq_parent

        if organ.footerMail is None:
            signatura = ''
        else:
            signatura = organ.footerMail.encode('utf-8')

        if session.llocConvocatoria is None:
            place = ''
        else:
            place = session.llocConvocatoria.encode('utf-8')

        lang = self.context.language
        sessiontitle = str(session.Title())

        titleText = _(u"Resultat. ") + sessiontitle + ' (' + sessiondate + ')'
        fromMessage = unicodedata.normalize('NFKD', titleText.decode('utf-8'))
        self.widgets["fromTitle"].value = fromMessage

        if lang == 'es':
            moreData = '<p><strong>' + sessiontitle + \
                '</strong><br/></p>Lugar: ' + place + "<br/>Data: " + sessiondate + \
                "<br/>Hora de inicio: " + starthour + \
                "<br/>Hora de fin: " + endHour + \
                '<br/><br/><p><strong> Resumen de la sesión </strong></p>'

        if lang == 'en':
            moreData = '<p><strong>' + sessiontitle + \
                '</strong><br/></p>Place: ' + place + "<br/>Data: " + sessiondate + \
                "<br/>Start date: " + starthour + \
                "<br/>End data: " + endHour + \
                '<br/><br/><p><strong> Sesison summary </strong></p>'
        else:
            # lang = ca or another...
            moreData = '<p><strong>' + sessiontitle + \
                '</strong><br/></p>Lloc: ' + place + "<br/>Data: " + sessiondate + \
                "<br/>Hora d'inici: " + starthour + \
                "<br/>Hora de fi: " + endHour + \
                '<br/><br/><p><strong> Resum de la sessió </strong></p>'

        self.widgets["message"].value = moreData + self.Punts2Acta() + '<br/>' + signatura

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

            addEntryLog(self.context, None, _(u'Sending mail informar sessio'), formData['recipients'])
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

    def PuntsOrdreDelDia(self):
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            portal_type='genweb.organs.punt',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            # value = obj.getObject()
            value = obj._unrestrictedGetObject()
            results.append(dict(Title=obj.Title,
                                url=value.absolute_url_path(),
                                punt=value.proposalPoint,
                                acord=value.agreement))
            if len(value.objectIds()) > 0:
                # valuesInside = portal_catalog.searchResults(
                valuesInside = portal_catalog.unrestrictedSearchResults(
                    portal_type='genweb.organs.subpunt',
                    sort_on='getObjPositionInParent',
                    path={'query': obj.getPath(),
                          'depth': 1})
                for item in valuesInside:
                    # subpunt = item.getObject()
                    subpunt = item._unrestrictedGetObject()
                    results.append(dict(Title=item.Title,
                                        url=subpunt.absolute_url_path(),
                                        punt=subpunt.proposalPoint,
                                        acord=subpunt.agreement))

        return results

    def Punts2Acta(self):
        """ Retorna els punt en format text per mostrar a l'ordre
            del dia de les actes
        """
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            # value = obj.getObject()
            value = obj._unrestrictedGetObject()
            if value.proposalPoint:
                number = str(value.proposalPoint) + '. '
            else:
                number = ''
            if value.portal_type == 'genweb.organs.acord':
                if value.agreement:
                    agreement = ' [Acord ' + str(value.agreement) + ' - ' + str(value.estatsLlista).upper() + ' ]'
                else:
                    agreement = _(u' [Acord sense numeracio]')
            else:
                agreement = ''
            # adding hidden field to maintain good urls
            results.append(str('&emsp;') + str('<a href=----@@----') + str(obj.getURL()) + str('>') + str(number) + str(obj.Title) + str(agreement) + str('</a>'))
            if len(value.objectIds()) > 0:
                valuesInside = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': obj.getPath(),
                          'depth': 1})
                for item in valuesInside:
                    subpunt = item.getObject()
                    if subpunt.proposalPoint:
                        numberSubpunt = str(subpunt.proposalPoint) + '. '
                    else:
                        numberSubpunt = ''
                    if subpunt.portal_type == 'genweb.organs.acord':
                        if subpunt.agreement:
                            agreement = ' [Acord ' + str(subpunt.agreement) + ' - ' + str(subpunt.estatsLlista).upper() + ' ]'
                    else:
                        agreement = _(u' [Acord sense numeracio]')
                    # adding hidden field to maintain good urls
                    results.append(str('&emsp;&emsp;') + str('<a href=----@@----') + str(item.getURL()) + str('>') + str(numberSubpunt) + str(item.Title) + str(agreement) + str('</a>'))

        return '<br/>'.join(results)
