*** Settings ***

Force Tags  wip-not_in_docs

Resource  plone/app/robotframework/selenium.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Plone Tests Folders are created
    Go to  ${PLONE_URL}/ca
    Page should contain  Organ Tests