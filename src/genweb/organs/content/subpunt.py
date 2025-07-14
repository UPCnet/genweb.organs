# -*- coding: utf-8 -*-
"""Subpunt content type (migrated to Plone 6 / Python 3).
Se basa en la implementación de ``punt.py`` pero con ligeras variaciones:
* El número de punto se calcula concatenando el del punt padre con un índice.
* No puede contener otros subpunts, así que ``SubPuntsInside`` devuelve una lista vacía.
"""

from AccessControl import Unauthorized
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.dexterity import textindexer
from plone import api
from plone.autoform import directives
from z3c.form import form
from plone.indexer import indexer
from plone.supermodel.directives import fieldset
from plone.supermodel import model
from zope import schema
from zope.interface import directlyProvides, implementer, provider
from zope.schema.interfaces import IContextAwareDefaultFactory, IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.textfield import RichText as RichTextField

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental.utils import UtilsFirmaDocumental

import unicodedata
from lxml import html


# -----------------------------------------------------------------------------
# Helper utilities
# -----------------------------------------------------------------------------

def llistaEstats(context):
    """Devuelve un vocabulario con los estados configurados en el órgano padre.
    A diferencia del punt, el subpunt tiene el órgano a **dos niveles** por
    encima (punt → sessio → organ). Sin embargo, utilizamos ``utils.get_organ``
    que ya sube por la cadena hasta encontrarlo, por lo que no necesitamos
    lógica adicional aquí.
    """
    organ = utils.get_organ(context)
    if not organ or not getattr(organ, 'estatsLlista', None) or not organ.estatsLlista.raw:
        return SimpleVocabulary([])

    raw_html = organ.estatsLlista.raw
    terms = []
    try:
        root = html.fromstring(f"<div>{raw_html}</div>")
        lines = [p.text_content().strip() for p in root.xpath('//p')]
        if not lines and raw_html.strip():
            lines = [line.strip() for line in raw_html.splitlines() if line.strip()]
    except (html.etree.ParserError, html.etree.XMLSyntaxError):
        lines = [line.strip() for line in raw_html.splitlines() if line.strip()]

    for line in lines:
        parts = line.split()
        if not parts:
            continue
        label = ' '.join(parts[:-1]) if len(parts) > 1 and parts[-1].isalnum() else line
        token = unicodedata.normalize('NFKD', label).encode('ascii', 'ignore').decode('ascii')
        terms.append(SimpleVocabulary.createTerm(label, token, label))

    return SimpleVocabulary(terms)

directlyProvides(llistaEstats, IContextSourceBinder)


# -----------------------------------------------------------------------------
# Default factories
# -----------------------------------------------------------------------------

@provider(IContextAwareDefaultFactory)
def proposal_point_default(context):
    """Genera automáticamente el número de subpunt.

    Se calcula como «<número punt>.<posición dentro del punt>».
    """
    # En los formularios de alta, *context* apunta al contenedor donde se
    # añade el subpunt (normalmente un objeto Punt). En edición, *context*
    # será el propio Subpunt. Cubrimos ambos casos.
    if hasattr(context, 'portal_type') and context.portal_type == 'genweb.organs.subpunt':
        # Ya somos un subpunt (modo edición): el número ya existe.
        return getattr(context, 'proposalPoint', '1.1') or '1.1'

    # Caso habitual: estamos en el Punt que actuará como contenedor
    punt = context

    # Número del punt (puede ser vacío si el punt aún no lo tiene)
    punt_number = getattr(punt, 'proposalPoint', None) or '1'

    # Contamos los subpunts y acords existentes para asignar el siguiente índice
    catalog = api.portal.get_tool(name='portal_catalog')
    folder_path = '/'.join(punt.getPhysicalPath())
    brains = catalog.searchResults(portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
                                   path={'query': folder_path, 'depth': 1})

    return f"{punt_number}.{len(brains) + 1}"


# -----------------------------------------------------------------------------
# Dexterity schema
# -----------------------------------------------------------------------------

@provider(IFormFieldProvider)
class ISubpunt(model.Schema):
    """Esquema Dexterity para Subpunt."""

    fieldset('subpunt', 
             label=_(u'Tab subpunt'), 
             fields=['title', 'proposalPoint', 'defaultContent', 'estatsLlista'])

    textindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Subpunt Title'), 
        required=True
    )

    directives.mode(proposalPoint='hidden')
    proposalPoint = schema.TextLine(
        title=_(u'Proposal point number'), 
        required=False, 
        defaultFactory=proposal_point_default
    )

    textindexer.searchable('defaultContent')
    defaultContent = RichTextField(
        title=_(u"Proposal description"), 
        required=False
    )

    estatsLlista = schema.Choice(
        title=_(u"Agreement and document label"), 
        source=llistaEstats, 
        required=True
    )


@indexer(ISubpunt)
def proposalPoint_index(obj):
    return obj.proposalPoint


# -----------------------------------------------------------------------------
# Edit form (no cambios)
# -----------------------------------------------------------------------------

class Edit(form.EditForm):
    pass


# -----------------------------------------------------------------------------
# Browser view
# -----------------------------------------------------------------------------

class View(BrowserView, UtilsFirmaDocumental):
    """Vista principal del Subpunt reutilizando la plantilla punt+subpunt."""

    index = ViewPageTemplateFile('templates/punt+subpunt_view.pt')

    def __call__(self):
        return self.index()

    # Métodos expuestos en la plantilla --------------------------------------

    def title(self):
        return self.context.title

    def message(self):
        if self.context.defaultContent:
            return self.context.defaultContent.output
        return None

    def FilesandDocumentsInside(self):
        return utils.FilesandDocumentsInside(self)

    def SubPuntsInside(self):
        """Un subpunt no contiene más subpunts, así que devolvemos lista vacía."""
        return []

    def getColor(self):
        """Devuelve el color asociado al estado seleccionado."""
        estat = self.context.estatsLlista
        organ = utils.get_organ(self.context)
        if not organ or not getattr(organ, 'estatsLlista', None) or not organ.estatsLlista.raw:
            return '#777777'

        raw_html = organ.estatsLlista.raw
        try:
            root = html.fromstring(f"<div>{raw_html}</div>")
            lines = [p.text_content().strip() for p in root.xpath('//p')]
            if not lines and raw_html.strip():
                lines = [line.strip() for line in raw_html.splitlines() if line.strip()]
        except (html.etree.ParserError, html.etree.XMLSyntaxError):
            lines = [line.strip() for line in raw_html.splitlines() if line.strip()]

        for line in lines:
            parts = line.split()
            if len(parts) > 1:
                line_state = ' '.join(parts[:-1])
                line_color = parts[-1]
                if estat == line_state:
                    return line_color
        return '#777777'

    # ---------------------------------------------------------------------
    # Permisos de visualización (idénticos a punt)
    # ---------------------------------------------------------------------

    def canView(self):
        roles = utils.getUserRoles(self, self.context, api.user.get_current().id)
        if 'Manager' in roles:
            return True

        estatSessio = utils.session_wf_state(self)
        organ_tipus = self.context.organType

        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada':
                return True
            elif estatSessio == 'realitzada':
                return True
            elif estatSessio == 'tancada':
                return True
            elif estatSessio == 'en_correccio':
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_members_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized

        if organ_tipus == 'restricted_to_affected_organ':
            if estatSessio == 'planificada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor'], roles):
                return True
            elif estatSessio == 'convocada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'realitzada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'tancada' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            elif estatSessio == 'en_correccio' and utils.checkhasRol(['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                return True
            else:
                raise Unauthorized

        # Si no coincide con ninguno de los casos anteriores
        raise Unauthorized
