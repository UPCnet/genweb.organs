
# -*- coding: utf-8 -*-
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implementer

from genweb.organs import _
from genweb.organs.content.acord import IAcord
from genweb.organs.content.acta.acta import IActa
from genweb.organs.content.punt import IPunt
from genweb.organs.content.subpunt import ISubpunt


class IFirmaDocumental(model.Schema):

    fieldset('firma_documental',
             label=_(u'Firma Documental'),
             fields=['info_firma', 'id_firma', 'estat_firma'])

    directives.omitted('info_firma')
    info_firma = schema.Text(title=u'', required=False, default=u'{}')

    directives.omitted('id_firma')
    id_firma = schema.TextLine(title=u'', required=False, default=u'')

    directives.omitted('estat_firma')
    estat_firma = schema.TextLine(title=u'', required=False, default=u'')


alsoProvides(IFirmaDocumental, IFormFieldProvider)


@implementer(IFirmaDocumental)
class FirmaDocumental(object):
    adapts(IAcord, IActa, IPunt, ISubpunt)

    def __init__(self, context):
        self.context = context

    def _set_info_firma(self, value):
        self.context.info_firma = value

    def _get_info_firma(self):
        return getattr(self.context, 'info_firma', None)

    info_firma = property(_get_info_firma, _set_info_firma)

    def _set_id_firma(self, value):
        self.context.id_firma = value

    def _get_id_firma(self):
        return getattr(self.context, 'id_firma', None)

    id_firma = property(_get_id_firma, _set_id_firma)

    def _set_estat_firma(self, value):
        self.context.estat_firma = value

    def _get_estat_firma(self):
        return getattr(self.context, 'estat_firma', None)

    estat_firma = property(_get_estat_firma, _set_estat_firma)
