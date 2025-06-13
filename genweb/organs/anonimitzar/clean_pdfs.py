#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from genweb.organs.anonimitzar.controlpanel import IAnonimitzarSettings
from plone.namedfile.file import NamedBlobFile  

import requests
import logging
import transaction
from io import BytesIO
from PyPDF2 import PdfFileReader

logger = logging.getLogger(__name__)

def is_signed_pdf(data):
    try:
        reader = PdfFileReader(BytesIO(data))
        if '/AcroForm' in reader.trailer['/Root']:
            acroform = reader.trailer['/Root']['/AcroForm']
            if '/Fields' in acroform:
                for field in acroform['/Fields']:
                    field_obj = field.getObject()
                    if field_obj.get('/FT') == '/Sig':
                        return True
        return False
    except Exception as e:
        logger.warning("Error analizando firma en PDF: %s" % e)
        return False


class CleanPDFsView(BrowserView):
    """Vista que recorre tots els arxius PDF i elimina els metadades usant l'API."""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(portal_type=[
            'File',
            'genweb.organs.file',
            'genweb.organs.acta',
            'genweb.organs.annex',
            'genweb.organs.propostapunt',
            'genweb.organs.proposar_punt'
        ])

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IAnonimitzarSettings, check=False)

        api_url = settings.api_url
        api_key = settings.api_key

        headers = {
            'accept': 'application/json;charset=utf-8',
            'X-Api-Key': api_key
        }

        count_total = 0
        count_cleaned = 0
        count_signed = 0
        errors = []

        possible_pdf_fields = [
            'file', 'visiblefile', 'hiddenfile', 'signsFile', 'anexFile', 'acta'
        ]


        for brain in brains:
            obj = brain.getObject()

            if obj is None:
                logger.warning("No s'ha pogut recuperar l'objecte per %s", brain.getPath())
                continue
            # Reparar obj.file si és bytes (cas erroni)
            # if isinstance(obj.file, bytes):
            #     filename = obj.getId() + '.pdf'
            #     obj.file = NamedBlobFile(
            #         data=obj.file,
            #         contentType='application/pdf',
            #         filename=filename
            #     )
            #     obj.reindexObject()

            for fieldname in possible_pdf_fields:
                file_field = getattr(obj, fieldname, None)
                if not file_field:
                    continue

                try:
                    filename = getattr(file_field, 'filename', None)
                    if not filename or not filename.lower().endswith('.pdf'):
                        continue

                    file_data = file_field.data
                    if is_signed_pdf(file_data):
                        logger.info("[SKIPPED] {} [{}] - PDF signat".format(obj.absolute_url(), fieldname))
                        count_signed += 1
                        continue

                    count_total += 1

                    files = {
                        'fitxerPerAnonimitzar': (filename, file_data, 'application/pdf')
                    }

                    response = requests.post(api_url, headers=headers, files=files)

                    if response.status_code == 200:
                        cleaned_data = response.content

                        setattr(obj, fieldname, NamedBlobFile(
                            data=cleaned_data,
                            contentType='application/pdf',
                            filename=filename
                        ))
                        logger.info("[OK] {} [{}]".format(obj.absolute_url(), fieldname))
                        count_cleaned += 1
                    else:
                        error_msg = "{} [{}]: {}".format(obj.absolute_url(), fieldname, response.status_code)
                        errors.append(error_msg)
                        logger.exception("[ERROR] {}".format(obj.absolute_url()))

                except Exception as e:
                    error_msg = "{} [{}]: {}".format(obj.absolute_url(), fieldname, str(e))
                    errors.append(error_msg)
                    logger.exception("[ERROR] {}".format(obj.absolute_url()))

            obj.reindexObject()

        html = """
            <h2>PDF Metadata Cleanup</h2>
            <p>Total PDFs candidates: <strong>{total}</strong></p>
            <p>Skipped (signed): <strong>{signed}</strong></p>
            <p>Successfully cleaned: <strong>{cleaned}</strong></p>
            <p>Errors: <strong>{errors}</strong></p>
            <pre>{error_list}</pre>
        """.format(
            total=count_total + count_signed,
            signed=count_signed,
            cleaned=count_cleaned,
            errors=len(errors),
            error_list='<br>'.join(errors)
        )

        transaction.commit()
        self.request.response.setHeader("Content-Type", "text/html; charset=utf-8")
        return html