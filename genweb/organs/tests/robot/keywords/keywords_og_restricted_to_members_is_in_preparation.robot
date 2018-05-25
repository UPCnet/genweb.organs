*** Settings ***

Library  Selenium2Library

Resource  keywords.robot
Resource  keywords_og.robot
Resource  keywords_og_checks.robot


*** Keywords ***

We make checks when the session is in preparation
  Log  \n*** Sessió en preparació ***  console=True
  We make the checks for OG secretary when the session is in preparation
  We make the checks for OG editor when the session is in preparation
  We make the checks for OG member when the session is in preparation
  We make the checks for OG affected when the session is in preparation
  We make the checks for not role user when the session is in preparation
  We make the checks for not validated user when the session is in preparation

We make the checks for OG secretary when the session is in preparation
  Log  \n- Usuari (SECRETARI):  console=True
  Login  ${SECRETARY_USER_NAME}  ${SECRETARY_USER_NAME}
  Check if can view portlet Navigation
  Check if can view list organs
  Check if can view list organs and types  Restringit a membres
  Check if can view OG
  Check if can view tab Sessions in a OG
  Check if can view tab Composition in a OG
  Check if can view tab Agreements in a OG
  Check if can view tab Acts in a OG
  Check if can view session in a OG
  Check if can view tab Call in a session
  Check if can view tab Members in a session
  Check if can view tab Agreements in a session
  Check if can view tab Act in a session
  Check if can view tab History in a session
  Check if can view button Add informational point in a session
  Check if can view button Add agreement in a session
  Check if can view button Agile creation in a session
  Check if can view button Number points in a session
  Check if can view button Number agreements in a session
  Check if can add Point in a point
  Check if can add Agreement in a point
  Check if can add Files in a point
  Check if can add Documents in a point
  Check if can view public file in a point
  Check if can view restricted file in a point
  Check if can add Points from the top menu
  Check if can add Act from the top menu
  Check if can add Agreement from the top menu
  Check if can view the edit bar in a point
  Check if can view the edit bar in a agreement
  Check if can view the edit bar in a act
  Check if can view the edit bar in a subpoint
  Check if can view public documents in the drop-down of session
  Check if the public document is opened in the same window
  Check if can view restricted documents in the drop-down of session
  Check if the restricted document is opened in the same window
  Check if can view public-restricted documents in the drop-down of session
  Check if the public-restricted document is opened in the same window
  Check if can view the public part in a document
  Check if can view the private part in a document
  Check if can view public files in the drop-down of session
  Check if the public file is opened in the same window
  Check if can view restricted files in the drop-down of session
  Check if the restricted file is opened in the same window
  Check if can view public-restricted files in the drop-down of session
  Check if the public-restricted file is opened in the same window
  Check if can view the public part in a file
  Check if can view the private part in a file
  Check if can view button Member message in a session
  Check if can view button Presentation mode in a session  False
  Check if can view button Send summary in a session  False
  Check if can view button Print in a session
  Check if can view button Preview in a act
  Check if can view button Download PDF file in a act

We make the checks for OG editor when the session is in preparation
  Log  \n- Usuari (EDITOR):  console=True
  Login  ${EDITOR_USER_NAME}  ${EDITOR_USER_NAME}
  Check if can view portlet Navigation
  Check if can view list organs
  Check if can view list organs and types  Restringit a membres
  Check if can view OG
  Check if can view tab Sessions in a OG
  Check if can view tab Composition in a OG
  Check if can view tab Agreements in a OG
  Check if can view tab Acts in a OG
  Check if can view session in a OG
  Check if can view tab Call in a session
  Check if can view tab Members in a session
  Check if can view tab Agreements in a session
  Check if can view tab Act in a session
  Check if can view tab History in a session  False
  Check if can view button Add informational point in a session
  Check if can view button Add agreement in a session
  Check if can view button Agile creation in a session
  Check if can view button Number points in a session
  Check if can view button Number agreements in a session
  Check if can add Point in a point
  Check if can add Agreement in a point
  Check if can add Files in a point
  Check if can add Documents in a point
  Check if can view public file in a point
  Check if can view restricted file in a point
  Check if can add Points from the top menu
  Check if can add Act from the top menu
  Check if can add Agreement from the top menu
  Check if can view the edit bar in a point
  Check if can view the edit bar in a agreement
  Check if can view the edit bar in a act
  Check if can view the edit bar in a subpoint
  Check if can view public documents in the drop-down of session
  Check if the public document is opened in the same window
  Check if can view restricted documents in the drop-down of session
  Check if the restricted document is opened in the same window
  Check if can view public-restricted documents in the drop-down of session
  Check if the public-restricted document is opened in the same window
  Check if can view the public part in a document
  Check if can view the private part in a document
  Check if can view public files in the drop-down of session
  Check if the public file is opened in the same window
  Check if can view restricted files in the drop-down of session
  Check if the restricted file is opened in the same window
  Check if can view public-restricted files in the drop-down of session
  Check if the public-restricted file is opened in the same window
  Check if can view the public part in a file
  Check if can view the private part in a file
  Check if can view button Member message in a session
  Check if can view button Presentation mode in a session  False
  Check if can view button Send summary in a session  False
  Check if can view button Print in a session
  Check if can view button Preview in a act
  Check if can view button Download PDF file in a act

We make the checks for OG member when the session is in preparation
  Log  \n- Usuari (MEMBRE):  console=True
  Login  ${MEMBER_USER_NAME}  ${MEMBER_USER_NAME}
  Check if can view portlet Navigation
  Check if can view list organs
  Check if can view list organs and types  Restringit a membres  False
  Check if can view OG
  Check if can view tab Sessions in a OG  False
  Check if can view tab Composition in a OG
  Check if can view tab Agreements in a OG  False
  Check if can view tab Acts in a OG  False
  Check if can view session in a OG  False

We make the checks for OG affected when the session is in preparation
  Log  \n- Usuari (AFECTAT):  console=True
  Login  ${AFFECTED_USER_NAME}  ${AFFECTED_USER_NAME}
  Check if can view portlet Navigation
  Check if can view list organs  False
  Check if can view list organs and types  Restringit a membres  False
  Check if can view OG  False

We make the checks for not role user when the session is in preparation
  Log  \n- Usuari sense rol:  console=True
  Login  ${VALIDATED_USER_NAME}  ${VALIDATED_USER_NAME}
  Check if can view portlet Navigation
  Check if can view list organs  False
  Check if can view list organs and types  Restringit a membres  False
  Check if can view OG  False

We make the checks for not validated user when the session is in preparation
  Log  \n- Usuari sense validarse:  console=True
  Logout
  Check if can view portlet Navigation
  Check if can view list organs  False
  Check if can view list organs and types  Restringit a membres  False
  Check if can view OG  False
