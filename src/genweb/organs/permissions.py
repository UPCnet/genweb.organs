# -*- coding: utf-8 -*-
from plone import api

from genweb.organs import utils

# Código copiado del canView de cada tipo.
# WARNING! HAY QUE TOCAR LOS DOS SI SE ACTUALIZA
# Sólo hay que cambiar: def canView(self) por def canViewXXX(self, item)
# y añadir:  self.context = item
# Después cambiar el return Unauthorized por return False
# SÓLO SE HAN DEJADO EL DE ACORD/PUNT/SUBPUNT PORQUE ES LO QUE MUESTRA EL SEARCH
# SI HAY QUE RETORNAR ALGO MÁS, HAY QUE AÑADIRLO TAMBIÉN


def canViewAcord(self, item):
    # Permissions to view ACORDS
    self.context = item
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
            return False

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
            return False

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
            return False


def canViewPunt(self, item):
    # Permissions to view PUNTS
    self.context = item
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
            return False

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
            return False

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
            return False


def canViewSubpunt(self, item):
    # Permissions to view SUBPUNTS
    self.context = item
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
            return False

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
            return False

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
            return False
