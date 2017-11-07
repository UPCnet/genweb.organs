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
import datetime
from PyPDF2 import PdfFileWriter, PdfFileReader
import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))


pdf_options = {
    'page-size': 'A4',
    'margin-top': '0.7in',
    'margin-right': '0.75in',
    'margin-bottom': '0.6in',
    'margin-left': '0.75in',
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
        """ Download pdf file with titlename """
        fitxer = self.genera_pdf()
        filename = self.context.Title() + '.pdf'
        # indiquem a l'entorn que li enviem un pdf i retornem el fitxer
        self.request.response.setHeader('Content-Type', 'application/pdf')
        self.request.response.setHeader('Content-Disposition', ' attachment; filename="%s"' % filename)
        return fitxer

    def genera_pdf(self):
        """ Generate PDF from printActa view.
            pdfkit generates a valid PDF but without headers & footers
            If we try the patched QT version from wkhtmltopdf the generated
            PDF has no the same view results. We tried another method, merge
            the initial PDf with another containing the header&footer.
            The results is valid but, the size is increased!
                original_PDF 49Kb
                final_PDF   350Kb
            Maybe the first version is valid enough...
        """
        context = self.context
        vista = getMultiAdapter((aq_inner(context), self.request), name='printActa')
        vista = vista.__of__(context)
        text = vista()
        lang = self.context.language
        if lang == 'en':
            data_msg = "Print date: "
            page_msg = 'Page '
            de_msg = ' of '
	elif lang == 'es':
            data_msg = "Fecha y hora de impresión: "
            page_msg = 'Página '
            de_msg = ' de '
        else:
            data_msg = "Data i hora d'impressió: "
            page_msg = 'Pàgina '
            de_msg = ' de '
        num_random = "%05d" % random.randint(0, 10000)
        nom_pdf_temporal = '/tmp/organs-pdf-acta-random-' + num_random + '.pdf'
        nom_pdf_modified = '/tmp/organs-pdf-acta-modified-' + num_random + '.pdf'
        pdfkit.from_string(text, nom_pdf_temporal, options=pdf_options)
        pdf = open(nom_pdf_temporal)
        fitxer_pdf = pdf.read()
        pdf.close()
        existing_pdf = PdfFileReader(file(nom_pdf_temporal, "rb"))
        num_pages = existing_pdf.getNumPages()
        packet = StringIO.StringIO()
        can = canvas.Canvas(packet, pagesize=A4)
        can.setFont('VeraIt', 6)
        can.saveState()
        can.drawString(10, 830, self.context.absolute_url())
        can.drawString(10, 10, data_msg + datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
        for i in range(num_pages):
            page_num = can.getPageNumber()
            can.setFont('VeraIt', 6)
            can.drawString(10, 830, self.context.absolute_url())
            can.drawString(10, 10, data_msg + datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
            can.drawString(535, 10, page_msg + str(page_num) + de_msg + str(num_pages))
            can.showPage()
        can.save()
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        output = PdfFileWriter()
        num_page = 0
        while (num_page < num_pages):
            page = existing_pdf.getPage(num_page)
            page.mergePage(new_pdf.getPage(num_page))
            output.addPage(page)
            num_page = num_page + 1
        # finally, write "output" to a real file
        outputStream = file(nom_pdf_modified, "wb")
        output.write(outputStream)
        outputStream.close()
        pdf_final = open(nom_pdf_modified)
        fitxer_pdf = pdf_final.read()
        #os.remove(nom_pdf_temporal)
        #os.remove(nom_pdf_modified)

        return fitxer_pdf
