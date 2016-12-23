# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from genweb.organs import _
from genweb.organs.utils import addEntryLog


class changeAgreement(BrowserView):

    def __call__(self):
        """ Adding log info when renaming content """
        try:
            origin_path = '/'.join(self.context.getPhysicalPath()) + '/' + self.request.form['pk']
            newvalue = self.request.form['value']
        except:
            return None

        try:
            entry = api.content.find(path=origin_path, depth=0)[0]
            newObject = api.content.find(id=entry.id, path='/'.join(origin_path.split('/')[:-1]))[0]
            item = newObject.getObject()
            oldvalue = item.agreement
            item.agreement = newvalue
            if newvalue == '':
                item.acordOrgan = False
            item.reindexObject()

            # ok transaction, then  -> save the process log
            recipients = '[' + item.Title() + '] ' + oldvalue + ' -> ' + newvalue
            addEntryLog(self.context, None, _(u"Change Agreement"), recipients)
        except:
            pass
