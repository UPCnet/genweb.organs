# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from collective import dexteritytextindexer
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

grok.templatedir("templates")


class IDocument(form.Schema):
    """ Tipus File: Per marcar si són públics o privats """
    directives.widget(defaultContent=WysiwygFieldWidget)
    dexteritytextindexer.searchable('defaultContent')
    defaultContent = schema.Text(
        title=_(u"Proposal description"),
        description=_(u"Default content shown in the document view"),
        required=False,
    )

    directives.widget(alternateContent=WysiwygFieldWidget)
    dexteritytextindexer.searchable('alternateContent')
    alternateContent = schema.Text(
        title=_(u"Alternate description"),
        description=_(u"Content used to hide protected content"),
        required=False,
    )


class Edit(dexterity.EditForm):
    """A standard edit form. """
    grok.context(IDocument)


class View(grok.View):
    grok.context(IDocument)
    grok.template('document_view')
