# genweb.organs
Paquet Organs de Govern amb jQuery i que s'integra a Genweb

[![Tests](https://github.com/UPCnet/genweb.organs/actions/workflows/test.yml/badge.svg?branch=pyto3)](https://github.com/UPCnet/genweb.organs/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Plone](https://img.shields.io/badge/plone-6.0.15-blue.svg)](https://plone.org)


Installation
============

Primer cal instal·lar i configurar el paquet Genweb UPC i posteriorment s'instal·la aquest paquet.


Information
===========

organs_one_state_workflow -> Tots els elements de tipus genweb.organs són públics i només hi ha un estat.

organs_sessio_workflow --> Workflow aplicat a la Sessió, i conté els estats:
    Planificada / Convocada / Realitzada / Tancada / En modificacio (hi ha un fake estat pre_convoque)

    Només poden passar a l'estat en modificació, els OG1-Secretari.


Testing
=======

Open console and execute:

    Execute all of organ_obert:

        ./bin/test --all -m  genweb.organs  -t test_organ_obert

    Or, individually:

        ./bin/test --all -m  genweb.organs  -t test_organ_obert_secretari
        ./bin/test --all -m  genweb.organs  -t test_organ_obert_editor
        ./bin/test --all -m  genweb.organs  -t test_organ_obert_membre
        ./bin/test --all -m  genweb.organs  -t test_organ_obert_afectat
        ./bin/test --all -m  genweb.organs  -t test_organ_obert_anonim

    In case of Robot tests (none):

    ROBOT_BROWSER=chrome ./bin/test --all -m  genweb.organs  -t test_organ_obert_secretari



Test commands
=============

STOP on first test error
   ./bin/test --all -m  genweb.organs  -t test_organ_obert_secretari -D
