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
                    field_obj = field.get_object()
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
        brains = catalog.searchResults(portal_type='File')

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

        for brain in brains:
            obj = brain.getObject()

            # Reparar obj.file si és bytes (cas erroni)
            # if isinstance(obj.file, bytes):
            #     filename = obj.getId() + '.pdf'
            #     obj.file = NamedBlobFile(
            #         data=obj.file,
            #         contentType='application/pdf',
            #         filename=filename
            #     )
            #     obj.reindexObject()

            if not obj.file or not obj.file.filename.lower().endswith('.pdf'):
                continue

            file_data = obj.file.data

            if is_signed_pdf(file_data):
                logger.info("[SKIPPED] %s - PDF signat" % obj.absolute_url())
                count_signed += 1
                continue

            count_total += 1

            try:
                filename = obj.file.filename

                files = {
                    'fitxerPerAnonimitzar': (filename, file_data, 'application/pdf')
                }

                response = requests.post(api_url, headers=headers, files=files)

                if response.status_code == 200:
                    cleaned_data = response.content

                    obj.file = NamedBlobFile(
                        data=cleaned_data,
                        contentType='application/pdf',
                        filename=filename
                    )

                    obj.reindexObject()
                    count_cleaned += 1
                    logger.info("[OK] %s" % obj.absolute_url())
                else:
                    errors.append("%s: %s" % (obj.absolute_url(), response.status_code))
                    logger.warning("[FAIL] %s - %s" % (obj.absolute_url(), response.status_code))

            except Exception as e:
                errors.append("%s: %s" % (obj.absolute_url(), str(e)))
                logger.exception("[ERROR] %s" % obj.absolute_url())

        html = """
                <h2>PDF Metadata Cleanup</h2>
                <p>Total PDFs candidates: <strong>{total_candidates}</strong></p>
                <p>Skipped (signed): <strong>{signed_count}</strong></p>
                <p>Successfully cleaned: <strong>{cleaned_count}</strong></p>
                <p>Errors: <strong>{error_count}</strong></p>
                <pre>{errors_list}</pre>
            """.format(
                total_candidates=count_total + count_signed,
                signed_count=count_signed,
                cleaned_count=count_cleaned,
                error_count=len(errors),
                errors_list='<br>'.join(errors)
            )

        transaction.commit()
        self.request.response.setHeader("Content-Type", "text/html; charset=utf-8")
        return html
