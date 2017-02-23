# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone import api
from time import strftime
import pkg_resources
from zope.interface import alsoProvides
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from plone.folder.interfaces import IExplicitOrdering
from genweb.organs.utils import addEntryLog
from genweb.organs import _
import unicodedata


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


class createElement(BrowserView):

    def __call__(self):
        # TODO: Al anadir el estado con espacio y acento lo pone mal
        portal_catalog = getToolByName(self, 'portal_catalog')
        action = self.request.form.get('action')
        itemid = self.request.form.get('name')
        if itemid == '':
            pass
        else:
            try:
                value = ' '.join(self.context.estatsLlista.split('</p>')[0].rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '').split(' ')[:-1])
                estat = unicodedata.normalize("NFKD", value).encode('utf-8')
            except:
                estat = ''
            if action == 'createPunt':
                items = portal_catalog.searchResults(
                        portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
                        path={'query': self.context.absolute_url_path(),
                              'depth': 1})
                index = len(items)
                obj = api.content.create(
                    title=itemid,
                    type='genweb.organs.punt',
                    container=self.context)
                obj.estatsLlista = estat
                obj.proposalPoint = index + 1
                addEntryLog(self.context, None, _(u'Created punt'), _(u'Title: ') + str(obj.Title()))
            elif action == 'createAcord':
                items = portal_catalog.searchResults(
                        portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
                        path={'query': self.context.absolute_url_path(),
                              'depth': 1})
                index = len(items)
                obj = api.content.create(
                    title=itemid,
                    type='genweb.organs.acord',
                    container=self.context)
                obj.estatsLlista = estat
                obj.proposalPoint = index + 1
                addEntryLog(self.context, None, _(u'Created acord'), _(u'Title: ') + str(obj.Title()))
            else:
                pass


class Delete(BrowserView):

    def __call__(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        action = self.request.form.get('action')
        itemid = self.request.form.get('item')
        portal_type = self.request.form.get('portal_type')
        try:
            if action == 'delete':
                if '/' in itemid:
                    # Es tracta de subpunt i inclou punt/subpunt a itemid (segon nivell)
                    folder_path = '/'.join(self.context.getPhysicalPath()) + '/' + str('/'.join(itemid.split('/')[:-1]))
                    itemid = str(''.join(itemid.split('/')[-1:]))
                else:
                    # L'objecte a esborrar es a primer nivell
                    folder_path = '/'.join(self.context.getPhysicalPath())

                deleteItem = portal_catalog.searchResults(
                    portal_type=portal_type,
                    path={'query': folder_path, 'depth': 1},
                    id=itemid)[0].getObject()
                api.content.delete(deleteItem)
                portal_catalog = getToolByName(self, 'portal_catalog')
                folder_path = '/'.join(self.context.getPhysicalPath())

                addEntryLog(self.context, None, _(u'Deleted element'), portal_type.split('.')[-1] + ' -> ' + folder_path + '/' + itemid)
                # agafo items ordenats!

                puntsOrdered = portal_catalog.searchResults(
                    portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
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
                portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
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
      <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
      <title>Mail content</title>
          <link rel='stylesheet' href=""" + CSS + """></link>
          <style type='text/css'>
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
        if session.start is None:
            sessiondate = ''
        else:
            sessiondate = session.start.strftime("%Y-%m-%d")
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

    def sessionTitle(self):
        """ Get organGovern Title used for printing the acta """
        return self.aq_parent.aq_parent.Title()

    def getActaLogo(self):
        """ Getlogo to use in print """
        try:
            self.context.actaLogo.filename
            return self.context.absolute_url() + '/@@images/actaLogo'
        except:
            return None

    def signatura(self):
        return self.context.aq_parent.aq_parent.footer


class Reload(BrowserView):

    def __call__(self):
        """ This call reassign the correct proposalPoints to the contents in this folder
        """
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        acro_parent = getattr(self.context.aq_parent, 'acronim', None)

        if acro_parent:
            acronim = str(self.context.aq_parent.acronim) + '/'
        else:
            acronim = ''

        start = getattr(self.context, 'start', None)
        if start:
            any = str(self.context.start.strftime('%Y')) + '/'
        else:
            any = ''

        numero = getattr(self.context, 'numSessio', None)
        if numero:
            numsessio = str(self.context.numSessio) + '/'
        else:
            numsessio = ''

        addEntryLog(self.context, None, _(u'Reload proposalPoints manually'), '')  # add log
        # agafo items ordenats!
        puntsOrdered = portal_catalog.searchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})
        idacord = 1
        index = 1
        for item in puntsOrdered:
            objecte = item.getObject()
            objecte.proposalPoint = unicode(str(index))
            objecte.reindexObject()
            if item.portal_type == 'genweb.organs.acord':
                printid = '{0}'.format(str(idacord).zfill(2))
                objecte.agreement = acronim + any + numsessio + printid
                idacord = idacord + 1

            if len(objecte.items()) > 0:
                search_path = '/'.join(objecte.getPhysicalPath())
                subpunts = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': search_path, 'depth': 1})

                subvalue = 1
                for value in subpunts:
                    newobjecte = value.getObject()
                    newobjecte.proposalPoint = unicode(str(index) + str('.') + str(subvalue))
                    newobjecte.reindexObject()
                    subvalue = subvalue+1
                    if value.portal_type == 'genweb.organs.acord':
                        printid = '{0}'.format(str(idacord).zfill(2))
                        newobjecte.agreement = acronim + '/' + any + '/' + numsessio + '/' + printid
                        idacord = idacord + 1

            index = index + 1

        self.request.response.redirect(self.context.absolute_url())


class modifyPointState(BrowserView):

    def __call__(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        estat = self.request.form.get('estat')
        itemid = self.request.form.get('id')
        try:
            object_path = '/'.join(self.context.getPhysicalPath())
            item = str(itemid.split('/')[-1:][0])
            currentitem = portal_catalog.searchResults(
                portal_type=['genweb.organs.punt', 'genweb.organs.subpunt', 'genweb.organs.acord'],
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
            # self.request.response.redirect(self.context.absolute_url())
        except:
            pass


class changeActualState(BrowserView):

    def __call__(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        estat = self.request.form.get('estat')
        itemid = self.request.form.get('id')
        try:
            object_path = '/'.join(self.context.getPhysicalPath())
            item = str(itemid.split('/')[-1:][0])
            currentitem = portal_catalog.searchResults(
                portal_type=['genweb.organs.punt', 'genweb.organs.subpunt', 'genweb.organs.acord'],
                id=item,
                path={'query': object_path,
                      'depth': 1})[0].getObject()
            if currentitem.portal_type == 'genweb.organs.punt':
                # es un punt i cal mirar a tots els de dintre...
                id = itemid.split('/')[-1:][0]
                items_inside = portal_catalog.searchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    path={'query': object_path + '/' + id,
                          'depth': 1})
                for subpunt in items_inside:
                    objecte = subpunt.getObject()
                    objecte.estatsLlista = estat
                currentitem.estatsLlista = estat
            else:
                # es un subpunt només es canvia aquest subpunt
                currentitem.estatsLlista = estat
            # self.request.response.redirect(self.context.absolute_url() + '/presentation')
        except:
            pass


class changeSubpuntState(BrowserView):
    """ En vista presentació no cal fer reload ja que no es poden moure els
        elements i han un somple canvi ja queda tot ok.
    """

    def __call__(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        estat = self.request.form.get('estat')
        itemid = self.request.form.get('id')
        object_path = '/'.join(self.context.getPhysicalPath()) + '/' + str(itemid.split('/')[0])
        item = str(itemid.split('/')[-1:][0])
        currentitem = portal_catalog.searchResults(
            portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
            id=item,
            path={'query': object_path,
                  'depth': 1})
        if currentitem:
            currentitem[0].getObject().estatsLlista = estat


class Butlleti(BrowserView):
    __call__ = ViewPageTemplateFile('views/butlleti.pt')

    def PuntsOrdreDelDia(self):
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.punt', 'genweb.organs.acord'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            # value = obj.getObject()
            value = obj._unrestrictedGetObject()
            if value.portal_type == 'genweb.organs.acord':
                agreement = value.agreement
            else:
                agreement = False
            results.append(dict(Title=obj.Title,
                                url=value.absolute_url_path(),
                                punt=value.proposalPoint,
                                acord=agreement))
            if len(value.objectIds()) > 0:
                # valuesInside = portal_catalog.searchResults(
                valuesInside = portal_catalog.unrestrictedSearchResults(
                    portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                    sort_on='getObjPositionInParent',
                    path={'query': obj.getPath(),
                          'depth': 1})
                for item in valuesInside:
                    # subpunt = item.getObject()
                    subpunt = item._unrestrictedGetObject()
                    if subpunt.portal_type == 'genweb.organs.acord':
                        agreement = subpunt.agreement
                    else:
                        agreement = False
                    results.append(dict(Title=item.Title,
                                        url=subpunt.absolute_url_path(),
                                        punt=subpunt.proposalPoint,
                                        acord=agreement))
        return results

    def geTitle(self):
        return self.context.Title()
