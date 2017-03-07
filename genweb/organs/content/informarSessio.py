# -*- coding: utf-8 -*-
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
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from genweb.organs.utils import addEntryLog
from Products.CMFCore.utils import getToolByName

from zope import schema

grok.templatedir("templates")


class IMessage(form.Schema):
    """ Define the fields of this form
    """

    sender = TextLine(
        title=_("Sender"),
        description=_("Sender organ help"),
        required=False,
        )

    recipients = TextLine(
        title=_("Recipients"),
        description=_("Mail address separated by blanks."),
        required=True)

    directives.widget(message=WysiwygFieldWidget)
    message = schema.Text(
        title=_(u"Message"),
        required=True,
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

        if session.start is None:
            sessiondate = ''
        else:
            sessiondate = session.start.strftime("%d/%m/%Y")
        if session.start is None:
            starthour = ''
        else:
            starthour = session.start.strftime("%H:%M")
        if session.end is None:
            endHour = ''
        else:
            endHour = session.end.strftime("%H:%M")
        sessionLink = str(session.absolute_url())
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

        if lang == 'es':
            introData = "<p>Puede consultar toda la documentación de la sesión aquí: <a href=" + \
                sessionLink + ">" + sessiontitle + "</a></p><br/>"
            moreData = '<p><strong>' + sessiontitle + \
                '</strong><br/></p>Lugar: ' + place + "<br/>Data: " + sessiondate + \
                "<br/>Hora de inicio: " + starthour + \
                "<br/>Hora de fin: " + endHour + \
                '<br/><br/><p><strong> Orden del día </strong></p>'

        if lang == 'en':
            introData = "<p>All the information about the session is visible here: <a href=" + \
                sessionLink + ">" + sessiontitle + "</a></p><br/>"
            moreData = '<p><strong>' + sessiontitle + \
                '</strong><br/></p>Place: ' + place + "<br/>Data: " + sessiondate + \
                "<br/>Start date: " + starthour + \
                "<br/>End data: " + endHour + \
                '<br/><br/><p><strong> Contents </strong></p>'
        else:
            # lang = ca or another...
            introData = "<p>Podeu consultar tota la documentació de la sessió aquí: <a href=" + \
                sessionLink + ">" + sessiontitle + "</a></p><br/>"
            moreData = '<p><strong>' + sessiontitle + \
                '</strong><br/></p>Lloc: ' + place + "<br/>Data: " + sessiondate + \
                "<br/>Hora d'inici: " + starthour + \
                "<br/>Hora de fi: " + endHour + \
                '<br/><br/><p><strong> Ordre del dia </strong></p>'

        self.widgets["message"].value = introData + moreData + self.Punts2Acta() + '<br/>' + signatura

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
        # replace hidden fields to maintain correct urls...
        body = formData['message'].replace('----@@----', '').encode('utf-8')
        sender = self.context.aq_parent.fromMail
        addEntryLog(self.context, sender, _(u'Sending mail informar sessio'), toMail)

        sessio_sendMail(self.context, toMail, body)  # Send mail

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
                number = str(value.proposalPoint) + '.- '
            else:
                number = ''
            if value.portal_type == 'genweb.organs.acord':
                if value.agreement:
                    agreement = str(value.agreement) + ' - '
                else:
                    agreement = _(u'ACORD') + ' - '
            else:
                agreement = ''
            # adding hidden field to maintain good urls
            results.append(str('&emsp;') + str(number) + str(agreement) + str('<a href=----@@----') + str(obj.getURL()) + str('>') + str(obj.Title) + str('</a>'))
            if len(value.objectIds()) > 0:
                valuesInside = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': obj.getPath(),
                          'depth': 1})
                for item in valuesInside:
                    subpunt = item.getObject()
                    if subpunt.proposalPoint:
                        numberSubpunt = str(subpunt.proposalPoint) + '.- '
                    else:
                        numberSubpunt = ''
                    if subpunt.portal_type == 'genweb.organs.acord':
                        if subpunt.agreement:
                            agreement = str(subpunt.agreement) + ' - '
                    else:
                        agreement = _(u'ACORD') + ' - '
                    # adding hidden field to maintain good urls
                    results.append(str('&emsp;&emsp;') + str(numberSubpunt) + str(agreement) + str('<a href=----@@----') + str(item.getURL()) + str('>') + str(item.Title) + str('</a>'))

        return '<br/>'.join(results)
