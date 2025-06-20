# -*- coding: utf-8 -*-
from AccessControl import Unauthorized

from plone.app.dexterity import textindexer
from plone import api
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.indexer import indexer
from plone.supermodel.directives import fieldset
from zope import schema
from zope.interface import directlyProvides, provider
from zope.schema.interfaces import IContextSourceBinder, IContextAwareDefaultFactory
from zope.schema.vocabulary import SimpleVocabulary
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.supermodel import model
from z3c.form import form
from plone.app.textfield import RichText as RichTextField

from genweb.organs import _
from genweb.organs import utils
from genweb.organs.firma_documental.utils import UtilsFirmaDocumental

import unicodedata
from lxml import html


def llistaEstats(context):
    """ Create vocabulary from Estats Organ. """
    organ = utils.get_organ(context)
    if not organ:
        return SimpleVocabulary([])

    # estatsLlista is a RichTextField on the Organ content type.
    estats_field = getattr(organ, 'estatsLlista', None)
    if not estats_field or not getattr(estats_field, 'raw', None):
        return SimpleVocabulary([])

    raw_html = estats_field.raw
    terms = []
    try:
        # Use lxml to safely parse the HTML from the RichText field
        root = html.fromstring(f"<div>{raw_html}</div>")
        lines = [p.text_content().strip() for p in root.xpath('//p')]
        if not lines and raw_html.strip():
            lines = [line.strip() for line in raw_html.splitlines() if line.strip()]

    except (html.etree.ParserError, html.etree.XMLSyntaxError):
        lines = [line.strip() for line in raw_html.splitlines() if line.strip()]

    for line in lines:
        if not line:
            continue
        # Convention: "State Name #ColorCode" or "State Name"
        parts = line.split()
        if len(parts) > 1 and parts[-1].isalnum():
            term_title = ' '.join(parts[:-1])
        else:
            term_title = line

        if term_title:
            token = unicodedata.normalize('NFKD', term_title).encode('ascii', 'ignore').decode('ascii')
            terms.append(SimpleVocabulary.createTerm(term_title, token, term_title))

    return SimpleVocabulary(terms)


directlyProvides(llistaEstats, IContextSourceBinder)


@provider(IContextAwareDefaultFactory)
def proposal_point_default(context):
    portal = api.portal.get()
    request = portal.REQUEST
    view = request.get('PUBLISHED', None)
    if hasattr(view, 'context'):
        context = view.context
    else:
        return "1.1"

    portal_catalog = api.portal.get_tool(name='portal_catalog')
    path_url = context.getPhysicalPath()[1:]
    folder_path = '/' + '/'.join(path_url)

    results = portal_catalog.searchResults(
        portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
        path={'query': folder_path, 'depth': 1}
    )
    subpunt_id = len(results) + 1

    punt_id = context.proposalPoint if getattr(context, 'proposalPoint', None) else 1
    return f"{punt_id}.{subpunt_id}"


@provider(IFormFieldProvider)
class ISubpunt(model.Schema):
    """ Subpunt: Molt similar el PUNT """
    fieldset('subpunt',
             label=_(u'Tab subpunt'),
             fields=['title', 'proposalPoint', 'defaultContent', 'estatsLlista']
             )

    textindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Subpunt Title'),
        required=True
    )

    directives.mode(proposalPoint='hidden')
    proposalPoint = schema.TextLine(
        title=_(u'Proposal point number'),
        required=False,
        defaultFactory=proposal_point_default,
    )

    textindexer.searchable('defaultContent')
    defaultContent = RichTextField(
        title=_(u"Proposal description"),
        required=False,
    )

    estatsLlista = schema.Choice(
        title=_(u"Agreement and document labels"),
        source=llistaEstats,
        required=True,
    )


@indexer(ISubpunt)
def proposalPoint(obj):
    return obj.proposalPoint


class Edit(form.EditForm):
    pass


class View(BrowserView, UtilsFirmaDocumental):
    index = ViewPageTemplateFile("templates/punt+subpunt_view.pt")

    def __call__(self):
        return self.index()

    def FilesandDocumentsInside(self):
        return utils.FilesandDocumentsInside(self)

    def SubPuntsInside(self):
        return None

    def getColor(self):
        estat = self.context.estatsLlista
        organ = utils.get_organ(self.context)
        if not organ or not getattr(organ, 'estatsLlista', None) or not organ.estatsLlista.raw:
            return '#777777'

        raw_html = organ.estatsLlista.raw
        color = '#777777'
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
        return color

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
