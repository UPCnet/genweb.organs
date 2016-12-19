# -*- coding: utf-8 -*-
from plone import api


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
