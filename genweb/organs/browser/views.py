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

        if action == 'movepunt':
            # move contents through the table
            ordering = getOrdering(self.context)
            folder_path = '/'.join(self.context.getPhysicalPath())
            delta = int(self.request.form['delta'])
            ordering.moveObjectsByDelta(itemid, delta)
            # Els ids es troben ordenats, cal canviar el proposalPoint

            # agafo items ordenats!
            puntsOrdered = portal_catalog.searchResults(
                portal_type=['genweb.organs.punt'],
                sort_on='getObjPositionInParent',
                path={'query': folder_path,
                      'depth': 1})
            index = 1
            for item in puntsOrdered:
                objecte = item.getObject()
                objecte.proposalPoint = unicode(str(index))

                if len(objecte.items()) > 0:
                    search_path = '/'.join(objecte.getPhysicalPath())
                    subpunts = portal_catalog.searchResults(
                        portal_type=['genweb.organs.subpunt'],
                        sort_on='getObjPositionInParent',
                        path={'query': search_path, 'depth': 1})

                    subvalue = 1
                    rootnumber = objecte.proposalPoint
                    for value in subpunts:
                        objecte = value.getObject()
                        objecte.proposalPoint = unicode(str(rootnumber) + str('.') + str(subvalue))
                        subvalue = subvalue+1

                index = index + 1

        # Volem moure un subpunt
        if action == 'movesubpunt':
            # move subpunts contents through the table
            # Esbrino id del pare (punt)
            punt = portal_catalog.searchResults(
                id=str(itemid.split('/')[0]),
                portal_type='genweb.organs.punt',
                )[0].getObject()
            ordering = getOrdering(punt)
            itemid = str(itemid.split('/')[1])
            folder_path = '/'.join(punt.getPhysicalPath())

            delta = int(self.request.form['delta'])
            ordering.moveObjectsByDelta(itemid, delta)
            # Els ids ja s'han mogut, cal afegir el proposalpoint pertinent.

            subpuntsOrdered = portal_catalog.searchResults(
                portal_type=['genweb.organs.subpunt'],
                sort_on='getObjPositionInParent',
                path={'query': folder_path,
                      'depth': 1})

            subvalue = 1
            puntnumber = punt.proposalPoint
            # Change proposaoints dels subpunts ordenats
            for item in subpuntsOrdered:
                if item.portal_type == 'genweb.organs.subpunt':
                    objecte = item.getObject()
                    objecte.proposalPoint = unicode(str(puntnumber) + '.' + str(subvalue))
                    subvalue = subvalue+1


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


class SessionAjax(BrowserView):

    __call__ = ViewPageTemplateFile('session_ajax.pt')

    def PuntsInside(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            if obj.portal_type == 'genweb.organs.punt':
                item = obj.getObject()
                results.append(dict(title=obj.Title,
                                    absolute_url=item.absolute_url(),
                                    proposalPoint=item.proposalPoint,
                                    state=item.estatsLlista,
                                    id=obj.id))
        return results

    def SubpuntsInside(self, data):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + data['id']
        values = portal_catalog.searchResults(
            portal_type='genweb.organs.subpunt',
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            item = obj.getObject()
            results.append(dict(title=obj.Title,
                                absolute_url=item.absolute_url(),
                                proposalPoint=item.proposalPoint,
                                state=item.estatsLlista,
                                css=self.getColor(obj),
                                id='/'.join(item.absolute_url_path().split('/')[-2:])))
        return results

    def filesinside(self, item):
        portal_catalog = getToolByName(self, 'portal_catalog')
        session_path = '/'.join(self.context.getPhysicalPath()) + '/' + item['id']

        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file', 'genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': session_path,
                  'depth': 1})
        results = []
        for obj in values:
            if obj.portal_type == 'genweb.organs.file':
                tipus = 'fa fa-file-pdf-o'
            else:
                tipus = 'fa fa-file-text-o'

            results.append(dict(title=obj.Title,
                                absolute_url=obj.getURL(),
                                classCSS=tipus))
        return results

    def getSessionTitle(self):
        return self.context.Title()

    def getColor(self, data):
        # assign custom colors on organ states
        estat = data.getObject().estatsLlista
        values = data.estatsLlista

        try:
            for value in values.splitlines():
                if estat == value.split('#')[0].rstrip(' '):
                    return '#' + value.split('#')[1].rstrip(' ').lstrip(' ')
        except:
            return '#777777'  # Grey color
