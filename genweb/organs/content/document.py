# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from plone.directives import dexterity
from plone.directives import form
from genweb.organs import _
from collective import dexteritytextindexer
from plone.autoform import directives
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone import api
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.supermodel.directives import fieldset
from AccessControl import Unauthorized

grok.templatedir("templates")


class IDocument(form.Schema):
    """ Tipus Document: Per marcar si són públics o privats """

    fieldset('document',
             label=_(u'Tab document'),
             fields=['title', 'description', 'defaultContent', 'alternateContent']
             )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    dexteritytextindexer.searchable('title')
    description = schema.Text(
        title=_PMF(u'label_description', default=u'Summary'),
        description=_PMF(
            u'help_description',
            default=u'Used in item listings and search results.'
        ),
        required=False,
        missing_value=u'',
    )

    directives.widget(defaultContent=WysiwygFieldWidget)
    dexteritytextindexer.searchable('defaultContent')
    defaultContent = schema.Text(
        title=_(u"Contingut public"),
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


@form.default_value(field=IDocument['title'])
def titleDefaultValue(data):
    # ficar el títol de document
    return data.context.Title()


class Edit(dexterity.EditForm):
    """A standard edit form. """
    grok.context(IDocument)


class View(grok.View):
    grok.context(IDocument)
    grok.template('document_view')

    def canView(self):
        if self.context.defaultContent is not None and api.user.is_anonymous():
            return True
        if not api.user.is_anonymous():
            return True
        raise Unauthorized

    def viewDocumentPublic(self):
        if self.context.defaultContent and self.context.alternateContent:
            if self.isSecretari() or self.isEditor() or self.isAfectat() or self.isManager() or api.user.is_anonymous():
                return True
        elif self.context.alternateContent:
            if self.isSecretari() or self.isEditor() or self.isManager():
                return True
            else:
                return False
        elif self.context.defaultContent:
            return True
        else:
            return False

    def viewDocumentReserved(self):
        if self.context.defaultContent and self.context.alternateContent:
            if self.isSecretari() or self.isEditor() or self.isMembre() or self.isManager():
                return True
        elif self.context.alternateContent:
            if self.isSecretari() or self.isEditor() or self.isMembre() or self.isManager():
                return True
            else:
                return False
        elif self.context.defaultContent:
            if self.isSecretari() or self.isEditor() or self.isManager():
                return True
            else:
                return False
        else:
            return False

    def isAfectat(self):
        """ No podem fer servir les funcions de l'utils perque sino al ser MANAGER el template surt 2 vegades """
        if api.user.is_anonymous():
            raise Unauthorized
        else:
            username = api.user.get_current().id
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'OG4-Afectat' in roles:
                return True
            else:
                return False
        return False

    def isMembre(self):
        """ No podem fer servir les funcions de l'utils perque sino al ser MANAGER el template surt 2 vegades """
        if api.user.is_anonymous():
            raise Unauthorized
        else:
            username = api.user.get_current().id
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'OG3-Membre' in roles:
                return True
            else:
                return False
        return False

    def isEditor(self):
        """ No podem fer servir les funcions de l'utils perque sino al ser MANAGER el template surt 2 vegades """
        if api.user.is_anonymous():
            raise Unauthorized
        else:
            username = api.user.get_current().id
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'OG2-Editor' in roles:
                return True
            else:
                return False
        return False

    def isSecretari(self):
        """ No podem fer servir les funcions de l'utils perque sino al ser MANAGER el template surt 2 vegades """
        if api.user.is_anonymous():
            raise Unauthorized
        else:
            username = api.user.get_current().id
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'OG1-Secretari' in roles:
                return True
            else:
                return False
        return False

    def isManager(self):
        """ No podem fer servir les funcions de l'utils perque sino al ser MANAGER el template surt 2 vegades """
        if api.user.is_anonymous():
            raise Unauthorized
        else:
            username = api.user.get_current().id
            roles = api.user.get_roles(username=username, obj=self.context)
            if 'Manager' in roles:
                return True
            else:
                return False
        return False
