# -*- coding: utf-8 -*-
from five import grok
from plone.dexterity.interfaces import IDexterityContent
from plone import api
from genweb.organs.interfaces import IGenwebOrgansLayer
import json
from Products.Five import BrowserView
import transaction
from Acquisition import aq_inner
from zope.component import getMultiAdapter
import pdfkit
import random
import os

pdf_options = {
    'page-size': 'A4',
    'margin-top': '0.5in',
    'margin-right': '0.75in',
    'margin-bottom': '0.5in',
    'margin-left': '0.75in',
    'footer-right': '[page] of [topage]',
    'quiet': '',
}


class changeInitialProposalPoint(grok.View):
    # After migration, there was an error...
    # Point 0 must be Informat, instead of Aprovat
    grok.context(IDexterityContent)
    grok.name('change_proposal_after_migration')
    grok.require('cmf.ModifyPortalContent')
    grok.layer(IGenwebOrgansLayer)

    def render(self):
        items = api.content.find(path='/', portal_type='genweb.organs.punt')
        results = []
        for item in items:
            value = item.getObject()
            if value.proposalPoint is '0':
                value.estatsLlista = 'Informat'
                results.append(dict(title=item.Title,
                                    path=item.getURL(),
                                    proposalPoint=value.proposalPoint,
                                    estat=value.estatsLlista))
        return json.dumps(results)


class searchOrgans(grok.View):
    # Put all in obert state
    grok.context(IDexterityContent)
    grok.name('show_all_organs')
    grok.require('cmf.ModifyPortalContent')
    grok.layer(IGenwebOrgansLayer)

    def render(self):
        items = api.content.find(path='/', portal_type='genweb.organs.organgovern')
        for item in items:
            value = item.getObject()
            value.organType = 'open_organ'
            transaction.commit()

        return True


class changeMimeType(grok.View):
    # After migration, there was an error...
    # Incorrect mimetypes in some pdf files
    # application/force-download -->
    # application/x-download -->
    # application/x-octet-stream -->

    grok.context(IDexterityContent)
    grok.name('change_file_mimetype_to_pdf')
    grok.require('cmf.ModifyPortalContent')
    grok.layer(IGenwebOrgansLayer)

    def render(self):
        files = api.content.find(path='/', portal_type='genweb.organs.file')
        results = []
        oldvisible = newvisible = oldhidden = newhidden = ''
        types = ['application/force-download', 'application/x-download', 'application/x-octet-stream']
        for file in files:
            changed = False
            item = file.getObject()
            if item.visiblefile and item.hiddenfile:
                oldvisible = item.visiblefile.contentType
                oldhidden = item.hiddenfile.contentType
                if item.visiblefile.contentType in types:
                    item.visiblefile.contentType = 'application/pdf'
                    newvisible = item.visiblefile.contentType
                    changed = True
                    transaction.commit()

                if item.hiddenfile.contentType in types:
                    item.hiddenfile.contentType = 'application/pdf'
                    newhidden = item.hiddenfile.contentType
                    changed = True
                    transaction.commit()

                results.append(dict(path=file.getURL(),
                                    oldvisible=oldvisible,
                                    oldhidden=oldhidden,
                                    newvisible=newvisible,
                                    newhidden=newhidden,
                                    changed=changed))
            elif item.hiddenfile:
                oldvisible = newvisible = ''
                oldhidden = item.hiddenfile.contentType
                if item.hiddenfile.contentType in types:
                    item.hiddenfile.contentType = 'application/pdf'
                    newhidden = item.hiddenfile.contentType
                    changed = True
                    transaction.commit()

                results.append(dict(path=file.getURL(),
                                    oldvisible=oldvisible,
                                    oldhidden=oldhidden,
                                    newvisible=newvisible,
                                    newhidden=newhidden,
                                    changed=changed))

            elif item.visiblefile:
                oldvisible = item.visiblefile.contentType
                oldhidden = newhidden = ''
                if item.visiblefile.contentType in types:
                    item.visiblefile.contentType = 'application/pdf'
                    newvisible = item.visiblefile.contentType
                    changed = True
                    transaction.commit()

                results.append(dict(path=file.getURL(),
                                    oldvisible=oldvisible,
                                    oldhidden=oldhidden,
                                    newvisible=newvisible,
                                    newhidden=newhidden,
                                    changed=changed))

        return json.dumps(results)


class PrintPDF(BrowserView):
    """
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """
        """
        pdf = self.genera_pdf()
        fitxer_pdf = pdf['fitxer_pdf']
        filename = self.context.Title() + '.pdf'
        # indiquem a l'entorn que li enviem un pdf i retornem el fitxer
        self.request.response.setHeader('Content-Type', 'application/pdf')
        self.request.response.setHeader('Content-Disposition', ' attachment; filename="%s"' % filename)

        return fitxer_pdf

    def genera_pdf(self):
        """ Generate PDF from printActa view """
        context = self.context
        vista = getMultiAdapter((aq_inner(context), self.request), name='printActa')
        vista = vista.__of__(context)
        text = vista()
        num_random = "%05d" % random.randint(0, 10000)
        nom_pdf_temporal = '/tmp/organs-pdf-acta-random-' + num_random + '.pdf'
        pdfkit.from_string(text, nom_pdf_temporal, options=pdf_options)
        pdf = open(nom_pdf_temporal)
        fitxer_pdf = pdf.read()
        pdf.close()
        os.remove(nom_pdf_temporal)

        return {'fitxer_pdf': fitxer_pdf, 'nom_pdf_temporal': nom_pdf_temporal}
