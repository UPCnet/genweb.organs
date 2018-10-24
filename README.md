# genweb.organs
Paquet Organs de Govern amb jQuery i que s'integra a Genweb

[![Build Status](https://travis-ci.org/UPCnet/genweb.organs.svg?branch=master)](https://travis-ci.org/UPCnet/genweb.organs)

[![Coverage Status](https://coveralls.io/repos/github/UPCnet/genweb.organs/badge.svg)](https://coveralls.io/github/UPCnet/genweb.organs)


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
