# -*- coding: utf-8 -*-
from plone import api
from zope.annotation.interfaces import IAnnotations
from datetime import datetime

def isReader(self):
    """ Returns true if user is Reader or Manager """
    try:
        if api.user.is_anonymous():
            return False
        else:
            username = api.user.get_current().getProperty('id')
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Reader' in roles or 'Manager' in roles:
                return True
            else:
                return False
    except:
        return False


def isEditor(self):
    """ Return true if user is Editor or Manager """
    try:
        username = api.user.get_current().getProperty('id')
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'Editor' in roles or 'Manager' in roles:
            return True
        else:
            return False
    except:
        return False


def isAffectat(self):
    """ Return true if user is Affectat or Manager """
    try:
        username = api.user.get_current().getProperty('id')
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'Affectat' in roles or 'Manager' in roles:
            return True
        else:
            return False
    except:
        return False


def isManager(self):
    """ Return true if user is Editor or Manager """
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
