# -*- coding: utf-8 -*-
from zope.interface import implements
from plone.dexterity.content import Item

from genweb.organs.content.organgovern import IOrgangovern
from genweb.organs.content.sessio import ISessio
from genweb.organs.content.punt import IPunt
from genweb.organs.content.subpunt import ISubpunt
from genweb.organs.content.acta import IActa
from genweb.organs.content.organsfolder import IOrgansfolder
from genweb.organs.content.file import IFile
from genweb.organs.content.document import IDocument
from genweb.organs.content.audio import IAudio


class Organgovern(Item):
    implements(IOrgangovern)


class Sessio(Item):
    implements(ISessio)


class Punt(Item):
    implements(IPunt)


class Subpunt(Item):
    implements(ISubpunt)


class Acta(Item):
    implements(IActa)


class Organsfolder(Item):
    implements(IOrgansfolder)


class File(Item):
    implements(IFile)


class Document(Item):
    implements(IDocument)


class Audio(Item):
    implements(IAudio)
