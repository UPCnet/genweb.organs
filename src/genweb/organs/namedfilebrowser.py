# -*- coding: utf-8 -*-
"""Adaptación a Plone 6 / Python 3 del navegador de ficheros usado por genweb.organs.

El módulo proporciona dos vistas:
  • @@download  → descarga el fichero respetando permisos
  • @@display-file → muestra/embebe el fichero (PDF, audio…) respetando permisos

Cambios sobre la versión de Plone 4:
  * El check de si *genweb.organs* está instalado ya no usa *portal_quickinstaller* (retirado en Plone 6).
    Se comprueba simplemente  importando el paquete.
  * Se añaden *type hints* y se simplifica la lógica de detección de permisos.
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
    """Obtiene el objeto *NamedFile* respetando la lógica de permisos de Organs."""

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

    def has(*rs):
        return utils.checkhasRol(list(rs), roles)

    # Mapear reglas según organ_type / estado / fieldname ------------------
    visible = view.fieldname == "visiblefile"
    hidden = view.fieldname == "hiddenfile"

    if organ_type == "open_organ":
        if sessio_state in {"convocada", "realitzada", "tancada"}:
            # abierto => todo el mundo puede ver los visibles
            if visible:
                return file
            # los ocultos solo ciertos roles
            if hidden and has("OG1-Secretari", "OG2-Editor", "OG3-Membre"):
                return file
        elif sessio_state == "planificada":
            if has("OG1-Secretari", "OG2-Editor"):
                return file
    elif organ_type == "restricted_to_members_organ":
        if has("OG1-Secretari", "OG2-Editor", "OG3-Membre"):
            return file
    elif organ_type == "restricted_to_affected_organ":
        if has("OG1-Secretari", "OG2-Editor", "OG3-Membre", "OG4-Afectat"):
            return file

    # Si llegamos aquí no se permite acceso
    raise Unauthorized
