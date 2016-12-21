# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from datetime import datetime
from Products.CMFCore.utils import getToolByName
from plone import api
from time import strftime
from genweb.organs import _
import transaction

import pkg_resources
from zope.interface import alsoProvides
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from plone.folder.interfaces import IExplicitOrdering

try:
    pkg_resources.get_distribution('plone4.csrffixes')
except pkg_resources.DistributionNotFound:
    CSRF = False
else:
    from plone.protect.interfaces import IDisableCSRFProtection
    CSRF = True


def getOrdering(context):
    if IPloneSiteRoot.providedBy(context):
        return context
    else:
        ordering = context.getOrdering()
        if not IExplicitOrdering.providedBy(ordering):
            return None
        return ordering


def addEntryLog(context, message, toMail):
    KEY = 'genweb.organs.logMail'
    annotations = IAnnotations(context)
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

        values = dict(dateMail=dateMail.strftime('%d/%m/%Y %H:%M:%S'),
                      message=message,
                      fromMail=username,
                      toMail=toMail)

        data.append(values)
        annotations[KEY] = data


class AssignAcord(BrowserView):

    def __call__(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        action = self.request.form.get('action')
        itemid = self.request.form.get('item')
        portal_type = self.request.form.get('portal_type')
        inputvalue = self.request.form.get('input')
        try:
            if action == 'assign':
                if '/' in itemid:
                    # Es tracta de subpunt i inclou punt/subpunt a itemid
                    folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + str('/'.join(itemid.split('/')[:-1]))
                    itemid = str(''.join(itemid.split('/')[-1:]))
                else:
                    folder_path = '/'.join(self.context.getPhysicalPath())

                addEntryLog(self.context, _(u'Modified acord number'), '')  # add log
                # agafo items ordenats!

                punt = portal_catalog.searchResults(
                    portal_type=portal_type,
                    id=itemid,
                    path={'query': folder_path,
                          'depth': 1})
                value = punt[0].getObject()
                value.acordOrgan = True
                value.agreement = inputvalue
        except:
            self.request.response.redirect(self.context.absolute_url())


class Delete(BrowserView):

    def __call__(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        action = self.request.form.get('action')
        itemid = self.request.form.get('item')
        portal_type = self.request.form.get('portal_type')
        try:
            if action == 'delete':
                if '/' in itemid:
                    # Es tracta de subpunt i inclou punt/subpunt a itemid
                    folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + str('/'.join(itemid.split('/')[:-1]))
                    itemid = str(''.join(itemid.split('/')[-1:]))
                    deleteItem = portal_catalog.searchResults(
                        portal_type=portal_type,
                        path={'query': folder_path, 'depth': 1},
                        id=itemid)[0].getObject()
                    api.content.delete(deleteItem)
                else:
                    folder_path = '/'.join(self.context.getPhysicalPath())
                    deleteItem = portal_catalog.searchResults(
                        portal_type=['genweb.organs.punt'],
                        path={'query': folder_path, 'depth': 1},
                        id=itemid)[0].getObject()
                    api.content.delete(deleteItem)

                portal_catalog = getToolByName(self, 'portal_catalog')
                folder_path = '/'.join(self.context.getPhysicalPath())
                addEntryLog(self.context, 'Reload proposalPoints manually', '')  # add log
                # agafo items ordenats!

                puntsOrdered = portal_catalog.searchResults(
                    portal_type=['genweb.organs.punt'],
                    sort_on='getObjPositionInParent',
                    path={'query': folder_path,
                          'depth': 1})
                index = 1
                for item in puntsOrdered:
                    objecte = item.getObject()
                    objecte.proposalPoint = index
                    objecte.reindexObject()

                    if len(objecte.items()) > 0:
                        search_path = '/'.join(objecte.getPhysicalPath())
                        subpunts = portal_catalog.searchResults(
                            portal_type=['genweb.organs.subpunt'],
                            sort_on='getObjPositionInParent',
                            path={'query': search_path, 'depth': 1})

                        subvalue = 1
                        for value in subpunts:
                            newobjecte = value.getObject()
                            newobjecte.proposalPoint = unicode(str(index) + str('.') + str(subvalue))
                            newobjecte.reindexObject()
                            subvalue = subvalue+1

                    index = index + 1

        except:
            self.request.response.redirect(self.context.absolute_url())


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
                objecte.reindexObject()

                if len(objecte.items()) > 0:
                    search_path = '/'.join(objecte.getPhysicalPath())
                    subpunts = portal_catalog.searchResults(
                        portal_type=['genweb.organs.subpunt'],
                        sort_on='getObjPositionInParent',
                        path={'query': search_path, 'depth': 1})

                    subvalue = 1
                    for value in subpunts:
                        newobjecte = value.getObject()
                        newobjecte.proposalPoint = unicode(str(index) + str('.') + str(subvalue))
                        newobjecte.reindexObject()
                        subvalue = subvalue+1

                index = index + 1

        # Volem moure un subpunt
        if action == 'movesubpunt':
            # move subpunts contents through the table
            # Esbrino id del pare (punt)
            search_path = '/'.join(self.context.getPhysicalPath())
            punt = portal_catalog.searchResults(
                id=str(itemid.split('/')[0]),
                portal_type='genweb.organs.punt',
                path={'query': search_path, 'depth': 1},
                )[0].getObject()
            ordering = getOrdering(punt)
            itemid = str(itemid.split('/')[1])
            folder_path = '/'.join(punt.getPhysicalPath())

            delta = int(self.request.form['delta'])
            ordering.moveObjectsByDelta(itemid, delta)
            # Els ids ja s'han mogut, cal afegir el proposalPoint pertinent.

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
                    objecteSubPunt = item.getObject()
                    objecteSubPunt.proposalPoint = unicode(str(puntnumber) + '.' + str(subvalue))
                    objecteSubPunt.reindexObject()
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

            values = dict(dateMail=dateMail.strftime('%d/%m/%Y %H:%M:%S'),
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
                                    item_path=obj.getPath(),
                                    css=self.getColor(obj),
                                    estats=self.estatsCanvi(obj),
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
                                item_path=obj.getPath(),
                                estats=self.estatsCanvi(obj),
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
        color = '#777777'
        for value in values.split('<br />'):
            if estat == value.split('#')[0].rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' '):
                return '#' + value.split('#')[1].replace('<p>', '').replace('</p>', '').rstrip(' ').lstrip(' ')
        return color

    def estatsCanvi(self, data):
        values = data.estatsLlista
        items = []
        for value in values.split('<br />'):
            estat = value.split('#')[0].lstrip(' ').rstrip(' ').replace('<p>', '').replace('</p>', '')
            items.append(estat)
        return items


class Reload(BrowserView):

    def __call__(self):
        """ This call reassign the correct proposalPoints to the contents in this folder
        """
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        addEntryLog(self.context, _(u'Reload proposalPoints manually'), '')  # add log
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
            objecte.reindexObject()

            if len(objecte.items()) > 0:
                search_path = '/'.join(objecte.getPhysicalPath())
                subpunts = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt'],
                    sort_on='getObjPositionInParent',
                    path={'query': search_path, 'depth': 1})

                subvalue = 1
                for value in subpunts:
                    newobjecte = value.getObject()
                    newobjecte.proposalPoint = unicode(str(index) + str('.') + str(subvalue))
                    newobjecte.reindexObject()
                    subvalue = subvalue+1

            index = index + 1
        self.request.response.redirect(self.context.absolute_url())


class modifyPointState(BrowserView):

    def __call__(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        estat = self.request.form.get('estat')
        itemid = self.request.form.get('id')
        try:
            object_path = str('/'.join(itemid.split('/')[:-1]))
            item = str(itemid.split('/')[-1:][0])
            currentitem = portal_catalog.searchResults(
                portal_type=['genweb.organs.punt', 'genweb.organs.subpunt'],
                id=item,
                path={'query': object_path,
                      'depth': 1})[0].getObject()
            if currentitem.portal_type == 'genweb.organs.punt':
                # es un punt i cal mirar a tots els de dintre...
                id = itemid.split('/')[-1:][0]
                items_inside = portal_catalog.searchResults(
                    portal_type='genweb.organs.subpunt',
                    path={'query': object_path + '/' + id,
                          'depth': 1})
                for subpunt in items_inside:
                    objecte = subpunt.getObject()
                    objecte.estatsLlista = estat
                currentitem.estatsLlista = estat
            else:
                # es un subpunt només es canvia aquest subpunt
                currentitem.estatsLlista = estat
            self.request.response.redirect(self.context.absolute_url())
        except:
            pass
