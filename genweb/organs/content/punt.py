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
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import logging


class InvalidEmailError(schema.ValidationError):
    __doc__ = u'Please enter a valid e-mail address.'


def _createLoggingVocabulary():
    """ Create zope.schema vocabulary from Python logging levels.
    """
    for level, name in logging._levelNames.items():

        # logging._levelNames dictionary is bidirectional, let's
        # get numeric keys only

        if type(level) == int:
            term = SimpleTerm(value=level, token=str(level), title=name)
            yield term

# Construct SimpleVocabulary objects of log level -> name mappings
logging_vocabulary = SimpleVocabulary(list(_createLoggingVocabulary()))


class IPunt(form.Schema):
    """ Tipus Punt: Per a cada Òrgan de Govern es podran crear
        tots els punts que es considerin oportunes
    """

    dexteritytextindexer.searchable('titlePunt')
    titlePunt = schema.TextLine(
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

    directives.widget(defaultContent=WysiwygFieldWidget)
    dexteritytextindexer.searchable('defaultContent')
    defaultContent = schema.Text(
        title=_(u"Proposal description"),
        description=_(u"Default content shown in the document view"),
        required=False,
    )

    estatsLlista = schema.Choice(
        title=_(u"Agreement and document labels"),
        vocabulary=logging_vocabulary,
        required=True,
    )


class Edit(dexterity.EditForm):
    """A standard edit form.
    """
    grok.context(IPunt)


class View(grok.View):
    grok.context(IPunt)
    grok.template('punt_view')

    def FilesInside(self):
        """ Retorna les sessions d'aquí dintre (sense tenir compte estat)
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        data = portal_catalog.searchResults(
            portal_type='File',
            path={'query': folder_path,
                  'depth': 1})

        # The last modified is the first shown.
        return sorted(data, key=lambda item: item.start, reverse=True)
