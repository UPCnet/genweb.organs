# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from collective import dexteritytextindexer
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from genweb.organs import utils
from plone import api

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

    def viewPublicContent(self):
        """ No podem fer servir les funcions de l'utils perque sino al ser MANAGER el template surt 2 vegades """
        try:
            username = api.user.get_current().getProperty('id')
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'OG1-Responsable' in roles or 'OG2-Editor' in roles or 'OG4-Afectat' in roles or 'OG5-Anonim' in roles:
                return True
            else:
                return False
        except:
            return False

    def viewPrivateContent(self):
        """ No podem fer servir les funcions de l'utils perque sino al ser MANAGER el template surt 2 vegades """
        try:
            username = api.user.get_current().getProperty('id')
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'OG1-Responsable' in roles or 'OG2-Editor' in roles:
                return True
            else:
                return False
        except:
            return False

    def showMembreContent(self):
        """ No podem fer servir les funcions de l'utils perque sino al ser MANAGER el template surt 2 vegades """
        try:
            username = api.user.get_current().getProperty('id')
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'OG3-Membre' in roles:
                if self.context.alternateContent and self.context.defaultContent:
                    return self.context.alternateContent
                elif self.context.alternateContent and not self.context.defaultContent:
                    return self.context.alternateContent
                elif self.context.defaultContent and not self.context.alternateContent:
                    return False
            else:
                return False
        except:
            return False

    def isManager(self):
        """ No podem fer servir les funcions de l'utils perque sino al ser MANAGER el template surt 2 vegades """
        try:
            username = api.user.get_current().getProperty('id')
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Manager' in roles:
                return True
            else:
                return False
        except:
            return False
