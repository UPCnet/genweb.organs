# -*- coding: utf-8 -*-
from zope.interface import implementer
from plone.dexterity.content import Item

from genweb.organs.content.organgovern.organgovern import IOrgangovern
from genweb.organs.content.sessio.sessio import ISessio
from genweb.organs.content.punt import IPunt
from genweb.organs.content.subpunt import ISubpunt
from genweb.organs.content.acta.acta import IActa
from genweb.organs.content.organsfolder.organsfolder import IOrgansfolder
from genweb.organs.content.file import IFile
from genweb.organs.content.document import IDocument
from genweb.organs.content.audio import IAudio
from genweb.organs.content.annex import IAnnex
from genweb.organs.content.acord import IAcord
from genweb.organs.content.votacio_acord import IVotacioAcord


@implementer(IOrgangovern)
class Organgovern(Item):
    pass


@implementer(ISessio)
class Sessio(Item):
    pass


@implementer(IPunt)
class Punt(Item):
    pass


@implementer(ISubpunt)
class Subpunt(Item):
    pass


@implementer(IActa)
class Acta(Item):
    pass


@implementer(IOrgansfolder)
class Organsfolder(Item):
    pass


@implementer(IFile)
class File(Item):
    pass


@implementer(IDocument)
class Document(Item):
    pass


@implementer(IAudio)
class Audio(Item):
    pass


@implementer(IAnnex)
class Annex(Item):
    pass


@implementer(IAcord)
class Acord(Item):
    pass


@implementer(IVotacioAcord)
class VotacioAcord(Item):
    pass
