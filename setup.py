# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.74.dev0'

README = open("README.rst").read()
HISTORY = open(os.path.join("docs", "HISTORY.rst")).read()

setup(name='genweb.organs',
      version=version,
      description="Paquet Organs de Govern amb jQuery i que s'integra a Genweb.",
      long_description=README + "\n" + HISTORY,
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='organs govern genweb jquery',
      author='plone.team@upcnet.es',
      author_email='plone.team@upcnet.es',
      url='https://github.com/UPCnet/genweb.organs',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['genweb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.dexteritytextindexer',
          'selenium',
          'pdfkit'
      ],
      extras_require={'test': ['plone.app.testing',
                               'plone.app.testing[robot]>=4.2.2',
                               'plone.app.robotframework[debug]']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
