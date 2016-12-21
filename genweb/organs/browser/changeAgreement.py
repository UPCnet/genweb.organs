# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from datetime import datetime
from plone import api
from genweb.organs import _
from zope.container.interfaces import INameChooser


class changeAgreement(BrowserView):

    def __call__(self):
        """ Adding log info when renaming content """
        annotations = IAnnotations(self.context)
        if annotations is not None:
            # http://localhost:8080/Plone/ca/consell-de-direccio/organ1/sess/changeTitle?pk=OLD_ID&name=&value=NEW_ID
            try:
                origin_path = '/'.join(self.context.getPhysicalPath()) + '/' + self.request.form['pk']
                newvalue = self.request.form['value']
            except:
                return None

            KEY = 'genweb.organs.logMail'
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
                          message=_(u"Change Agreement"),
                          fromMail=username,
                          toMail=origin_path + ' -> ' + newvalue)

            try:
                entry = api.content.find(path=origin_path, depth=0)[0]

                newObject = api.content.find(id=entry.id, path='/'.join(origin_path.split('/')[:-1]))[0]
                newObject.getObject().agreement = newvalue
                if newvalue == '':
                    newObject.getObject().acordOrgan = False
                newObject.getObject().reindexObject()

                # ok transaction, then  -> save the process log
                data.append(values)
                annotations[KEY] = data
            except:
                pass
