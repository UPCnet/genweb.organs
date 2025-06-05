# -*- coding: utf-8 -*-
"""Installer for the genweb.organs package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])
setup(
    name='genweb.organs',
    version='0.73.dev0',
    description="Paquet Organs de Govern amb jQuery i que s'integra a Genweb.",
    long_description=long_description,
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
    author='Plone Team',
    author_email='plone.team@upcnet.es',
    url='https://github.com/UPCnet/genweb.organs',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['genweb'],
    package_dir={'': 'src'},
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
    [console_scripts]
    update_locale = genweb.organs.locales.update:update_locale
    """,
)
