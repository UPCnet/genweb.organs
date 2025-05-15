# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives
from z3c.form import form
from plone.event.interfaces import IEventAccessor
from z3c.form import button
from z3c.form.interfaces import DISPLAY_MODE
from zope import schema
from zope.schema import TextLine
from plone.supermodel import model

from genweb.organs import _
from genweb.organs.utils import addEntryLog
from genweb.organs.content.sessio import ISessio
from genweb.organs.interfaces import IGenwebOrgansLayer
from genweb.organs import utils

import unicodedata


class IMessage(model.Schema):
    """ Informar de la sessio: /mail_informar
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


class Message(model.SchemaForm):
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
        organ = self.context.aq_parent
        self.widgets["sender"].mode = DISPLAY_MODE
        self.widgets["sender"].value = str(organ.fromMail)
        session = self.context
        if session.adrecaAfectatsLlista:
            self.widgets["recipients"].value = str(session.adrecaLlista) + ', ' + str(session.adrecaAfectatsLlista)
        else:
            self.widgets["recipients"].value = str(session.adrecaLlista)

        acc = IEventAccessor(self.context)
        if acc.start is None:
            sessiondate = ''
        else:
            sessiondate = acc.start.strftime("%d/%m/%Y")
        if acc.start is None:
            starthour = ''
        else:
            starthour = acc.start.strftime("%H:%M")
        if acc.end is None:
            endHour = ''
        else:
            endHour = acc.end.strftime("%H:%M")
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

        sessiontitle = unicodedata.normalize('NFKD', session.Title().decode('utf-8'))
        fromMessage = _(u"Resultat. ") + sessiontitle + ' (' + sessiondate + ')'
        self.widgets["fromTitle"].value = fromMessage

        if lang == 'es':
            text = unicodedata.normalize('NFKD', 'Resumen de la sesión'.decode('utf-8'))
            moreData = '<p><strong>' + sessiontitle + \
                '</strong><br/></p>Lugar: ' + place + "<br/>Data: " + sessiondate + \
                "<br/>Hora de inicio: " + starthour + \
                "<br/>Hora de finalización: " + endHour + \
                "<br/><br/><p><strong>" + text + "</strong></p>"

        if lang == 'en':
            moreData = '<p><strong>' + sessiontitle + \
                '</strong><br/></p>Place: ' + place + "<br/>Data: " + sessiondate + \
                "<br/>Start date: " + starthour + \
                "<br/>End data: " + endHour + \
                '<br/><br/><p><strong> Sesison summary </strong></p>'
        else:
            # lang = ca or another...
            text = unicodedata.normalize('NFKD', 'Resum de la sessió'.decode('utf-8'))
            moreData = '<p><strong>' + sessiontitle + \
                "</strong><br/></p>Lloc: " + place + "<br/>Data: " + sessiondate + \
                "<br/>Hora d'inici: " + starthour + \
                "<br/>Hora de fi: " + endHour + \
                "<br/><br/><p><strong>" + text + "</strong></p>"
        punts = unicodedata.normalize('NFKD', self.Punts2Acta().decode('utf-8'))
        signatura = unicodedata.normalize('NFKD', signatura.decode('utf-8'))

        self.widgets["message"].value = moreData + punts + '<br/>' + signatura

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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
        portal_catalog = api.portal.get_tool(name='portal_catalog')
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
                    agreement = _(u'[Acord ') + str(value.agreement) + ' - ' + str(value.estatsLlista).upper() + ' ]'
                else:
                    agreement = _(u'[Acord sense numeracio]') if not getattr(value, 'omitAgreement', False) else ''
            else:
                agreement = ''
            # adding hidden field to maintain good urls
            results.append(str('&emsp;') + str('<a href=----@@----') + str(obj.getURL()) + str('>') + str(number) + str(obj.Title) + str('</a>') + '&nbsp;' + str(agreement))

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
                            agreement = _(u'[Acord ') + str(subpunt.agreement) + ' - ' + str(subpunt.estatsLlista).upper() + ' ]'
                        else:
                            agreement = _(u'[Acord sense numeracio]') if not getattr(subpunt, 'omitAgreement', False) else ''
                    else:
                        agreement = ''
                    # adding hidden field to maintain good urls
                    results.append(str('&emsp;&emsp;') + str('<a href=----@@----') + str(item.getURL()) + str('>') + str(numberSubpunt) + str(item.Title) + str('</a>') + '&nbsp;' + str(agreement))
        return '<br/>'.join(results)
