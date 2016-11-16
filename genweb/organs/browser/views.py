# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from datetime import datetime
from Products.CMFCore.utils import getToolByName
from plone import api
from time import strftime
from genweb.organs import _
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from plone.folder.interfaces import IExplicitOrdering
from zope.component import getMultiAdapter
from AccessControl import Unauthorized


def getOrdering(context):
    if IPloneSiteRoot.providedBy(context):
        return context
    else:
        ordering = context.getOrdering()
        if not IExplicitOrdering.providedBy(ordering):
            return None
        return ordering


class Move(BrowserView):

    def __call__(self):
        ordering = getOrdering(self.context)
        # authenticator = getMultiAdapter((self.context, self.request),
        #                                 name=u"authenticator")
        # if not authenticator.verify() or \
        #         self.request['REQUEST_METHOD'] != 'POST':
        #     raise Unauthorized

        #  ./wildcard.foldercontents-1.2.7-py2.7.egg/wildcard/foldercontents/
        portal_catalog = getToolByName(self, 'portal_catalog')
        action = self.request.form.get('action')
        itemid = self.request.form.get('itemid')
        if action == 'movedelta':
            # move contents through the table
            delta = int(self.request.form['delta'])
            ordering.moveObjectsByDelta([itemid], delta)
            i = 1
            items = self.context.items()
            for item in items:
                objid = item[0]  # el primer de tots, tenim [('title'), <container...]

                folder_path = self.context.absolute_url_path()
                value = portal_catalog.searchResults(
                    portal_type=['genweb.organs.punt'],
                    id=objid,
                    path={'query': folder_path,
                          'depth': 1})

                value[0].getObject().proposalPoint = i
                print str(value[0].getObject()) + ' -- ' + str(i)
                if len(value[0].getObject().items()) > 0:
                    print 'has subpunts'

                    for a, j in enumerate(self.context.items()):
                        if j[0] == itemid:
                            rootvalue = a + 1  # remove 0 value
                    subpunts = portal_catalog.searchResults(
                        portal_type=['genweb.organs.subpunt'],
                        path={'query': self.context.absolute_url_path() + '/' + itemid ,'depth': 1})

                    subvalue = 1
                    for value in subpunts:
                        value.getObject().proposalPoint = str(rootvalue) + str('.') + str(subvalue)
                        subvalue = subvalue+1
                i = i+1


def sessio_sendMail(session, recipients, body):
    """ Si enviem mail des de la sessio.
        Mateix codi que /browser/events/change.py
    """
    lang = getToolByName(session, 'portal_languages').getPreferredLanguage()
    now = strftime("%d/%m/%Y %H:%M:%S")

    sessiontitle = str(session.Title())

    sessiondate = session.dataSessio.strftime("%d/%m/%Y")
    starthour = session.horaInici.strftime("%H:%M")
    endHour = session.horaFi.strftime("%H:%M")
    sessionLink = str(session.absolute_url())
    organ = session.aq_parent

    if session.signatura is None:
        signatura = ''
    else:
        signatura = session.signatura.encode('utf-8')

    if session.llocConvocatoria is None:
        place = ''
    else:
        place = session.llocConvocatoria.encode('utf-8')

    senderPerson = str(organ.fromMail)

    # Fixed from modal values
    customBody = body + '<br/><br/>'
    recipientPerson = recipients

    CSS = '"' + session.portal_url()+'/++genwebupc++stylesheets/genwebupc.css' + '"'

    html_content = """
     <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <title>Mail content</title>
          <link rel="stylesheet" href=""" + CSS + """></link>
          <style type="text/css">
            body {padding:25px;}
          </style>
    </head>
    <body>
    """
    if lang == 'ca':
        session.notificationDate = now
        subjectMail = "Missatge de la sessió: " + sessiontitle + ' - ' + sessiondate
        introData = "<br/><p>Podeu consultar tota la documentació de la sessió aquí: <a href=" + \
                    sessionLink + ">" + sessiontitle + "</a></p><br/>" + signatura
        moreData = html_content + \
            '<br/>' + customBody + '<strong>' + sessiontitle + \
            '</strong><br/><br/>Lloc: ' + place + "<br/>Data: " + sessiondate + \
            "<br/>Hora d'inici: " + starthour + \
            "<br/>Hora de fi: " + endHour + \
            '<br/><br/><strong> Ordre del dia </strong></body>'
        bodyMail = moreData + str(introData)

    if lang == 'es':
        session.notificationDate = now
        subjectMail = "Mensaje de la sesión: " + sessiontitle + ' - ' + sessiondate
        introData = "<br/><p>Puede consultar toda la documentación de la sesión aquí: <a href=" + \
                    sessionLink + ">" + sessiontitle + "</a></p><br/>" + signatura
        moreData = html_content + \
            '<br/>' + customBody + '<strong>' + sessiontitle + \
            '</strong><br/><br/>Lugar: ' + place + "<br/>Fecha: " + sessiondate + \
            "<br/>Hora de inicio: " + starthour + \
            "<br/>Hora de finalización: " + endHour + \
            '<br/><br/><strong> Orden del día </strong>'
        bodyMail = moreData + str(introData)

    if lang == 'en':
        now = strftime("%Y-%m-%d %H:%M")
        session.notificationDate = now
        sessiondate = session.dataSessio.strftime("%Y-%m-%d")
        subjectMail = "Session message: " + sessiontitle + ' - ' + sessiondate
        introData = "<br/><p>You can view the complete session information here:: <a href=" + \
                    sessionLink + ">" + sessiontitle + "</a></p><br/>" + signatura
        moreData = html_content + \
            '<br/>' + customBody + '<strong>' + sessiontitle + \
            '</strong><br/><br/>Place: ' + place + "<br/>Date: " + sessiondate + \
            "<br/>Start time: " + starthour + \
            "<br/>End time: " + endHour + \
            '<br/><br/><strong> Contents </strong>'
        bodyMail = moreData + str(introData)

    # Sending Mail!
    try:
        session.MailHost.send(bodyMail,
                              mto=recipientPerson,
                              mfrom=senderPerson,
                              subject=subjectMail,
                              encode=None,
                              immediate=False,
                              charset='utf8',
                              msg_type='text/html')
        session.plone_utils.addPortalMessage(
            _("Missatge enviat correctament"), 'info')
    except:
        session.plone_utils.addPortalMessage(
            _("Missatge no enviat. Comprovi els destinataris del missatge"), 'error')


class ActaPrintView(BrowserView):

    __call__ = ViewPageTemplateFile('views/acta_print.pt')

    def organGovernTitle(self):
        """ Get organGovern Title used for printing the acta """
        return self.aq_parent.aq_parent.aq_parent.Title()

    def getOrganLogo(self):
        """ Get Image to use in print """
        try:
            if self.context.defaultImg:
                if self.context.aq_parent.aq_parent.customImage:
                    self.context.aq_parent.aq_parent.logoOrganFolder.filename
                    return self.context.aq_parent.aq_parent.aq_parent.absolute_url() + '/@@images/logoOrganFolder'
                else:
                    return self.context.aq_parent.aq_parent.aq_parent.absolute_url() + '/capcalera.jpg'
            else:
                self.context.actaImage.filename
                return self.context.absolute_url() + '/@@images/actaImage'
        except:
            return self.context.aq_parent.aq_parent.aq_parent.absolute_url() + '/capcalera.jpg'

    def getSessionLogo(self):
        """ Getlogo to use in print """
        try:
            self.context.aq_parent.aq_parent.logoOrgan.filename
            return self.context.aq_parent.aq_parent.absolute_url() + '/@@images/logoOrgan'
        except:
            return None


class AddLogMail(BrowserView):

    def __call__(self):
        """ Adding send mail information to context in annotation format
        """
        KEY = 'genweb.organs.logMail'
        annotations = IAnnotations(self.context)

        if annotations is not None:
            try:
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
                username = 'Anonymous user'

            body = ''  # Fiquem el body buit per si de cas...
            try:
                # If someone access directly to this view... do nothing
                toMail = self.request.form['recipients-name']
                body = self.request.form['message-text']
            except:
                return

            values = dict(dateMail=dateMail,
                          message=_("Send mail"),
                          fromMail=username,
                          toMail=toMail)

            data.append(values)
            annotations[KEY] = data

            sessio_sendMail(self.context, toMail, body)  # Enviem mail
        # session, sender, recipients, body

        self.request.response.redirect(self.context.absolute_url())


# Notificar canvi -> Enviar missatge
