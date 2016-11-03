# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone import api
from time import strftime
from zope.annotation.interfaces import IAnnotations
from datetime import datetime
from genweb.organs import _


def sessio_changed(session, event):
    """ If organs.session change WF to convoque, sends email and
        shows the info in the template
    """
    # si passem estat a convocat cal enviar mail de convocatoria...
    if event.transition is None:
        # Quan crees element també executa aquesta acció, i ID no existeix
        # Fem el bypass
        pass
    else:
        if event.transition.id == 'convoquing':
            lang = getToolByName(session, 'portal_languages').getPreferredLanguage()
            now = strftime("%d/%m/%Y %H:%M:%S")
            sessiontitle = str(session.Title())

            sessiondate = str(session.dataSessio.strftime("%d/%m/%Y"))
            starthour = str(session.horaInici.strftime("%H:%M"))
            endHour = str(session.horaFi.strftime("%H:%M"))
            organ = session.aq_parent

            sessionLink = str(session.absolute_url())
            senderPerson = str(organ.fromMail)
            if session.signatura is None:
                signatura = ''
            else:
                signatura = str(session.signatura.encode('utf-8'))

            if session.llocConvocatoria is None:
                place = ''
            else:
                place = str(session.llocConvocatoria.encode('utf-8'))

            if session.bodyMail is None:
                customBody = ''
            else:
                customBody = str(session.bodyMail.encode('utf-8'))

            if session.adrecaLlista is None:
                recipientPerson = organ.adrecaLlista.replace(' ', '').encode('utf-8').split(',')
            else:
                recipientPerson = session.adrecaLlista.replace(' ', '').encode('utf-8').split(',')

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
                subjectMail = "Convocatòria " + sessiontitle + ' - ' + sessiondate + ' - ' + starthour
                introData = "<br/><p>Podeu consultar tota la documentació de la sessió aquí: <a href=" + \
                            sessionLink + ">" + sessiontitle + "</a></p><br/>" + signatura
                moreData = html_content + \
                    '<br/>' + customBody + '<strong>' + sessiontitle + \
                    '</strong><br/><br/>Lloc: ' + place + "<br/>Data: " + sessiondate + \
                    "<br/>Hora d'inici: " + starthour + \
                    "<br/>Hora de fi: " + endHour + \
                    '<br/><br/>/body>'
                bodyMail = moreData + str(introData)

            if lang == 'es':
                session.notificationDate = now
                subjectMail = "Convocatoria " + sessiontitle + ' - ' + sessiondate + ' - ' + starthour
                introData = "<br/><p>Puede consultar toda la documentación de la sesión aquí: <a href=" + \
                            sessionLink + ">" + sessiontitle + "</a></p><br/>" + signatura
                moreData = html_content + \
                    '<br/>' + customBody + '<strong>' + sessiontitle + \
                    '</strong><br/><br/>Lugar: ' + place + "<br/>Fecha: " + sessiondate + \
                    "<br/>Hora de inicio: " + starthour + \
                    "<br/>Hora de finalización: " + endHour + \
                    '<br/><br/>'
                bodyMail = moreData + str(introData)

            if lang == 'en':
                now = strftime("%Y-%m-%d %H:%M")
                session.notificationDate = now
                sessiondate = session.dataSessio.strftime("%Y-%m-%d")
                subjectMail = "Session " + sessiontitle + ' - ' + sessiondate + ' - ' + starthour
                introData = "<br/><p>You can view the complete session information here:: <a href=" + \
                            sessionLink + ">" + sessiontitle + "</a></p><br/>" + signatura
                moreData = html_content + \
                    '<br/>' + customBody + '<strong>' + sessiontitle + \
                    '</strong><br/><br/>Place: ' + place + "<br/>Date: " + sessiondate + \
                    "<br/>Start time: " + starthour + \
                    "<br/>End time: " + endHour + \
                    '<br/><br/>'
                bodyMail = moreData + str(introData)

            # Sending Mail!
            try:
                addAnnotation(session, recipientPerson)
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
                    _("Missatge no enviat. Comprovi el from i el to del missatge"), 'error')


def addAnnotation(object, recipients):
    """ Add annotation after change state and send mail
    """
    KEY = 'genweb.organs.logMail'
    annotations = IAnnotations(object)

    if annotations is not None:
        try:
            # Get data and append values
            data = annotations.get(KEY)
        except:
            # If it's empty, initialize data
            data = []

        dateMail = datetime.now()
        username = api.user.get_current().id
        values = dict(dateMail=dateMail.strftime('%d/%m/%Y %H:%M:%S'),
                      message=_("Sessio convocada"),
                      fromMail=username,
                      toMail=', '.join(map(str, recipients)))

        data.append(values)
        annotations[KEY] = data
