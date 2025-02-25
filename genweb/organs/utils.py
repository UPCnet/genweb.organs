# -*- coding: utf-8 -*-
import ast
from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin

from datetime import datetime
from plone import api
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.uuid.utils import uuidToObject
from plone.memoize import instance
from plone.registry.interfaces import IRegistry
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

from genweb.organs import _
from genweb.organs.controlpanel import IOrgansSettings

import unicodedata


def isConvidat(self):
    """ Return true if user has role OG4-Afectat """
    if not api.user.is_anonymous():
        username = api.user.get_current().id
        roles = getUserRoles(self, self.context, username)
        if 'OG5-Convidat' in roles:
            return True
    return False


def isAfectat(self):
    """ Return true if user has role OG4-Afectat """
    if not api.user.is_anonymous():
        username = api.user.get_current().id
        roles = getUserRoles(self, self.context, username)
        if 'OG4-Afectat' in roles:
            return True
    return False


def isMembre(self):
    """ Return true if user has role OG3-Membre """
    if not api.user.is_anonymous():
        username = api.user.get_current().id
        roles = getUserRoles(self, self.context, username)
        if 'OG3-Membre' in roles:
            return True
    return False


def isEditor(self):
    """ Returns true if user has role OG2-Editor """
    if not api.user.is_anonymous():
        username = api.user.get_current().id
        roles = getUserRoles(self, self.context, username)
        if 'OG2-Editor' in roles:
            return True
    return False


def isSecretari(self):
    """ Return true if user has role OG1-Secretari """
    if not api.user.is_anonymous():
        username = api.user.get_current().id
        roles = getUserRoles(self, self.context, username)
        if 'OG1-Secretari' in roles:
            return True
    return False


def isManager(self):
    """ Return true if user has role Manager """
    if not api.user.is_anonymous():
        username = api.user.get_current().id
        roles = getUserRoles(self, self.context, username)
        if 'Manager' in roles:
            return True
    return False


@instance.memoize
def getUserRoles(self, context, username):
    try:
        return api.user.get_roles(username=username, obj=context)
    except:
        return []


def checkhasRol(check_roles, user_roles):
    for check_rol in check_roles:
        if check_rol in user_roles:
            return True
    return False


def isAnon(self):
    """ Return true if user has role OG1-Secretari """
    if api.user.is_anonymous():
        return True


def addEntryLog(context, sender, message, recipients):
    """ Adds entry log with the values:
            context: where the actions is executed
            sender: who sends the mail
            message: the message
            recipients: the recipients of the message
    """

    KEY = 'genweb.organs.logMail'
    annotations = IAnnotations(context)

    # This is used to remove all the log entries:
    # import ipdb;ipdb.set_trace()
    # annotations[KEY] = []
    # To remove some entry:
    # aaa = annotations[KEY]
    # pp(aaa)       # Search the desired entry position
    # aaa.pop(0)    # remove the entry

    if annotations is not None:
        try:
            # Get data and append values
            if annotations.get(KEY) is not None:
                data = annotations.get(KEY)
            else:
                data = []
        except:
            # If it's empty, initialize data
            data = []

        dateMail = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        if not sender:
            anon = api.user.is_anonymous()
            if anon:
                sender = _(u'Anonymous user')
            else:
                portal = api.portal.get()
                plugins = portal.acl_users.plugins.listPlugins(IPropertiesPlugin)
                # We use the most preferent plugin
                try:
                    pplugin = plugins[2][1]
                    all_user_properties = pplugin.enumerateUsers(api.user.get_current().id)
                    fullname = ''
                    for user in all_user_properties:
                        if user['id'] == api.user.get_current().id:
                            fullname = user['sn']
                            pass
                    if fullname:
                        sender = fullname + ' [' + api.user.get_current().id + ']'
                    else:
                        sender = api.user.get_current().id

                except:
                    # Not LDAP plugin configured
                    sender = api.user.get_current().fullname + ' [' + api.user.get_current().id + ']'
        try:
            index = len(annotations.get(KEY))
        except:
            index = 0

        values = dict(index=index + 1,
                      dateMail=dateMail,
                      message=message,
                      fromMail=sender,
                      toMail=recipients)

        data.append(values)
        annotations[KEY] = data


def addExcuse(context, name, email, message):
    """ Adds entry log with the values:
            context: where the actions is executed
            name: who make the excuse
            email: user email
            excuse message: description of the excuse
    """

    KEY = 'genweb.organs.excuse'
    annotations = IAnnotations(context)

    # This is used to remove all the log entries:
    # import ipdb;ipdb.set_trace()
    # annotations[KEY] = []
    # To remove some entry:
    # aaa = annotations[KEY]
    # pp(aaa)       # Search the desired entry position
    # aaa.pop(0)    # remove the entry

    if annotations is not None:
        try:
            # Get data and append values
            if annotations.get(KEY) is not None:
                data = annotations.get(KEY)
            else:
                data = []
        except:
            # If it's empty, initialize data
            data = []

        date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        try:
            index = len(annotations.get(KEY))
        except:
            index = 0

        values = dict(index=index + 1,
                      date=date,
                      name=name,
                      email=email,
                      message=message)

        data.append(values)
        annotations[KEY] = data


def addPoint(context, names, title, justification, path):
    """ Adds entry log with the values:
            context: where the actions is executed
            names: who makes the point
            title: title of the proposed point
            justification: why
    """

    KEY = 'genweb.organs.point'
    annotations = IAnnotations(context)

    # This is used to remove all the log entries:
    # import ipdb;ipdb.set_trace()
    # annotations[KEY] = []
    # To remove some entry:
    # aaa = annotations[KEY]
    # pp(aaa)       # Search the desired entry position
    # aaa.pop(0)    # remove the entry

    if annotations is not None:
        try:
            # Get data and append values
            if annotations.get(KEY) is not None:
                data = annotations.get(KEY)
            else:
                data = []
        except:
            # If it's empty, initialize data
            data = []

        date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        try:
            index = len(annotations.get(KEY))
        except:
            index = 0

        values = dict(index=index + 1,
                      date=date,
                      names=names,
                      title=title,
                      justification=justification,
                      path=path)

        data.append(values)
        annotations[KEY] = data


def FilesandDocumentsInside(self):
    # Return files and docs found inside the session object
    organ_tipus = self.context.organType
    # roles = getUserRoles(self, self.context, api.user.get_current().id)

    # if getattr(self.context, 'info_firma', None) and self.context.info_firma.get('fitxers', None):
    #     results = []
    #     acta = uuidToObject(self.context.info_firma.get('related_acta', None))
    #     if (
    #       acta and getattr(acta, 'info_firma', None)
    #       and acta.info_firma.get('enviatASignar', None)
    #       and acta.estat_firma.lower() in ['pendent', 'signada']
    #     ):
    #         for pos, file in self.context.info_firma['fitxers'].items():
    #             class_css = 'fa fa-2x fa-file-pdf-o text-success' if file['public'] else 'fa fa-2x fa-file-pdf-o text-error'
    #             roles_to_check = ['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat']
    #             if organ_tipus == 'open_organ':
    #                 roles_to_check.append('OG4-Afectat')
    #             if not file['public'] and not checkhasRol(roles_to_check, roles):
    #                 continue
    #             results.append(dict(title=file['title'],
    #                                 absolute_url=self.context.absolute_url() + '/viewFile?pos=' + str(pos),
    #                                 classCSS=class_css,
    #                                 new_tab=True,
    #                                 ))
    #         return results
    portal_catalog = api.portal.get_tool(name='portal_catalog')
    folder_path = '/'.join(self.context.getPhysicalPath())
    values = portal_catalog.unrestrictedSearchResults(
        portal_type=['genweb.organs.file', 'genweb.organs.document'],
        sort_on='getObjPositionInParent',
        path={'query': folder_path,
              'depth': 1})
    results = []
    for obj in values:
        value = obj.getObject()
        roles = getUserRoles(self, value, api.user.get_current().id)
        if checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor'], roles):
            class_css = 'fa fa-2x fa-file-pdf-o'
            if obj.portal_type == 'genweb.organs.file':
                if value.visiblefile and value.hiddenfile:
                    class_css = 'fa fa-2x fa-file-pdf-o text-success double-icon'
                elif value.visiblefile:
                    class_css = 'fa fa-2x fa-file-pdf-o text-success'
                elif value.hiddenfile:
                    class_css = 'fa fa-2x fa-file-pdf-o text-error'
            else:
                if value.defaultContent and value.alternateContent:
                    class_css = 'fa fa-2x fa-file-text-o text-success double-icon'
                elif value.defaultContent:
                    class_css = 'fa fa-2x fa-file-text-o text-success'
                elif value.alternateContent:
                    class_css = 'fa fa-2x fa-file-text-o text-error'

            # si està validat els mostrem tots
            results.append(dict(title=obj.Title,
                                absolute_url=obj.getURL(),
                                classCSS=class_css,
                                new_tab=False,
                                hidden=False))
        else:
            # Anonim / Afectat / Membre veuen obrir en finestra nova dels fitxers.
            # Es un document/fitxer, mostrem part publica si la té
            if obj.portal_type == 'genweb.organs.document':
                class_css = 'fa fa-2x fa-file-text-o'
                if value.defaultContent and value.alternateContent:
                    if checkhasRol(['OG3-Membre', 'OG5-Convidat'], roles):
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL(),
                                            new_tab=True,
                                            classCSS=class_css))
                    else:
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL(),
                                            new_tab=True,
                                            classCSS=class_css))
                elif value.defaultContent:
                    results.append(dict(title=obj.Title,
                                        portal_type=obj.portal_type,
                                        absolute_url=obj.getURL(),
                                        new_tab=True,
                                        classCSS=class_css))
                elif value.alternateContent:
                    if checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                        results.append(dict(title=obj.Title,
                                            portal_type=obj.portal_type,
                                            absolute_url=obj.getURL(),
                                            new_tab=True,
                                            classCSS=class_css))

            if obj.portal_type == 'genweb.organs.file':
                info_firma = getattr(value, 'info_firma', None) or {}
                if not isinstance(info_firma, dict):
                    info_firma = ast.literal_eval(info_firma)

                class_css = 'fa fa-2x fa-file-pdf-o'
                if value.visiblefile and value.hiddenfile:
                    if organ_tipus == 'open_organ':
                        if checkhasRol(['OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                            if info_firma.get('private', {}).get('uploaded', False):
                                absolute_url = obj.getURL() + '/viewFileGDoc?visibility=private'
                            else:
                                absolute_url = obj.getURL() + '/@@display-file/hiddenfile/' + value.hiddenfile.filename
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=absolute_url,
                                                new_tab=True,
                                                classCSS=class_css))
                        else:
                            if info_firma.get('public', {}).get('uploaded', False):
                                absolute_url = obj.getURL() + '/viewFileGDoc?visibility=public'
                            else:
                                absolute_url = obj.getURL() + '/@@display-file/visiblefile/' + value.visiblefile.filename
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=absolute_url,
                                                new_tab=True,
                                                classCSS=class_css))
                    else:
                        if info_firma.get('private', {}).get('uploaded', False):
                                absolute_url = obj.getURL() + '/viewFileGDoc?visibility=private'
                        else:
                            absolute_url = obj.getURL() + '/@@display-file/hiddenfile/' + value.hiddenfile.filename
                        if checkhasRol(['OG3-Membre', 'OG5-Convidat'], roles):
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=absolute_url,
                                                new_tab=True,
                                                classCSS=class_css))
                        else:
                            if info_firma.get('public', {}).get('uploaded', False):
                                absolute_url = obj.getURL() + '/viewFileGDoc?visibility=public'
                            else:
                                absolute_url = obj.getURL() + '/@@display-file/visiblefile/' + value.visiblefile.filename
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=absolute_url,
                                                new_tab=True,
                                                classCSS=class_css))
                elif value.visiblefile:
                    if info_firma.get('public', {}).get('uploaded', False):
                        absolute_url = obj.getURL() + '/viewFileGDoc?visibility=public'
                    else:
                        absolute_url = obj.getURL() + '/@@display-file/visiblefile/' + value.visiblefile.filename
                    results.append(dict(title=obj.Title,
                                        absolute_url=absolute_url,
                                        new_tab=True,
                                        classCSS=class_css,
                                        hidden=False))
                elif value.hiddenfile:
                    if info_firma.get('private', {}).get('uploaded', False):
                        absolute_url = obj.getURL() + '/viewFileGDoc?visibility=private'
                    else:
                        absolute_url = obj.getURL() + '/@@display-file/hiddenfile/' + value.hiddenfile.filename
                    if organ_tipus == 'open_organ':
                        if checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat', 'OG5-Convidat'], roles):
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=absolute_url,
                                                new_tab=True,
                                                classCSS=class_css))
                    else:
                        if checkhasRol(['Manager', 'OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG5-Convidat'], roles):
                            results.append(dict(title=obj.Title,
                                                portal_type=obj.portal_type,
                                                absolute_url=absolute_url,
                                                new_tab=True,
                                                classCSS=class_css))
    return results


def SubPuntsInside(self):
    # Returns punts and acords inside Punts
    portal_catalog = api.portal.get_tool(name='portal_catalog')
    folder_path = '/'.join(self.context.getPhysicalPath())
    values = portal_catalog.unrestrictedSearchResults(
        portal_type=['genweb.organs.subpunt', 'genweb.organs.acord'],
        sort_on='getObjPositionInParent',
        path={'query': folder_path,
              'depth': 1})
    results = []
    for obj in values:
        item = obj._unrestrictedGetObject()
        if obj.portal_type == 'genweb.organs.acord':
            agreement = item.agreement
        else:
            agreement = False
        results.append(dict(title=obj.Title,
                            proposalPoint=item.proposalPoint,
                            agreement=agreement,
                            absolute_url=obj.getURL()))
    return results


def getColor(self):
    # Get custom colors on passed organ states
    color = '#777777'
    try:
        obj = self._unrestrictedGetObject()
        estat = obj.estatsLlista
        organ = get_organ(obj)
        values = organ.estatsLlista
        for value in values.split('</p>'):
            if value != '':
                item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
                if estat.decode('utf-8') == ' '.join(item_net.split()[:-1]).lstrip():
                    return item_net.split(' ')[-1:][0].rstrip(' ').replace('<p>', '').replace('</p>', '').lstrip(' ')
    except:
        pass
    return color


def estatsCanvi(self):
    # Returns real names from estats
    organ = get_organ(self._unrestrictedGetObject())
    values = organ.estatsLlista
    items = []
    for value in values.split('</p>'):
        if value != '':
            item_net = unicodedata.normalize("NFKD", value).rstrip(' ').replace('<p>', '').replace('</p>', '').replace('\r\n', '')
            estat = ' '.join(item_net.split()[:-1]).lstrip().encode('utf-8')
            color = ' '.join(item_net.split()[-1:]).lstrip().encode('utf-8')
            items.append(dict(title=estat, color=color))
    return items


def session_wf_state(self):
    # Returns session state. Check it recurring all path...
    from genweb.organs.content.sessio import ISessio
    if ISessio.providedBy(self.context):
        portal_state = api.content.get_state(obj=self.context)
        return portal_state
    else:
        portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(self.context, portal_state.portal())
        physical_path = aq_inner(self.context).getPhysicalPath()
        relative = physical_path[len(root.getPhysicalPath()):]
        for i in range(len(relative)):
            now = relative[:i + 1]
            obj = aq_inner(root.unrestrictedTraverse(now))
            if ISessio.providedBy(obj):
                session_state = api.content.get_state(obj=obj)
                return session_state


def get_settings_property(property_id):
    settings = getUtility(IRegistry).forInterface(IOrgansSettings)
    return getattr(settings, property_id, None)


def get_organ(context):
    from genweb.organs.content.organgovern import IOrgangovern
    if IOrgangovern.providedBy(context):
        return context
    else:
        portal_state = context.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(context, portal_state.portal())
        physical_path = aq_inner(context).getPhysicalPath()
        relative = physical_path[len(root.getPhysicalPath()):]
        for i in range(len(relative)):
            now = relative[:i + 1]
            obj = aq_inner(root.unrestrictedTraverse(now))
            if IOrgangovern.providedBy(obj):
                return obj
    return None


def get_session(context):
    from genweb.organs.content.sessio import ISessio
    if ISessio.providedBy(context):
        return context
    else:
        portal_state = context.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(context, portal_state.portal())
        physical_path = aq_inner(context).getPhysicalPath()
        relative = physical_path[len(root.getPhysicalPath()):]
        for i in range(len(relative)):
            now = relative[:i + 1]
            obj = aq_inner(root.unrestrictedTraverse(now))
            if ISessio.providedBy(obj):
                return obj
    return None


def getLdapUserData(user, typology=None):
    acl_users = api.portal.get_tool(name='acl_users')
    if not typology:
        search_result = acl_users.searchUsers(id=user, exactMatch=True)
    else:
        search_result = acl_users.searchUsers(id=user, exactMatch=True, typology=typology)
    return search_result


def get_acord(context):
    from genweb.organs.content.acord import IAcord
    for obj in aq_chain(context):
        if IAcord.providedBy(obj):
            return obj
    return None


def checkHasOpenVote(context):
    acord = get_acord(context)
    if acord:
        if acord.estatVotacio == 'open':
            return True

        acord_folder_path = '/'.join(acord.getPhysicalPath())
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        esmenas = portal_catalog.unrestrictedSearchResults(
            portal_type=['genweb.organs.votacioacord'],
            sort_on='getObjPositionInParent',
            path={'query': acord_folder_path,
                    'depth': 1})

        for esmena in esmenas:
            if esmena.getObject().estatVotacio == 'open':
                return True

    return False


def getFilesSessio(context):
    portal_catalog = api.portal.get_tool('portal_catalog')
    session = get_session(context)
    session_path = '/'.join(session.getPhysicalPath())
    punts = portal_catalog.searchResults(
        portal_type=['genweb.organs.acord', 'genweb.organs.punt'],
        path={'query': session_path, 'depth': 1},
        sort_on='getObjPositionInParent'
    )
    files = []
    for punt in punts:
        files_punt = portal_catalog.searchResults(
            portal_type=['genweb.organs.file'],
            path={'query': punt.getPath(), 'depth': 1},
            sort_on='getObjPositionInParent'
        )

        for file in files_punt:
            files.append(file.getObject())

        if punt.getObject().portal_type == 'genweb.organs.acord':
            continue

        subpunts = portal_catalog.searchResults(
            portal_type=['genweb.organs.acord', 'genweb.organs.subpunt'],
            path={'query': punt.getPath(), 'depth': 1},
            sort_on='getObjPositionInParent'
        )

        for subpunt in subpunts:
            files_subpunt = portal_catalog.searchResults(
                portal_type=['genweb.organs.file'],
                path={'query': subpunt.getPath(), 'depth': 1},
                sort_on='getObjPositionInParent'
            )
            for file in files_subpunt:
                files.append(file.getObject())

    return files