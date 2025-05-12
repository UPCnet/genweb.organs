# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.73.dev0'

README = open("README.rst").read()
HISTORY = open(os.path.join("docs", "HISTORY.rst")).read()

setup(
    name='genweb.organs',
    version=version,
    description="Paquet Organs de Govern amb jQuery i que s'integra a Genweb.",
    long_description=README + "\n" + HISTORY,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='organs govern genweb',
    author='plone.team@upcnet.es',
    author_email='plone.team@upcnet.es',
    url='https://github.com/UPCnet/genweb.organs',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['genweb'],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.8',
    install_requires=[
        'setuptools',
        'Plone >=6.0.0',
        'plone.app.dexterity',
        'plone.app.contenttypes',
        'plone.app.registry',
        'plone.api',
        'collective.dexteritytextindexer',
        'pdfkit',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.robotframework[debug]',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
