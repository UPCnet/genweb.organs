# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from collective import dexteritytextindexer
from Products.CMFCore.utils import getToolByName
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import directlyProvides
import unicodedata

grok.templatedir("templates")


class InvalidEmailError(schema.ValidationError):
    __doc__ = u'Please enter a valid e-mail address.'


def llistamails(context):
    """ Create zope.schema vocabulary from Python logging levels. """

    terms = []

    values = context.aq_parent.estatsLlista
    mails = values.split(',')

    for item in mails:
        if isinstance(item, str):
            flattened = unicodedata.normalize('NFKD', item.decode('utf-8')).encode('ascii', errors='ignore')
        else:
            flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')

        terms.append(SimpleVocabulary.createTerm(item, flattened, item))

    return SimpleVocabulary(terms)
directlyProvides(llistamails, IContextSourceBinder)


class IPunt(form.Schema):
    """ Tipus Punt: Per a cada Òrgan de Govern es podran crear
        tots els punts que es considerin oportuns
    """

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Punt Title'),
        required=True
    )

    proposalPoint = schema.TextLine(
        title=_(u'Proposal point number'),
        required=False
    )

    agreement = schema.TextLine(
        title=_(u'Agreement number'),
        required=False
    )

    acordOrgan = schema.Bool(
        title=_(u'Es un acord?'),
        required=False,
        default=False,
    )

    directives.widget(defaultContent=WysiwygFieldWidget)
    dexteritytextindexer.searchable('defaultContent')
    defaultContent = schema.Text(
        title=_(u"Proposal description"),
        required=False,
    )

    estatsLlista = schema.Choice(
        title=_(u"Agreement and document labels"),
        source=llistamails,
        required=True,
    )


class Edit(dexterity.EditForm):
    """A standard edit form.
    """
    grok.context(IPunt)


class View(grok.View):
    grok.context(IPunt)
    grok.template('punt_view')

    def isAcord(self):
        if self.context.acordOrgan:
            return True
        return False

    def FilesandDocumentsInside(self):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        values = portal_catalog.searchResults(
            portal_type=['genweb.organs.file','genweb.organs.document'],
            sort_on='getObjPositionInParent',
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for obj in values:
            if obj.portal_type == 'genweb.organs.file':
                if obj.hiddenfile is True:
                    tipus = 'fa fa-file'
                else:
                    tipus = 'fa fa-file-o'
            else:
                tipus = 'fa fa-file-text-o'

            results.append(dict(title=obj.Title,
                                absolute_url=obj.getURL(),
                                classCSS=tipus,
                                hidden=obj.hiddenfile))
        return results
