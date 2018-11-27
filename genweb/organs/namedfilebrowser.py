from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse, NotFound

from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.namedfile.utils import set_headers, stream_data

from AccessControl.ZopeGuards import guarded_getattr
from Products.Five.browser import BrowserView
from AccessControl import Unauthorized


class Download(BrowserView):
    """Download a file, via ../context/@@download/fieldname/filename
    `fieldname` is the name of an attribute on the context that contains
    the file. `filename` is the filename that the browser will be told to
    give the file. If not given, it will be looked up from the field.
    The attribute under `fieldname` should contain a named (blob) file/image
    instance from this package.
    If no `fieldname` is supplied, then a default field is looked up through
    adaption to `plone.rfc822.interfaces.IPrimaryFieldInfo`.
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(Download, self).__init__(context, request)
        self.fieldname = None
        self.filename = None

    def publishTraverse(self, request, name):

        if self.fieldname is None:  # ../@@download/fieldname
            self.fieldname = name
        elif self.filename is None:  # ../@@download/fieldname/filename
            self.filename = name
        else:
            raise NotFound(self, name, request)

        return self

    def __call__(self):
        file = getFileOrgans(self)
        if not self.filename:
            self.filename = getattr(file, 'filename', self.fieldname)
        set_headers(file, self.request.response, filename=self.filename)
        return stream_data(file)


class DisplayFile(Download):
    """Display a file, via ../context/@@display-file/fieldname/filename
    Same as Download, however in this case we don't set the filename so the
    browser can decide to display the file instead.
    """
    def __call__(self):
        file = getFileOrgans(self)
        set_headers(file, self.request.response)
        return stream_data(file)


def getFileOrgans(self):
    if not self.fieldname:
        info = IPrimaryFieldInfo(self.context, None)
        if info is None:
            # Ensure that we have at least a filedname
            raise NotFound(self, '', self.request)
        self.fieldname = info.fieldname
        file = info.value
    else:
        context = getattr(self.context, 'aq_explicit', self.context)
        file = guarded_getattr(context, self.fieldname, None)

    if file is None:
        raise NotFound(self, self.fieldname, self.request)
    # GENWEB ORGANS CODE ADDED
    # Antes de retornar el fichero comprobamos los estados de la sesion
    # para ver si lo debemos mostrar o no
    # Check if genweb.organs installed...

    from Products.CMFCore.utils import getToolByName
    qi = getToolByName(self.context, 'portal_quickinstaller')
    prods = qi.listInstalledProducts()
    installed = False

    if 'genweb.organs' in [prod['id'] for prod in prods]:
        installed = True
    if not installed:
        # Standard functionallity.
        return file
    elif self.context.portal_type == 'File':
        # If package is installed but thit is not an organ type
        # then only is an standeard file, we have to show it.
        return file
    else:
        # Organs functionallity
        from plone import api
        from genweb.organs import utils

        if utils.isManager(self):
            return file

        if self.context.aq_parent.aq_parent.portal_type == 'genweb.organs.sessio':
            # primer nivell
            estatSessio = api.content.get_state(obj=self.context.aq_parent.aq_parent)
        elif self.context.portal_type == 'genweb.organs.acta':
            estatSessio = api.content.get_state(obj=self.context.aq_parent)
        else:
            # segon nivell
            estatSessio = api.content.get_state(obj=self.context.aq_parent.aq_parent.aq_parent)
        organ_tipus = self.context.organType
        if organ_tipus == 'open_organ':
            if estatSessio == 'planificada':
                if (utils.isSecretari(self) or utils.isEditor(self)):
                    return file
                else:
                    raise Unauthorized
            if estatSessio == 'convocada':
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):
                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                else:
                    if (utils.isSecretari(self) or utils.isEditor(self)):
                        return file
                    elif utils.isMembre(self):
                        if (self.context.visiblefile and self.context.hiddenfile):
                            if self.fieldname == 'hiddenfile':
                                return file
                            else:
                                raise Unauthorized
                        else:
                            return file
                    else:
                        raise Unauthorized
            if estatSessio == 'realitzada':
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):
                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                else:
                    if (utils.isSecretari(self) or utils.isEditor(self)):
                        return file
                    elif utils.isMembre(self):
                        if (self.context.visiblefile and self.context.hiddenfile):
                            if self.fieldname == 'hiddenfile':
                                return file
                            else:
                                raise Unauthorized
                        else:
                            return file
                    elif utils.isAfectat(self):
                        if (self.context.visiblefile and self.context.hiddenfile):
                            if self.fieldname == 'visiblefile':
                                return file
                            else:
                                raise Unauthorized
                        if (self.context.hiddenfile):
                                raise Unauthorized
                        if (self.context.visiblefile):
                            return file
                    else:
                        raise Unauthorized
            if (estatSessio == 'tancada' or estatSessio == 'en_correccio'):
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):
                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                else:
                    if (utils.isSecretari(self) or utils.isEditor(self)):
                        return file
                    elif utils.isMembre(self):
                        if (self.context.visiblefile and self.context.hiddenfile):
                            if self.fieldname == 'hiddenfile':
                                return file
                            else:
                                raise Unauthorized
                        else:
                            return file
                    else:
                        if (self.context.visiblefile and self.context.hiddenfile):
                            if self.fieldname == 'visiblefile':
                                return file
                            else:
                                raise Unauthorized
                        elif (self.context.hiddenfile):
                                raise Unauthorized
                        elif (self.context.visiblefile):
                            return file
                        else:
                            raise Unauthorized

        elif organ_tipus == 'restricted_to_members_organ':
            if utils.isAnon(self):
                raise Unauthorized
            elif estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return file
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):
                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                elif self.context.visiblefile and self.context.hiddenfile:
                    if utils.isMembre(self):
                        if self.fieldname == 'visiblefile':
                            raise Unauthorized
                else:
                    return file
                return file
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):

                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                elif self.context.visiblefile and self.context.hiddenfile:
                    if utils.isMembre(self):
                        if self.fieldname == 'visiblefile':
                            raise Unauthorized
                else:
                    return file
                return file
            elif estatSessio == 'tancada':
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):
                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                elif self.context.visiblefile and self.context.hiddenfile:
                    if utils.isMembre(self):
                        if self.fieldname == 'visiblefile':
                            raise Unauthorized
                else:
                    return file
                return file
            elif estatSessio == 'en_correccio':
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):
                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                elif self.context.visiblefile and self.context.hiddenfile:
                    if utils.isMembre(self):
                        if self.fieldname == 'visiblefile':
                            raise Unauthorized
                else:
                    return file
                return file
            else:
                raise Unauthorized

        elif organ_tipus == 'restricted_to_affected_organ':
            if utils.isAnon(self):
                raise Unauthorized
            elif estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
                return file
            elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):
                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                elif self.context.visiblefile and self.context.hiddenfile:
                    if utils.isMembre(self):
                        if self.fieldname == 'visiblefile':
                            raise Unauthorized
                else:
                    return file
                return file
            elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):
                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                elif self.context.visiblefile and self.context.hiddenfile:
                    if utils.isMembre(self):
                        if self.fieldname == 'visiblefile':
                            raise Unauthorized
                    elif utils.isAfectat(self):
                        if self.fieldname == 'hiddenfile':
                            raise Unauthorized
                elif self.context.hiddenfile:
                    if utils.isAfectat(self) and (not utils.isEditor(self) or not utils.isMembre(self) or not utils.isSecretari(self)):
                        raise Unauthorized
                    else:
                        return file
                else:
                    return file
                return file
            elif estatSessio == 'tancada':
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):
                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                elif self.context.visiblefile and self.context.hiddenfile:
                    if utils.isMembre(self):
                        if self.fieldname == 'visiblefile':
                            raise Unauthorized
                    elif utils.isAfectat(self):
                        if self.fieldname == 'hiddenfile':
                            raise Unauthorized
                elif self.context.hiddenfile:
                    if utils.isAfectat(self) and not utils.isEditor(self) and not utils.isMembre(self) and not utils.isSecretari(self):
                        raise Unauthorized
                    else:
                        return file
                else:
                    return file
                return file
            elif estatSessio == 'en_correccio':
                if (self.context.portal_type == 'genweb.organs.acta') or (self.context.portal_type == 'genweb.organs.audio'):
                    if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
                        return file
                    else:
                        raise Unauthorized
                elif self.context.visiblefile and self.context.hiddenfile:
                    if utils.isMembre(self):
                        if self.fieldname == 'visiblefile':
                            raise Unauthorized
                    elif utils.isAfectat(self):
                        if self.fieldname == 'hiddenfile':
                            raise Unauthorized
                elif self.context.hiddenfile:
                    if utils.isAfectat(self):
                        raise Unauthorized
                else:
                    return file
                return file
            else:
                raise Unauthorized
        else:
            raise Unauthorized
