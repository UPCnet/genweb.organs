*** Settings ***

Force Tags  wip-not_in_docs

Library   Selenium2Library
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open browser  ${PLONE_URL}  chrome
Test Teardown  Close all browsers


*** Test Cases ***

Homepage is shown
  Given Go to  ${PLONE_URL}
  Then Page should contain  Identifica't
