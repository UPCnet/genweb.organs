# -*- coding: utf-8 -*-
from genweb.organs import utils
from plone import api

# Código copiado del canView de cada tipo.
# HAY QUE TOCAR LOS DOS SI SE ACTUALIZA
# Solo hay que cambiar el def canView(self) por def canViewXXX(self, item)
# y añadir denro el :  self.context = item
# Después cambiar el raise Unauthorized por return False


def canViewFile(self, item):
    # Permissions to view FILE
    self.context = item
    if utils.isManager(self):
        return True
    estatSessio = utils.session_wf_state(self)
    organ_tipus = self.context.aq_parent.organType  # 1 level up
    if organ_tipus == 'open_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada':
            return True
        elif estatSessio == 'en_correccio':
            return True
        else:
            return False

    elif organ_tipus == 'restricted_to_members_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        else:
            return False

    elif organ_tipus == 'restricted_to_affected_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        else:
            return False

    else:
        return False


def canViewAcord(self, item):
    # Permissions to view ACORDS
    self.context = item
    if utils.isManager(self):
        return True
    estatSessio = utils.session_wf_state(self)

    organ_tipus = self.context.organType  # TODO: WHY??? Funciona amb 1 i 2 level up

    if organ_tipus == 'open_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada':
            return True
        elif estatSessio == 'en_correccio':
            return True
        else:
            return False

    if organ_tipus == 'restricted_to_members_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        else:
            return False

    if organ_tipus == 'restricted_to_affected_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        else:
            return False


def canViewActa(self, item):
    # Permissions to view acta
    self.context = item
    if utils.isManager(self):
        return True
    estatSessio = utils.session_wf_state(self)

    if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
        return True
    elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
        return True
    elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
        return True
    elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
        return True
    elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
        return True
    else:
        return False


def canViewAudio(self, item):
    """ Return true if user is Editor/Secretari/Manager """
    try:
        username = api.user.get_current().id
        roles = api.user.get_roles(username=username, obj=self.context)
        if 'OG2-Editor' in roles or 'OG1-Secretari' in roles or 'Manager' in roles:
            return True
        else:
            return False
    except:
        return False


def canViewOrgangovern(self, item):
    # Permissions to view ORGANS DE GOVERN
    self.context = item
    if utils.isManager(self):
        return True
    organType = self.context.organType
    # If Obert
    if organType == 'open_organ':
        return True
    # if restricted_to_members_organ
    elif organType == 'restricted_to_members_organ':
        if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        else:
            return False
    # if restricted_to_affected_organ
    elif organType == 'restricted_to_affected_organ':
        if (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        else:
            return False
    else:
        return False


def canViewSessio(self, item):
    # Permissions to view SESSIONS
    self.context = item
    if utils.isManager(self):
        return True
    estatSessio = utils.session_wf_state(self)
    organ_tipus = self.context.aq_parent.organType  # 1 level up

    if organ_tipus == 'open_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada':
            return True
        elif estatSessio == 'en_correccio':
            return True
        else:
            return False

    if organ_tipus == 'restricted_to_members_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        else:
            return False

    if organ_tipus == 'restricted_to_affected_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        else:
            return False


def canViewPunt(self, item):
    # Permissions to view PUNTS
    self.context = item
    if utils.isManager(self):
        return True
    estatSessio = utils.session_wf_state(self)

    organ_tipus = self.context.aq_parent.organType  # 1 level up

    if organ_tipus == 'open_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada':
            return True
        elif estatSessio == 'en_correccio':
            return True
        else:
            return False

    if organ_tipus == 'restricted_to_members_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        else:
            return False

    if organ_tipus == 'restricted_to_affected_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        else:
            return False


def canViewSubpunt(self, item):
    # Permissions to view PUNTS
    self.context = item
    if utils.isManager(self):
        return True
    estatSessio = utils.session_wf_state(self)
    organ_tipus = self.context.aq_parent.aq_parent.organType  # 2 levels up

    if organ_tipus == 'open_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada':
            return True
        elif estatSessio == 'en_correccio':
            return True
        else:
            return False

    if organ_tipus == 'restricted_to_members_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        else:
            return False

    if organ_tipus == 'restricted_to_affected_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        else:
            return False


def canViewOrgansfolder(self, item):
    # Permissions per veure l'estat dels organs a la taula principal
    self.context = item
    if utils.isManager(self) or utils.isSecretari(self) or utils.isEditor(self):
        return True
    else:
        return False


def canViewDocument(self, item):
    # Permissions to view DOCUMENT
    self.context = item
    if utils.isManager(self):
        return True
    estatSessio = utils.session_wf_state(self)
    organ_tipus = self.context.aq_parent.organType  # 1 level up
    if organ_tipus == 'open_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada':
            return True
        elif estatSessio == 'en_correccio':
            return True
        else:
            return False

    if organ_tipus == 'restricted_to_members_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        else:
            return False

    if organ_tipus == 'restricted_to_affected_organ':
        if estatSessio == 'planificada' and (utils.isSecretari(self) or utils.isEditor(self)):
            return True
        elif estatSessio == 'convocada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self)):
            return True
        elif estatSessio == 'realitzada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'tancada' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        elif estatSessio == 'en_correccio' and (utils.isSecretari(self) or utils.isEditor(self) or utils.isMembre(self) or utils.isAfectat(self)):
            return True
        else:
            return False
