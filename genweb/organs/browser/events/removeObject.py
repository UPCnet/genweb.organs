# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone import api
from time import strftime
from zope.annotation.interfaces import IAnnotations
from datetime import datetime
from genweb.organs import _
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from genweb.organs.content.punt import IPunt
from genweb.organs.content.subpunt import ISubpunt
from five import grok
from zope.interface import implements
from transaction.interfaces import ISavepointDataManager
from transaction._transaction import AbortSavepoint
import transaction


class RedirectDataManager(object):

    implements(ISavepointDataManager)

    def __init__(self, request, url):
        self.request = request
        self.url = url
        # Use the default thread transaction manager.
        self.transaction_manager = transaction.manager

    def tpc_begin(self, transaction):
        print 'tcp_begin'
        pass

    def tpc_finish(self, transaction):
        print 'tcp_finish ' + self.url
        self.request.response.redirect(self.url)

    def tpc_abort(self, transaction):
        print 'tcp_abort ' + self.url
        self.request.response.redirect(self.url)

    def commit(self, transaction):
        # On success after delete_confirmation!
        # la buena
        # import ipdb;ipdb.set_trace()
        print 'DELETED....'
        pass

    def abort(self, transaction):
        print 'abort'
        pass

    def tpc_vote(self, transaction):
        print 'tcp_vote'
        pass

    def sortKey(self):
        return id(self)

    def savepoint(self):
        """
        This is just here to make it possible to enter a savepoint with this manager active.
        """
        print 'savepoint'
        return AbortSavepoint(self, transaction.get())


def redirect_to_trial(obj, event):
    request = getattr(obj, 'REQUEST', None)
    if request:
        print 'request'
        if obj.portal_type == 'genweb.organs.punt':
            trial_url = obj.__parent__.absolute_url()
        if obj.portal_type == 'genweb.organs.subpunt':
            trial_url = obj.__parent__.__parent__.absolute_url()
        print trial_url
        transaction.get().join(RedirectDataManager(request, trial_url))
    else:
        print 'not request'
