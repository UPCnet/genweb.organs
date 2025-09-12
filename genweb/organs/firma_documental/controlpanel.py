# -*- coding: utf-8 -*-
from zope import schema
from plone.supermodel import model
from plone.app.registry.browser import controlpanel

from genweb.organs import _


class IFirmaDocumentalSettings(model.Schema):

    gdoc_url = schema.TextLine(
        title=_(u'URL gDOC'),
        required=False)

    gdoc_user = schema.TextLine(
        title=_(u'Usuari gDOC'),
        required=False)

    gdoc_hash = schema.TextLine(
        title=_(u'Hash gDOC'),
        required=False)

    gdoc_fons_id = schema.TextLine(
        title=_(u'Fons ID gDOC'),
        required=False)    

    codiexpedient_url = schema.TextLine(
        title=_(u'URL Generar codi expedient'),
        required=False)

    codiexpedient_apikey = schema.TextLine(
        title=_(u'API Key Generar codi expedient'),
        required=False)

    portafirmes_url = schema.TextLine(
        title=_(u'URL Portafirmes'),
        required=False)

    portafirmes_apikey = schema.TextLine(
        title=_(u'API Key Portafirmes'),
        required=False)

    copiesautentiques_url = schema.TextLine(
        title=_(u'URL Còpies Autèntiques'),
        required=False)

    copiesautentiques_apikey = schema.TextLine(
        title=_(u'API Key Còpies Autèntiques'),
        required=False)

    signaturacsv_url = schema.TextLine(
        title=_(u'URL del servei de Signatura CSV'),
        required=False)

    signaturacsv_apikey = schema.TextLine(
        title=_(u'API Key del servei de Signatura CSV'),
        required=False)


class FirmaDocumentalSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IFirmaDocumentalSettings
    label = _(u'Firma Documental')


class FirmaDocumentalSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FirmaDocumentalSettingsEditForm
