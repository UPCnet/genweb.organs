# -*- coding: utf-8 -*-
from plone import api
from zope.annotation.interfaces import IAnnotations
from datetime import datetime
from Products.CMFCore.utils import getToolByName
from genweb.organs import _
import unicodedata


def isAnonim(self):
    """ Returns true if user is Anonim or Manager """
    try:
        username = api.user.get_current().getProperty('id')
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'OG5-Anonim' in roles:
            return True
        else:
            return False
    except:
        return False


def isAfectat(self):
    """ Return true if user is Afectat or Manager """
    try:
        username = api.user.get_current().getProperty('id')
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'OG4-Afectat' in roles:
            return True
        else:
            return False
    except:
        return False


def isMembre(self):
    """ Return true if user is Membre or Manager """
    try:
        username = api.user.get_current().getProperty('id')
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'OG3-Membre' in roles:
            return True
        else:
            return False
    except:
        return False


def isEditor(self):
    """ Returns true if user is Editor or Manager """
    try:
        username = api.user.get_current().getProperty('id')
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'OG2-Editor' in roles:
            return True
        else:
            return False
    except:
        return False


def isResponsable(self):
    """ Return true if user is Responsable or Manager """
    try:
        username = api.user.get_current().getProperty('id')
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'OG1-Responsable' in roles:
            return True
        else:
            return False
    except:
        return False


def isManager(self):
    """ Return true if user is Manager """
    try:
        username = api.user.get_current().getProperty('id')
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'Manager' in roles:
            return True
        else:
            return False
    except:
        return False


def addEntryLog(context, sender, message, recipients):
    """ Adds entry log with the values:
            context: where the actions is executed
            sender: who sends the mail
            message: the message
            recipients: the recipients of the message
    """
    KEY = 'genweb.organs.logMail'
    annotations = IAnnotations(context)

    if annotations is not None:
        try:
            # Get data and append values
            if annotations.get(KEY) is not None:
                data = annotations.get(KEY)
            else:
                data = []
        except:
            # If it's empty, initialize data
            data = []

        dateMail = datetime.now()

        if not sender:
            anon = api.user.is_anonymous()
            if anon:
                sender = 'Anonymous user'
            else:
                sender = api.user.get_current().id

        values = dict(dateMail=dateMail.strftime('%d/%m/%Y %H:%M:%S'),
                      message=message,
                      fromMail=sender,
                      toMail=recipients)

        data.append(values)
        annotations[KEY] = data


def FilesandDocumentsInside(self):
    portal_catalog = getToolByName(self, 'portal_catalog')
    folder_path = '/'.join(self.context.getPhysicalPath())
    values = portal_catalog.searchResults(
        portal_type=['genweb.organs.file', 'genweb.organs.document'],
        sort_on='getObjPositionInParent',
        path={'query': folder_path,
              'depth': 1})
    results = []

    for obj in values:
        if obj.portal_type == 'genweb.organs.file':
            if obj.hiddenfile is True:
                try:
                    username = api.user.get_current().getProperty('id')
                    roles = api.user.get_roles(username=username, obj=self.context)
                    if 'OG1-Responsable' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'Manager' in roles:
                        tipus = 'fa fa-file-pdf-o'
                        document = _(u'Fitxer intern')
                        labelClass = 'label label-danger'
                    else:
                        continue
                except:
                    continue
            else:
                tipus = 'fa fa-file-pdf-o'
                document = _(u'Fitxer públic')
                labelClass = 'label label-default'

        else:
            tipus = 'fa fa-file-text-o'
            document = _(u'Document')
            labelClass = 'label label-default'
            obj.hiddenfile = False

        results.append(dict(title=obj.Title,
                            absolute_url=obj.getURL(),
                            classCSS=tipus,
                            hidden=obj.hiddenfile,
                            labelClass=labelClass,
                            content=document))
    return results


def SubPuntsInside(self):
    portal_catalog = getToolByName(self, 'portal_catalog')
    folder_path = '/'.join(self.context.getPhysicalPath())
    values = portal_catalog.searchResults(
        portal_type=['genweb.organs.subpunt'],
        sort_on='getObjPositionInParent',
        path={'query': folder_path,
              'depth': 1})
    results = []
    for obj in values:
        item = obj.getObject()
        results.append(dict(title=obj.Title,
                            proposalPoint=item.proposalPoint,
                            agreement=item.agreement,
                            absolute_url=obj.getURL()))
    return results


def getColor(self):
    # assign custom colors on organ states
    estat = self.getObject().estatsLlista
    values = self.estatsLlista
    color = '#777777'
    for value in values.split('</p>'):
        if value != '':
            item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
            if estat.decode('utf-8') == ' '.join(item_net.split()[:-1]).lstrip().encode('utf-8'):
                return item_net.split(' ')[-1:][0].rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' ')
    return color


def estatsCanvi(self):
    values = self.estatsLlista
    items = []
    for value in values.split('</p>'):
        if value != '':
            item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
            estat = ' '.join(item_net.split()[:-1]).lstrip().encode('utf-8')
            items.append(estat)
    return items
