# -*- coding: utf-8 -*-

from five import grok
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from Products.CMFCore.interfaces import IActionSucceededEvent
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapter
from plone.namedfile.file import NamedBlobFile
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from genweb.organs.anonimitzar.controlpanel import IAnonimitzarSettings
from genweb.organs.utils import get_settings_property
from genweb.organs.content.organgovern import IOrgangovern
from genweb.organs.content.sessio import ISessio
from genweb.organs.content.acord import IAcord
from genweb.organs.indicators.updating import (
    update_indicators,
    update_indicators_if_state)
from PyPDF2 import PdfFileReader
from io import BytesIO
import logging
logger = logging.getLogger(__name__)
import requests



# @grok.subscribe(IOrgangovern, IObjectRemovedEvent)
def update_indicators_on_organ_deletion(obj, event):
    update_indicators_if_state(
        obj, ('intranet', 'published'),
        service=get_settings_property('service_id'), indicator='organ-n')


# @grok.subscribe(IOrgangovern, IObjectCreatedEvent)
def update_indicators_on_organ_review_state_change(obj, event):
    update_indicators(
        obj, service=get_settings_property('service_id'), indicator='organ-n')


# @grok.subscribe(ISessio, IObjectRemovedEvent)
def update_indicators_on_sessio_deletion(obj, event):
    update_indicators_if_state(
        obj, ('convocada',),
        service=get_settings_property('service_id'), indicator='sessio-n')


# @grok.subscribe(ISessio, IActionSucceededEvent)
def update_indicators_on_sessio_review_state_change(obj, event):
    update_indicators(
        obj, service=get_settings_property('service_id'), indicator='sessio-n')


# @grok.subscribe(IAcord, IObjectRemovedEvent)
def update_indicators_on_acord_deletion(obj, event):
    update_indicators_if_state(
        obj, ('intranet', 'published'),
        service=get_settings_property('service_id'), indicator='acord-n')


# @grok.subscribe(IAcord, IObjectCreatedEvent)
def update_indicators_on_acord_review_state_change(obj, event):
    update_indicators(
        obj, service=get_settings_property('service_id'), indicator='acord-n')

def is_signed_pdf(data):
    try:
        reader = PdfFileReader(BytesIO(data))
        if '/AcroForm' in reader.trailer['/Root']:
            acroform = reader.trailer['/Root']['/AcroForm']
            if '/Fields' in acroform:
                for field in acroform['/Fields']:
                    field_obj = field.gteObject()
                    if field_obj.get('/FT') == '/Sig':
                        return True
        return False
    except Exception as e:
        logger.warning("Error analizando firma en PDF: %s" % e)
        return False


@grok.subscribe(IDexterityContent, IObjectAddedEvent)
def clean_pdf_on_upload(obj, event):
    """Subscriber que limpia el PDF al subirlo si no está firmado."""
    if not getattr(obj, 'file', None):
        return

    if not obj.file.filename.lower().endswith('.pdf'):
        return

    file_data = obj.file.data

    if is_signed_pdf(file_data):
        logger.info("[SKIPPED] %s - PDF signat" % obj.absolute_url())
        return

    try:
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IAnonimitzarSettings, check=False)

        api_url = settings.api_url
        api_key = settings.api_key

        headers = {
            'accept': 'application/json;charset=utf-8',
            'X-Api-Key': api_key
        }

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
            logger.info("[OK] %s - PDF anonimizado" % obj.absolute_url())
        else:
            logger.warning("[FAIL] %s - %s - %s" % (obj.absolute_url(), response.status_code, response.text))

    except Exception as e:
        logger.exception("[ERROR] %s - %s" % (obj.absolute_url(), str(e))) 