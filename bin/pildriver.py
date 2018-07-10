#!/var/plone/python2.7/bin/python
"""PILdriver, an image-processing calculator using PIL.

An instance of class PILDriver is essentially a software stack machine
(Polish-notation interpreter) for sequencing PIL image
transformations.  The state of the instance is the interpreter stack.

The only method one will normally invoke after initialization is the
`execute' method.  This takes an argument list of tokens, pushes them
onto the instance's stack, and then tries to clear the stack by
successive evaluation of PILdriver operators.  Any part of the stack
not cleaned off persists and is part of the evaluation context for
the next call of the execute method.

PILDriver doesn't catch any exceptions, on the theory that these
are actually diagnostic information that should be interpreted by
the calling code.

When called as a script, the command-line arguments are passed to
a PILDriver instance.  If there are no command-line arguments, the
module runs an interactive interpreter, each line of which is split into
space-separated tokens and passed to the execute method.

In the method descriptions below, a first line beginning with the string
`usage:' means this method can be invoked with the token that follows
it.  Following <>-enclosed arguments describe how the method interprets
the entries on the stack.  Each argument specification begins with a
type specification: either `int', `float', `string', or `image'.

All operations consume their arguments off the stack (use `dup' to
keep copies around).  Use `verbose 1' to see the stack state displayed
before each operation.

Usage examples:

    `show crop 0 0 200 300 open test.png' loads test.png, crops out a portion
of its upper-left-hand corner and displays the cropped portion.

    `save rotated.png rotate 30 open test.tiff' loads test.tiff, rotates it
30 degrees, and saves the result as rotated.png (in PNG format).
"""
# by Eric S. Raymond <esr@thyrsus.com>
# $Id$

# TO DO:
# 1. Add PILFont capabilities, once that's documented.
# 2. Add PILDraw operations.
# 3. Add support for composing and decomposing multiple-image files.
#

from __future__ import print_function



import sys
sys.path[0:0] = [
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Plone-4.3.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Pillow-2.7.0-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.multilingual-2.0.5_upcnet-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.contenttypes-1.1b5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.upc-2.52-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.robotframework-1.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/robotframework_ride-1.5.2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/watchdog-0.8.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/robotframework_debuglibrary-0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.testrunner-4.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.schema-4.2.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.i18n-3.7.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.configuration-3.7.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.component-3.9.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/setuptools-36.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/selenium-2.43.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/robotsuite-1.6.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/robotframework_selenium2library-1.5.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/robotframework-2.8.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.uuid-1.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.testing-5.0.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.testing-4.2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.globalrequest-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Babel-1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PluggableAuthService-1.10.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PlonePAS-4.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.MailHost-2.13.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFPlone-4.3.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFCore-2.2.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.dexteritytextindexer-2.2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.stack-2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.core-4.8.49-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.grok-1.3.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.GenericSetup-1.7.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFQuickInstallerTool-3.0.12-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pytz-2013b-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.versioningbehavior-1.2.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.namedfile-2.0.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.relationfield-1.2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.querystring-1.1.10-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.dexterity-2.2.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.querystring-1.2.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.dexterity-2.0.16-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.event-1.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.contentmenu-2.0.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.relationfield-0.6.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.theme-2.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.contenttree-1.0.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.behavior-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.z3cform-0.7.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.registry-1.2.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PloneLanguageTool-3.2.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/wicked-1.1.12-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.theming-1.1.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.openid-2.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.iterate-2.1.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.caching-1.1.10-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFPlacefulWorkflow-1.5.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pathtools-0.1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/argh-0.26.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/PyYAML-3.12-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.interface-3.6.7-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.exceptions-3.6.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.event-3.5.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.i18nmessageid-3.5.3-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/unittest2-0.5.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/lxml-2.3.6-py2.7-linux-x86_64.egg',
  '/home/roberto/.local/lib/python2.7/site-packages',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/docutils-0.12-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/decorator-3.4.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.publisher-3.12.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.lifecycleevent-3.6.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.browserpage-3.12.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.testing-3.9.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Zope2-2.13.23-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.memoize-1.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.localsitemanager-2.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.site-3.9.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.dottedname-3.4.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.globalrequest-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PluginRegistry-1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFDefault-2.2.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.i18n-2.0.10-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.session-3.5.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.sendmail-3.7.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.deferredimport-3.5.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Persistence-2.13.2-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/DocumentTemplate-2.13.2-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/DateTime-3.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Acquisition-2.13.9-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/AccessControl-3.0.11-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.traversing-3.13.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.tales-3.5.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.tal-3.5.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.structuredtext-3.5.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.pagetemplate-3.6.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.location-3.9.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.deprecation-3.4.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.container-3.11.2-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.locales-3.6.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.autoinclude-0.3.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/transaction-1.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plonetheme.sunburst-1.4.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plonetheme.classic-1.3.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.registry-1.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.protect-3.0.12-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.portlets-2.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.portlet.static-2.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.portlet.collection-2.1.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.locking-2.0.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.intelligenttext-2.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.indexer-1.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.fieldsets-2.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.contentrules-2.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.browserlayer-2.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.batching-1.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.workflow-2.2.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.vocabularies-2.1.20-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.viewletmanager-2.0.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.uuid-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.users-1.2.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.upgrade-1.3.18-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.search-1.1.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.redirector-1.2.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.portlets-2.5.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.locales-4.3.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.linkintegrity-1.5.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.layout-2.3.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.jquerytools-1.7.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.jquery-1.8.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.i18n-2.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.form-2.2.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.folder-1.1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.discussion-2.2.15-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.customerize-1.2.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.controlpanel-2.3.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.contentrules-3.0.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.contentlisting-1.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.content-2.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.collection-1.0.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.blob-1.5.16-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.customerize-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/borg.localrole-3.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/archetypes.referencebrowserwidget-2.5.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/archetypes.querywidget-1.1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ZODB3-3.10.5-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.statusmessages-4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.TinyMCE-1.3.14-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ResourceRegistries-2.2.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PortalTransforms-2.1.10-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PlacelessTranslationService-2.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PasswordResetTool-2.0.18-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.MimetypesRegistry-2.0.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ExternalEditor-1.1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ExtendedPathIndex-3.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.DCWorkflow-2.2.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFUid-2.2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFFormController-3.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFEditions-2.2.16-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFDynamicViewFTI-4.1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFDiffTool-2.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFCalendar-2.2.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.CMFActionIcons-2.1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.Archetypes-1.9.10-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ATContentTypes-2.1.16-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ExtensionClass-2.13.2-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.publication-3.12.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ZSQLMethods-2.13.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.form-3.2.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.z3cform-0.8.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.supermodel-1.2.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.api-1.8.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/archetypes.multilingual-2.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.recaptcha-2.0a3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.recaptcha-2.1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pfg.drafts-1.1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.collage.ploneformgen-1.0a1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.pfg.dexterity-0.10.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.polls-1.6.2.upcnet-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.logosfooter-1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.banners-1.12-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/upcnet.stats-1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/upcnet.cas-1.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.windowZ-1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.Collage-1.4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PloneFormGen-1.7.17-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PloneLDAP-1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.packets-2.17-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.restapi-2.0.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ipdb-0.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/simplejson-2.5.2-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/elasticsearch-5.4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/souper.plone-1.2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pyquery-1.4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/quintagroup.seoptimizer-99.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/jarn.jsi18n-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/wildcard.foldercontents-1.2.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.tinymcetemplates-1.0b4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.workflowmanager-1.1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.lockingbehavior-1.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.referenceablebehavior-0.7.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/archetypes.schemaextender-2.1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.controlpanel-1.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.portlets-1.2.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.js-1.15-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.cdn-1.60-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/genweb.theme-2.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.contentprovider-3.7.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.annotation-3.5.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.viewlet-1.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.view-2.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.site-1.6.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.security-1.6.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.component-2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/grokcore.annotation-1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/martian-0.14-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.formlib-4.3.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.container-3.9.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/rwproperty-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.autoform-1.6.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.rfc822-1.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.security-3.7.4-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.formwidget.query-0.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.intid-1.0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.intid-1.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.intid-3.7.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.size-3.4.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.filerepresentation-3.6.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.browser-1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.synchronize-1.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.folder-1.0.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.alterego-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.schemaeditor-1.3.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.namedfile-1.0.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.textfield-1.2.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.z3cform.datetimewidget-1.2.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.recurrence-1.2.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.datetime-1.3.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.event-1.3.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/icalendar-4.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.elephantvocabulary-0.2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ZCatalog-2.13.27-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.DateRecurringIndex-2.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.browsermenu-3.9.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zc.relation-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.objpath-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.intid-3.7.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.formwidget.autocomplete-1.2.8-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/repoze.xmliter-0.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.resourceeditor-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.resource-1.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.transformchain-1.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.subrequest-1.6.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/roman-1.4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/diazo-1.0.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.openid-2.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.viewlet-3.7.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.zcmlhook-1.0b1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.browserresource-3.10.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.cachepurging-1.0.9-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.caching-1.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/python_dateutil-1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.proxy-3.6.1-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.contenttype-3.5.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.StandardCacheManagers-2.13.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PythonScripts-2.13.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.MIMETools-2.13.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ExternalMethod-2.13.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.BTreeFolder2-2.13.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.testbrowser-3.11.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.sequencesort-3.4.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.ptresource-3.9.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.processlifetime-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zLOG-2.11.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zExceptions-2.13.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zdaemon-2.0.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/tempstorage-2.12.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/initgroups-2.13.0-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ZopeUndo-2.12.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ZConfig-2.9.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/RestrictedPython-3.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Record-2.13.0-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ZCTextIndex-2.13.5-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.OFSP-2.13.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/MultiMapping-2.13.0-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Missing-2.13.1-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.ramcache-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/five.formlib-1.0.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Unidecode-0.4.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.keyring-3.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.broken-3.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zc.buildout-2.11.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.monkeypatcher-1.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.componentvocabulary-1.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.SecureMailHost-1.1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.contentmigration-2.1.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/feedparser-5.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.cachedescriptors-3.5.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.stringinterp-1.0.13-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.validation-2.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.scale-1.3.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.app.imaging-1.0.11-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zc.lockfile-1.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.content-3.5.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.outputfilters-1.15-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Markdown-2.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/python_gettext-1.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ZopeVersionControl-1.1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.copy-3.5.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.app.form-4.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.Marshall-2.1.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.datetime-3.4.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.ATReferenceBrowserWidget-3.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.error-3.7.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.authentication-3.7.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/norecaptcha-0.3.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.DataGridField-1.9.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.directives.dexterity-1.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/anz.casclient-1.1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/stripogram-1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.js.jqueryui-1.10.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.PythonField-1.1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.TemplateFields-1.2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.TALESField-1.1.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.LDAPUserFolder-2.27-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Products.LDAPMultiPlugins-1.14-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/PyJWT-1.6.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.rest-1.0.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ipython-5.3.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/souper-1.0.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/cssselect-1.0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/quintagroup.canonicalpath-0.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plone.directives.form-2.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/collective.z3cform.datagridfield-1.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pyScss-1.2.1-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.jbot-0.7.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.dublincore-3.7.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.copypastemove-3.7.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.keyreference-3.6.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/z3c.caching-2.0a1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/experimental.cssselect-0.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/python_openid-2.2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/mechanize-0.2.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.bforest-1.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/python_ldap-2.4.25-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/dataflake.fakeldap-2.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pexpect-4.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pathlib2-2.3.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/backports.shutil_get_terminal_size-1.0.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/Pygments-1.6-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/prompt_toolkit-1.0.15-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/traitlets-4.3.2-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/simplegeneric-0.8.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/pickleshare-0.7.4-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/repoze.catalog-0.8.3-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/node.ext.zodb-1.0.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ptyprocess-0.6.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/scandir-1.7-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/wcwidth-0.1.7-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/ipython_genutils-0.2.0-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/zope.index-3.6.4-py2.7-linux-x86_64.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/node-0.9.18.1-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/plumber-1.5-py2.7.egg',
  '/var/plone/genweb.organs/src/genweb.organs/eggs/odict-1.6.2-py2.7.egg',
  ]


from PIL import Image

class PILDriver:

    verbose = 0

    def do_verbose(self):
        """usage: verbose <int:num>

        Set verbosity flag from top of stack.
        """
        self.verbose = int(self.do_pop())

    # The evaluation stack (internal only)

    stack = []          # Stack of pending operations

    def push(self, item):
        "Push an argument onto the evaluation stack."
        self.stack = [item] + self.stack

    def top(self):
        "Return the top-of-stack element."
        return self.stack[0]

    # Stack manipulation (callable)

    def do_clear(self):
        """usage: clear

        Clear the stack.
        """
        self.stack = []

    def do_pop(self):
        """usage: pop

        Discard the top element on the stack.
        """
        top = self.stack[0]
        self.stack = self.stack[1:]
        return top

    def do_dup(self):
        """usage: dup

        Duplicate the top-of-stack item.
        """
        if hasattr(self, 'format'):     # If it's an image, do a real copy
            dup = self.stack[0].copy()
        else:
            dup = self.stack[0]
        self.stack = [dup] + self.stack

    def do_swap(self):
        """usage: swap

        Swap the top-of-stack item with the next one down.
        """
        self.stack = [self.stack[1], self.stack[0]] + self.stack[2:]

    # Image module functions (callable)

    def do_new(self):
        """usage: new <int:xsize> <int:ysize> <int:color>:

        Create and push a greyscale image of given size and color.
        """
        xsize = int(self.do_pop())
        ysize = int(self.do_pop())
        color = int(self.do_pop())
        self.push(Image.new("L", (xsize, ysize), color))

    def do_open(self):
        """usage: open <string:filename>

        Open the indicated image, read it, push the image on the stack.
        """
        self.push(Image.open(self.do_pop()))

    def do_blend(self):
        """usage: blend <image:pic1> <image:pic2> <float:alpha>

        Replace two images and an alpha with the blended image.
        """
        image1 = self.do_pop()
        image2 = self.do_pop()
        alpha = float(self.do_pop())
        self.push(Image.blend(image1, image2, alpha))

    def do_composite(self):
        """usage: composite <image:pic1> <image:pic2> <image:mask>

        Replace two images and a mask with their composite.
        """
        image1 = self.do_pop()
        image2 = self.do_pop()
        mask = self.do_pop()
        self.push(Image.composite(image1, image2, mask))

    def do_merge(self):
        """usage: merge <string:mode> <image:pic1> [<image:pic2> [<image:pic3> [<image:pic4>]]]

        Merge top-of stack images in a way described by the mode.
        """
        mode = self.do_pop()
        bandlist = []
        for band in mode:
            bandlist.append(self.do_pop())
        self.push(Image.merge(mode, bandlist))

    # Image class methods

    def do_convert(self):
        """usage: convert <string:mode> <image:pic1>

        Convert the top image to the given mode.
        """
        mode = self.do_pop()
        image = self.do_pop()
        self.push(image.convert(mode))

    def do_copy(self):
        """usage: copy <image:pic1>

        Make and push a true copy of the top image.
        """
        self.dup()

    def do_crop(self):
        """usage: crop <int:left> <int:upper> <int:right> <int:lower> <image:pic1>

        Crop and push a rectangular region from the current image.
        """
        left = int(self.do_pop())
        upper = int(self.do_pop())
        right = int(self.do_pop())
        lower = int(self.do_pop())
        image = self.do_pop()
        self.push(image.crop((left, upper, right, lower)))

    def do_draft(self):
        """usage: draft <string:mode> <int:xsize> <int:ysize>

        Configure the loader for a given mode and size.
        """
        mode = self.do_pop()
        xsize = int(self.do_pop())
        ysize = int(self.do_pop())
        self.push(self.draft(mode, (xsize, ysize)))

    def do_filter(self):
        """usage: filter <string:filtername> <image:pic1>

        Process the top image with the given filter.
        """
        from PIL import ImageFilter
        filter = eval("ImageFilter." + self.do_pop().upper())
        image = self.do_pop()
        self.push(image.filter(filter))

    def do_getbbox(self):
        """usage: getbbox

        Push left, upper, right, and lower pixel coordinates of the top image.
        """
        bounding_box = self.do_pop().getbbox()
        self.push(bounding_box[3])
        self.push(bounding_box[2])
        self.push(bounding_box[1])
        self.push(bounding_box[0])

    def do_getextrema(self):
        """usage: extrema

        Push minimum and maximum pixel values of the top image.
        """
        extrema = self.do_pop().extrema()
        self.push(extrema[1])
        self.push(extrema[0])

    def do_offset(self):
        """usage: offset <int:xoffset> <int:yoffset> <image:pic1>

        Offset the pixels in the top image.
        """
        xoff = int(self.do_pop())
        yoff = int(self.do_pop())
        image = self.do_pop()
        self.push(image.offset(xoff, yoff))

    def do_paste(self):
        """usage: paste <image:figure> <int:xoffset> <int:yoffset> <image:ground>

        Paste figure image into ground with upper left at given offsets.
        """
        figure = self.do_pop()
        xoff = int(self.do_pop())
        yoff = int(self.do_pop())
        ground = self.do_pop()
        if figure.mode == "RGBA":
            ground.paste(figure, (xoff, yoff), figure)
        else:
            ground.paste(figure, (xoff, yoff))
        self.push(ground)

    def do_resize(self):
        """usage: resize <int:xsize> <int:ysize> <image:pic1>

        Resize the top image.
        """
        ysize = int(self.do_pop())
        xsize = int(self.do_pop())
        image = self.do_pop()
        self.push(image.resize((xsize, ysize)))

    def do_rotate(self):
        """usage: rotate <int:angle> <image:pic1>

        Rotate image through a given angle
        """
        angle = int(self.do_pop())
        image = self.do_pop()
        self.push(image.rotate(angle))

    def do_save(self):
        """usage: save <string:filename> <image:pic1>

        Save image with default options.
        """
        filename = self.do_pop()
        image = self.do_pop()
        image.save(filename)

    def do_save2(self):
        """usage: save2 <string:filename> <string:options> <image:pic1>

        Save image with specified options.
        """
        filename = self.do_pop()
        options = self.do_pop()
        image = self.do_pop()
        image.save(filename, None, options)

    def do_show(self):
        """usage: show <image:pic1>

        Display and pop the top image.
        """
        self.do_pop().show()

    def do_thumbnail(self):
        """usage: thumbnail <int:xsize> <int:ysize> <image:pic1>

        Modify the top image in the stack to contain a thumbnail of itself.
        """
        ysize = int(self.do_pop())
        xsize = int(self.do_pop())
        self.top().thumbnail((xsize, ysize))

    def do_transpose(self):
        """usage: transpose <string:operator> <image:pic1>

        Transpose the top image.
        """
        transpose = self.do_pop().upper()
        image = self.do_pop()
        self.push(image.transpose(transpose))

    # Image attributes

    def do_format(self):
        """usage: format <image:pic1>

        Push the format of the top image onto the stack.
        """
        self.push(self.do_pop().format)

    def do_mode(self):
        """usage: mode <image:pic1>

        Push the mode of the top image onto the stack.
        """
        self.push(self.do_pop().mode)

    def do_size(self):
        """usage: size <image:pic1>

        Push the image size on the stack as (y, x).
        """
        size = self.do_pop().size
        self.push(size[0])
        self.push(size[1])

    # ImageChops operations

    def do_invert(self):
        """usage: invert <image:pic1>

        Invert the top image.
        """
        from PIL import ImageChops
        self.push(ImageChops.invert(self.do_pop()))

    def do_lighter(self):
        """usage: lighter <image:pic1> <image:pic2>

        Pop the two top images, push an image of the lighter pixels of both.
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        self.push(ImageChops.lighter(image1, image2))

    def do_darker(self):
        """usage: darker <image:pic1> <image:pic2>

        Pop the two top images, push an image of the darker pixels of both.
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        self.push(ImageChops.darker(image1, image2))

    def do_difference(self):
        """usage: difference <image:pic1> <image:pic2>

        Pop the two top images, push the difference image
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        self.push(ImageChops.difference(image1, image2))

    def do_multiply(self):
        """usage: multiply <image:pic1> <image:pic2>

        Pop the two top images, push the multiplication image.
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        self.push(ImageChops.multiply(image1, image2))

    def do_screen(self):
        """usage: screen <image:pic1> <image:pic2>

        Pop the two top images, superimpose their inverted versions.
        """
        from PIL import ImageChops
        image2 = self.do_pop()
        image1 = self.do_pop()
        self.push(ImageChops.screen(image1, image2))

    def do_add(self):
        """usage: add <image:pic1> <image:pic2> <int:offset> <float:scale>

        Pop the two top images, produce the scaled sum with offset.
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        scale = float(self.do_pop())
        offset = int(self.do_pop())
        self.push(ImageChops.add(image1, image2, scale, offset))

    def do_subtract(self):
        """usage: subtract <image:pic1> <image:pic2> <int:offset> <float:scale>

        Pop the two top images, produce the scaled difference with offset.
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        scale = float(self.do_pop())
        offset = int(self.do_pop())
        self.push(ImageChops.subtract(image1, image2, scale, offset))

    # ImageEnhance classes

    def do_color(self):
        """usage: color <image:pic1>

        Enhance color in the top image.
        """
        from PIL import ImageEnhance
        factor = float(self.do_pop())
        image = self.do_pop()
        enhancer = ImageEnhance.Color(image)
        self.push(enhancer.enhance(factor))

    def do_contrast(self):
        """usage: contrast <image:pic1>

        Enhance contrast in the top image.
        """
        from PIL import ImageEnhance
        factor = float(self.do_pop())
        image = self.do_pop()
        enhancer = ImageEnhance.Contrast(image)
        self.push(enhancer.enhance(factor))

    def do_brightness(self):
        """usage: brightness <image:pic1>

        Enhance brightness in the top image.
        """
        from PIL import ImageEnhance
        factor = float(self.do_pop())
        image = self.do_pop()
        enhancer = ImageEnhance.Brightness(image)
        self.push(enhancer.enhance(factor))

    def do_sharpness(self):
        """usage: sharpness <image:pic1>

        Enhance sharpness in the top image.
        """
        from PIL import ImageEnhance
        factor = float(self.do_pop())
        image = self.do_pop()
        enhancer = ImageEnhance.Sharpness(image)
        self.push(enhancer.enhance(factor))

    # The interpreter loop

    def execute(self, list):
        "Interpret a list of PILDriver commands."
        list.reverse()
        while len(list) > 0:
            self.push(list[0])
            list = list[1:]
            if self.verbose:
                print("Stack: " + repr(self.stack))
            top = self.top()
            if not isinstance(top, str):
                continue
            funcname = "do_" + top
            if not hasattr(self, funcname):
                continue
            else:
                self.do_pop()
                func = getattr(self, funcname)
                func()

if __name__ == '__main__':
    import sys
    try:
        import readline
    except ImportError:
        pass # not available on all platforms

    # If we see command-line arguments, interpret them as a stack state
    # and execute.  Otherwise go interactive.

    driver = PILDriver()
    if len(sys.argv[1:]) > 0:
        driver.execute(sys.argv[1:])
    else:
        print("PILDriver says hello.")
        while True:
            try:
                if sys.version_info[0] >= 3:
                    line = input('pildriver> ')
                else:
                    line = raw_input('pildriver> ')
            except EOFError:
                print("\nPILDriver says goodbye.")
                break
            driver.execute(line.split())
            print(driver.stack)

# The following sets edit modes for GNU EMACS
# Local Variables:
# mode:python
# End:
