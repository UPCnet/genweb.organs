*** Settings ***

Force Tags  wip-not_in_docs

Library  Selenium2Library
Library  Collections

Resource  plone/app/robotframework/selenium.robot
Resource  keywords/keywords.robot
Resource  keywords/keywords_og.robot
Resource  keywords/keywords_og_checks.robot
Resource  keywords/keywords_og_restricted_to_members_is_in_preparation.robot
Resource  keywords/keywords_og_restricted_to_members_is_in_convened.robot
Resource  keywords/keywords_og_restricted_to_members_is_done.robot
Resource  keywords/keywords_og_restricted_to_members_is_close.robot
Resource  keywords/keywords_og_restricted_to_members_is_in_correction.robot

Test Setup  Open browser  ${PLONE_URL}  chrome
#Test Teardown  Close all browsers


*** Test Cases ***

OG restricted to members
  Everything is configured
  We make the checks for the differents users when the session is in preparation


*** Keywords ***

Everything is configured
  Log  \n===== OG restringit a membres =====\n  console=True
  Initial configurations
  Create a different users
  Create a organs folder
  Create a OG restricted to members
  Create a different contents
  Add portlet Navigation

Create a OG restricted to members
  Create a OG  restricted_to_members_organ
  Log  Creat OG restringit a membres  console=True

We make the checks for the differents users when the session is in preparation
  We make checks when the session is in preparation
  We make checks when the session is in convened
  We make checks when the session is done
  We make checks when the session is close
  We make checks when the session is in correction
