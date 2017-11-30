*** Settings ***

Force Tags  wip-not_in_docs

Library  Selenium2Library
Library  Collections

Resource  plone/app/robotframework/selenium.robot
Resource  keywords/keywords.robot
Resource  keywords/keywords_og.robot
Resource  keywords/keywords_og_checks.robot
Resource  keywords/keywords_og_restricted_to_affecteds_is_in_preparation.robot
Resource  keywords/keywords_og_restricted_to_affecteds_is_in_convened.robot
Resource  keywords/keywords_og_restricted_to_affecteds_is_done.robot
Resource  keywords/keywords_og_restricted_to_affecteds_is_close.robot
Resource  keywords/keywords_og_restricted_to_affecteds_is_in_correction.robot

Test Setup  Open browser  ${PLONE_URL}  chrome
Test Teardown  Close all browsers


*** Test Cases ***

OG restricted to affecteds
  Everything is configured
  We make the checks for the differents users when the session is in preparation


*** Keywords ***

Everything is configured
  Log  \n===== OG restringit a afectats =====\n  console=True
  Initial configurations
  #Create a different users
  Create a OG affected user
  Create a organs folder
  Create a OG restricted to affecteds
  Create a different contents
  Add portlet Navigation

Create a OG restricted to affecteds
  Create a OG  restricted_to_affected_organ
  Log  Creat OG restringit a afectats  console=True

We make the checks for the differents users when the session is in preparation
  #We make checks when the session is in preparation
  #We make checks when the session is in convened
  Change session state to convened
  We make checks when the session is done
  We make checks when the session is close
  We make checks when the session is in correction
