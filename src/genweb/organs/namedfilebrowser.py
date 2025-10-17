# -*- coding: utf-8 -*-
"""Adaptación a Plone 6 / Python 3 del navegador de ficheros.

El módulo proporciona dos vistas:
  • @@download  → descarga el fichero respetando permisos
  • @@display-file → muestra/embebe el fichero respetando permisos

Cambios sobre la versión de Plone 4:
  * El check de si *genweb.organs* está instalado ya no usa
    *portal_quickinstaller* (retirado en Plone 6).
    Se comprueba simplemente  importando el paquete.
  * Se añaden *type hints* y se simplifica la lógica de permisos.
"""

from typing import Optional
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse, NotFound
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.namedfile.utils import set_headers, stream_data
from AccessControl.ZopeGuards import guarded_getattr
from Products.Five.browser import BrowserView
from AccessControl import Unauthorized
from plone import api

from genweb.organs import utils

__all__ = [
    "Download",
    "DisplayFile",
]


@implementer(IPublishTraverse)
class Download(BrowserView):
    """Descargar un archivo via @@download/fieldname/filename"""

    fieldname: Optional[str] = None
    filename: Optional[str] = None

    # IPublishTraverse -------------------------------------------------
    def publishTraverse(self, request, name):  # type: ignore[override]
        if self.fieldname is None:
            self.fieldname = name
        elif self.filename is None:
            self.filename = name
        else:
            raise NotFound(self, name, request)
        return self

    # -----------------------------------------------------------------
    def __call__(self):
        file = _get_file_with_perms(self)
        if not self.filename:
            self.filename = getattr(file, "filename", self.fieldname)
        set_headers(file, self.request.response, filename=self.filename)
        return stream_data(file)


class DisplayFile(Download):
    """Mostrar un archivo via @@display-file/fieldname/filename"""

    def __call__(self):
        file = _get_file_with_perms(self)
        set_headers(file, self.request.response)
        return stream_data(file)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _get_file_with_perms(view: Download):
    """Obtiene NamedFile respetando permisos de Organs."""

    # 1. Localizar el campo -------------------------------------------------
    context = view.context  # convenience

    if not view.fieldname:
        info = IPrimaryFieldInfo(context, None)
        if info is None:
            raise NotFound(view, "", view.request)
        view.fieldname = info.fieldname
        file = info.value
    else:
        real_context = getattr(context, "aq_explicit", context)
        file = guarded_getattr(real_context, view.fieldname, None)

    if file is None:
        raise NotFound(view, view.fieldname, view.request)

    # En Plone 6, NamedBlobFile puede devolver un objeto vacío en lugar de None
    # Check si el archivo tiene contenido real
    if hasattr(file, 'data') and not file.data:
        raise NotFound(view, view.fieldname, view.request)

    # 2. Si genweb.organs no define permisos especiales, devolvemos ---------
    #    (En runtime esto siempre es True, pero mantiene compatibilidad).
    try:
        import genweb.organs  # noqa: F401
    except ImportError:
        return file

    # 3. Para contenido File estándar (no tipos Organs) mostramos directo
    if context.portal_type == "File":
        return file

    # 4. Lógica de permisos específica Organs -----------------------------
    roles = utils.getUserRoles(view, context, api.user.get_current().id)
    if "Manager" in roles:
        return file

    # Determinar estado de la sessió
    sessio_state = utils.session_wf_state(view)
    organ_type = context.organType

    # Mapear reglas según organ_type / estado / fieldname / portal_type ----
    visible = view.fieldname == "visiblefile"
    hidden = view.fieldname == "hiddenfile"
    is_acta_audio_or_annex = context.portal_type in (
        "genweb.organs.acta", "genweb.organs.audio", "genweb.organs.annex")

    # Reglas para ACTAS, AUDIOS y ANNEX
    if is_acta_audio_or_annex:
        if sessio_state == "planificada":
            if utils.checkhasRol(["OG1-Secretari", "OG2-Editor"], roles):
                return file
        elif sessio_state in {"convocada", "realitzada"}:
            if organ_type == "open_organ":
                # Órganos públicos: sin afectados + anónimos
                allowed = ["OG1-Secretari", "OG2-Editor", "OG3-Membre",
                           "OG5-Convidat"]
                if utils.checkhasRol(allowed, roles):
                    return file
                # Si tiene OG4-Afectat, denegar acceso
                if "OG4-Afectat" in roles:
                    raise Unauthorized
                # Anónimos pueden ver actas/audios públicos
                return file
            else:
                # Órganos restringidos: sin afectados ni anónimos
                allowed = ["OG1-Secretari", "OG2-Editor", "OG3-Membre",
                           "OG5-Convidat"]
                if utils.checkhasRol(allowed, roles):
                    return file
        elif sessio_state == "tancada":
            if organ_type == "open_organ":
                # Órganos públicos: con afectados + anónimos
                allowed = ["OG1-Secretari", "OG2-Editor", "OG3-Membre",
                           "OG4-Afectat", "OG5-Convidat"]
                if utils.checkhasRol(allowed, roles):
                    return file
                # Anónimos pueden ver actas/audios públicos
                return file
            else:
                # Órganos restringidos: sin afectados ni anónimos
                allowed = ["OG1-Secretari", "OG2-Editor", "OG3-Membre",
                           "OG5-Convidat"]
                if utils.checkhasRol(allowed, roles):
                    return file
        elif sessio_state == "en_correccio":
            # En corrección: sin OG4-Afectat ni Anónimos
            allowed = ["OG1-Secretari", "OG2-Editor", "OG3-Membre",
                       "OG5-Convidat"]
            if utils.checkhasRol(allowed, roles):
                return file
        # Si no coincide con ningún estado permitido para actas/audios
        raise Unauthorized
    # Reglas para SESIONES (visiblefile/hiddenfile) - órganos abiertos
    elif organ_type == "open_organ":
        if sessio_state == "planificada":
            # Solo Secretari/Editor
            if utils.checkhasRol(["OG1-Secretari", "OG2-Editor"], roles):
                return file
        elif sessio_state in {
            "convocada", "realitzada", "tancada", "en_correccio"
        }:
            # Secretaris/editors/membres/convidats/afectats: ven ambos
            allowed = ["OG1-Secretari", "OG2-Editor", "OG3-Membre",
                       "OG4-Afectat", "OG5-Convidat"]
            if utils.checkhasRol(allowed, roles):
                return file
            # Anónimos: solo ven el visible
            if visible:
                return file
            # Si intentan acceder al hidden sin rol: Unauthorized
            if hidden:
                raise Unauthorized
    elif organ_type == "restricted_to_members_organ":
        if sessio_state == "planificada":
            if utils.checkhasRol(["OG1-Secretari", "OG2-Editor"], roles):
                return file
        elif sessio_state in {
            "convocada", "realitzada", "tancada", "en_correccio"
        }:
            if is_acta_audio_or_annex:
                # Actas/audios/annex: sin afectados ni anónimos
                if utils.checkhasRol(
                    ["OG1-Secretari", "OG2-Editor",
                     "OG3-Membre", "OG5-Convidat"],
                        roles):
                    return file
            else:
                # Sesiones: Secretari/Editor/Membre/Convidat ven todo
                if utils.checkhasRol(
                    ["OG1-Secretari", "OG2-Editor",
                     "OG3-Membre", "OG5-Convidat"],
                        roles):
                    return file
                # Afectat solo ve visiblefile
                if utils.checkhasRol(["OG4-Afectat"], roles):
                    if visible:
                        return file
                    # Si intenta acceder a hiddenfile: Unauthorized
                    if hidden:
                        raise Unauthorized
    elif organ_type == "restricted_to_affected_organ":
        if sessio_state == "planificada":
            # Solo Secretari y Editor
            if utils.checkhasRol(["OG1-Secretari", "OG2-Editor"], roles):
                return file
        elif sessio_state == "convocada":
            if is_acta_audio_or_annex:
                # Actas/audios/annex: solo Secretari, Editor, Membre, Convidat
                # (sin Afectat ni Anónimo)
                if utils.checkhasRol(
                    ["OG1-Secretari", "OG2-Editor",
                     "OG3-Membre", "OG5-Convidat"],
                        roles):
                    return file
            else:
                # Sesiones: Secretari, Editor ven todo
                if utils.checkhasRol(["OG1-Secretari", "OG2-Editor"], roles):
                    return file
                # Membre, Convidat: lógica especial con ambos ficheros
                elif utils.checkhasRol(["OG3-Membre", "OG5-Convidat"], roles):
                    if context.visiblefile and context.hiddenfile:
                        # Si hay ambos: solo ven hiddenfile
                        if hidden:
                            return file
                        else:
                            raise Unauthorized
                    else:
                        # Si hay solo uno: lo ven
                        return file
                # Afectat y Anónimo: sin acceso
        elif sessio_state in {"realitzada", "en_correccio"}:
            if is_acta_audio_or_annex:
                # Actas/audios/annex: sin Afectat ni Anónimo
                if utils.checkhasRol(
                    ["OG1-Secretari", "OG2-Editor",
                     "OG3-Membre", "OG5-Convidat"],
                        roles):
                    return file
            else:
                # Sesiones: Secretari, Editor ven todo
                if utils.checkhasRol(["OG1-Secretari", "OG2-Editor"], roles):
                    return file
                # Membre, Convidat: lógica especial con ambos ficheros
                elif utils.checkhasRol(["OG3-Membre", "OG5-Convidat"], roles):
                    if context.visiblefile and context.hiddenfile:
                        # Si hay ambos: solo ven hiddenfile
                        if hidden:
                            return file
                        else:
                            raise Unauthorized
                    else:
                        # Si hay solo uno: lo ven
                        return file
                # Afectat: lógica especial
                elif "OG4-Afectat" in roles:
                    if context.visiblefile and context.hiddenfile:
                        # Si hay ambos: solo ve visiblefile
                        if visible:
                            return file
                        else:
                            raise Unauthorized
                    elif context.hiddenfile:
                        # Si solo hay hiddenfile: sin acceso
                        raise Unauthorized
                    elif context.visiblefile:
                        # Si solo hay visiblefile: lo ve
                        return file
        elif sessio_state == "tancada":
            if is_acta_audio_or_annex:
                # Actas/audios/annex: incluye Afectat (sin Anónimo)
                if utils.checkhasRol(
                    ["OG1-Secretari", "OG2-Editor", "OG3-Membre",
                     "OG4-Afectat", "OG5-Convidat"],
                        roles):
                    return file
            else:
                # Sesiones: Secretari, Editor ven todo
                if utils.checkhasRol(["OG1-Secretari", "OG2-Editor"], roles):
                    return file
                # Membre, Convidat: lógica especial con ambos ficheros
                elif utils.checkhasRol(["OG3-Membre", "OG5-Convidat"], roles):
                    if context.visiblefile and context.hiddenfile:
                        # Si hay ambos: solo ven hiddenfile
                        if hidden:
                            return file
                        else:
                            raise Unauthorized
                    else:
                        # Si hay solo uno: lo ven
                        return file
                # Afectat: lógica especial (igual que en realitzada/en_correccio)
                elif "OG4-Afectat" in roles:
                    if context.visiblefile and context.hiddenfile:
                        # Si hay ambos: solo ve visiblefile
                        if visible:
                            return file
                        else:
                            raise Unauthorized
                    elif context.hiddenfile:
                        # Si solo hay hiddenfile: sin acceso
                        raise Unauthorized
                    elif context.visiblefile:
                        # Si solo hay visiblefile: lo ve
                        return file
                # Anónimos: sin acceso (pero con lógica especial legacy)
                else:
                    if context.visiblefile and context.hiddenfile:
                        # Si hay ambos: solo ven visiblefile
                        if visible:
                            return file
                        else:
                            raise Unauthorized
                    elif context.hiddenfile:
                        # Si solo hay hiddenfile: sin acceso
                        raise Unauthorized
                    elif context.visiblefile:
                        # Si solo hay visiblefile: lo ve
                        return file

    # Si llegamos aquí no se permite acceso
    raise Unauthorized
