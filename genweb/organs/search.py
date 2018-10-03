# -*- coding: utf-8 -*-
from plone import api
from DateTime import DateTime
from plone.app.contentlisting.interfaces import IContentListing
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.ZCTextIndex.ParseTree import ParseError
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.publisher.browser import BrowserView
from ZTUtils import make_query
# from operator import itemgetter
from genweb.organs import permissions

PLMF = MessageFactory('plonelocales')
_ = MessageFactory('plone')

# We should accept both a simple space, unicode u'\u0020 but also a
# multi-space, so called 'waji-kankaku', unicode u'\u3000'
MULTISPACE = u'\u3000'.encode('utf-8')
EVER = DateTime('1970/01/03')


def quote_chars(s):
    # We need to quote parentheses when searching text indices
    if '(' in s:
        s = s.replace('(', '"("')
    if ')' in s:
        s = s.replace(')', '")"')
    if MULTISPACE in s:
        s = s.replace(MULTISPACE, ' ')
    return s


class Search(BrowserView):

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def getOwnOrgans(self):
        if not api.user.is_anonymous():
            results = []
            portal_catalog = getToolByName(self, 'portal_catalog')
            root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
            lt = getToolByName(self, 'portal_languages')
            lang = lt.getPreferredLanguage()
            values = portal_catalog.searchResults(
                portal_type=['genweb.organs.organgovern'],
                sort_on='created',
                sort_order='reverse',
                path=root_path + '/' + lang)
            for obj in values:
                organ = obj.getObject()
                username = api.user.get_current().id
                all_roles = api.user.get_roles(username=username, obj=organ)
                roles = [o for o in all_roles if o in ['OG1-Secretari', 'OG2-Editor', 'OG3-Membre', 'OG4-Afectat']]
                sessionpath = organ.absolute_url()
                if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles:
                    results.append(dict(
                        url=sessionpath,
                        title=organ.title,
                        color=organ.eventsColor,
                        role=roles))
            if results:
                return results
            else:
                return False
        else:
            return False

    valid_keys = ('sort_on', 'sort_order', 'sort_limit', 'fq', 'fl', 'facet')

    def results(self, query=None, batch=True, b_size=50, b_start=0):
        """ Get properly wrapped search results from the catalog.
        Everything in Plone that performs searches should go through this view.
        'query' should be a dictionary of catalog parameters.
        """
        if query is None:
            query = {}
        if batch:
            query['b_start'] = b_start = int(b_start)
            query['b_size'] = b_size
        query = self.filter_query(query)
        query['sort_order'] = 'reverse'
        newresults = []
        new_path = []
        root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
        lt = getToolByName(self, 'portal_languages')
        lang = lt.getPreferredLanguage()
        query_paths = [
            root_path + '/' + lang + '/consell-de-govern/consell-de-govern/',
            root_path + '/' + lang + '/cs/ple-del-consell-social/',
            root_path + '/' + lang + '/claustre-universitari/claustre-universitari/']
        not_view = False
        if type(query['path']) == str:
            if query['path'] not in query_paths:
                not_view = True
        else:
            for value in query['path']:
                if value not in query_paths:
                    not_view = True
        if not_view:
            return None
        # if query['path'] not in query_paths:
            # import ipdb; ipdb.set_trace()
            # if query['path'] == '/empty_path/'
            # return None
            # else:
                # If path is hacked and not in search paths, force default path
                # query['path'] = root_path + '/' + lang + '/consell-de-govern/consell-de-govern/'
        if query['latest_session']:
            # if query['path'] == root_path + '/' + lang:
            #     query['path'] = query_paths
            if isinstance(query['path'], list):
                for organ in query['path']:
                    session_path = api.content.find(
                        path=organ,
                        portal_type='genweb.organs.sessio',
                        sort_on='created',
                        sort_order='reverse')
                    if session_path:
                        new_path.append(session_path[0].getPath())
            if isinstance(query['path'], str):
                session_path = api.content.find(
                    path=query['path'],
                    portal_type='genweb.organs.sessio',
                    sort_on='created',
                    sort_order='reverse')
                if session_path:
                    new_path.append(session_path[0].getPath())
            query['path'] = new_path
        # Make default view return 0 results
        if 'SearchableText' not in query:
            # La primera vez, sin seleccionar nada, están marcados todos los elementos
            # Cogemos por ejemplo el Folder para hacer el check
            if 'Folder' in query['portal_type']:
                return None
        if 'genweb.organs.punt' in query['portal_type']:
            query['portal_type'].append('genweb.organs.subpunt')
        if query is None:
            results = []
        else:
            catalog = getToolByName(self.context, 'portal_catalog')
            try:
                results = catalog(**query)
                for res in results:
                    item = res.getObject()
                    if item.portal_type == 'genweb.organs.punt':
                        if permissions.canViewPunt(self, item):
                            newresults.append(res)
                    if item.portal_type == 'genweb.organs.subpunt':
                        if permissions.canViewSubpunt(self, item):
                            newresults.append(res)
                    if item.portal_type == 'genweb.organs.acord':
                        if permissions.canViewAcord(self, item):
                            newresults.append(res)
            except ParseError:
                return []

        results = IContentListing(newresults)
        if batch:
            results = Batch(results, b_size, b_start)
        return results

    def filter_query(self, query):
        request = self.request

        catalog = getToolByName(self.context, 'portal_catalog')
        valid_indexes = tuple(catalog.indexes())
        valid_keys = self.valid_keys + valid_indexes
        text = query.get('SearchableText', None)
        if text is None:
            text = request.form.get('SearchableText', '')
        if not text:
            # Without text, must provide a meaningful non-empty search
            valid = set(valid_indexes).intersection(request.form.keys()) or \
                set(valid_indexes).intersection(query.keys())
            if not valid:
                return

        for k, v in request.form.items():
            if v and ((k in valid_keys) or k.startswith('facet.')):
                query[k] = v
        if text:
            query['SearchableText'] = quote_chars(text)

        # don't filter on created at all if we want all results
        created = query.get('created')
        # Add new prperty to check if they are searching in latest session
        query['latest_session'] = False
        if created:
            if created['query'][0].ISO() == '1900-11-12T00:00:00':  # Fake to simulate LAST_SESSION
                # Search latest session bassed on params
                query['latest_session'] = True
            else:
                try:
                    if created.get('query') and created['query'][0] <= EVER:
                        del query['created']
                except AttributeError:
                    # created not a mapping
                    del query['created']

        # respect `types_not_searched` setting
        types = query.get('portal_type', [])
        if 'query' in types:
            types = types['query']
        query['portal_type'] = self.filter_types(types)
        # respect effective/expiration date
        query['show_inactive'] = False
        # respect navigation root
        if 'path' not in query:
            # Added /Plone/ca
            # query['path'] = '/all_checked/'
            # getNavigationRoot(self.context)
            # Added all defaults folders:
            if 'genweb.organs.acord' or 'genweb.organs.punt' in query['portal_type']:
                query['path'] = '/empty_path/'
            else:
                root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
                lt = getToolByName(self, 'portal_languages')
                lang = lt.getPreferredLanguage()
                query['path'] = [
                    root_path + '/' + lang + '/consell-de-govern/consell-de-govern/',
                    root_path + '/' + lang + '/cs/ple-del-consell-social/',
                    root_path + '/' + lang + '/claustre-universitari/claustre-universitari/']
        return query

    def filter_types(self, types):
        plone_utils = getToolByName(self.context, 'plone_utils')
        if not isinstance(types, list):
            types = [types]
        return plone_utils.getUserFriendlyTypes(types)

    def types_list(self):
        # only show the types of Organs de Govern
        # removed subpunt because visually is the same that punt.
        # Subpunt is added in other part of code
        # catalog = getToolByName(self.context, 'portal_catalog')
        # used_types = catalog._catalog.getIndex('portal_type').uniqueValues()
        used_types = ('genweb.organs.acord', 'genweb.organs.punt')
        return sorted(self.filter_types(list(used_types)))

    def getLatestCDG(self):
        """ Retorna ultima sessió consell de govern """
        root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
        lt = getToolByName(self, 'portal_languages')
        lang = lt.getPreferredLanguage()
        portal_catalog = getToolByName(self, 'portal_catalog')
        item = portal_catalog.searchResults(
            portal_type=['genweb.organs.sessio'],
            path=root_path + "/" + lang + "/consell-de-govern/consell-de-govern",
            sort_on='created',
            sort_order='reverse')
        if item:
            title = item[0].Title
            url = item[0].getPath()
            return dict(title=title, url=url)
        else:
            return None

    def getLatestCS(self):
        """ Retorna ultima sessió consell social """
        root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
        lt = getToolByName(self, 'portal_languages')
        lang = lt.getPreferredLanguage()
        portal_catalog = getToolByName(self, 'portal_catalog')
        item = portal_catalog.searchResults(
            portal_type=['genweb.organs.sessio'],
            path=root_path + "/" + lang + "/cs/ple-del-consell-social",
            sort_on='created',
            sort_order='reverse')
        if item:
            title = item[0].Title
            url = item[0].getPath()
            return dict(title=title, url=url)
        else:
            return None

    def getLatestCU(self):
        """ Retorna ultima sessió claustre universitari """
        root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
        lt = getToolByName(self, 'portal_languages')
        lang = lt.getPreferredLanguage()
        portal_catalog = getToolByName(self, 'portal_catalog')
        item = portal_catalog.searchResults(
            portal_type=['genweb.organs.sessio'],
            path=root_path + "/" + lang + "/claustre-universitari/claustre-universitari",
            sort_on='created',
            sort_order='reverse')
        if item:
            title = item[0].Title
            url = item[0].getPath()
            return dict(title=title, url=url)
        else:
            return None

    def sort_options(self):
        """ Sorting options for search results view. """
        return (
            SortOption(
                self.request, _(u'date (newest first)'),
                'Date', reverse=True
            ),
            SortOption(self.request, _(u'alphabetically'), 'sortable_title'),
        )

    def breadcrumbs(self, item):
        obj = item.getObject()
        view = getMultiAdapter((obj, self.request), name='breadcrumbs_view')
        # cut off the item itself
        breadcrumbs = list(view.breadcrumbs())[:-1]
        # Fixed to Remove Unit OG Folder Name
        breadcrumbs = breadcrumbs[1:]
        if len(breadcrumbs) == 0:
            # don't show breadcrumbs if we only have a single element
            return None
        if len(breadcrumbs) > 3:
            # if we have too long breadcrumbs, emit the middle elements
            empty = {'absolute_url': '', 'Title': unicode('…', 'utf-8')}
            breadcrumbs = [breadcrumbs[0], empty] + breadcrumbs[-2:]
        return breadcrumbs

    def navroot_url(self):
        if not hasattr(self, '_navroot_url'):
            state = self.context.unrestrictedTraverse('@@plone_portal_state')
            self._navroot_url = state.navigation_root_url()
        return self._navroot_url

    def root_path(self):
        path = '/'.join(api.portal.get().getPhysicalPath())
        return path

    def getPage(self):
        """ Retorna la pagina benvingut """
        portal_catalog = getToolByName(self, 'portal_catalog')
        item = portal_catalog.searchResults(
            portal_type=['Document'], id='benvingut')
        if item:
            return item[0].getObject().text.output
        else:
            return None


class SortOption(object):

    def __init__(self, request, title, sortkey='', reverse=False):
        self.request = request
        self.title = title
        self.sortkey = sortkey
        self.reverse = reverse

    def selected(self):
        sort_on = self.request.get('sort_on', '')
        return sort_on == self.sortkey

    def url(self):
        q = {}
        q.update(self.request.form)
        if 'sort_on' in q.keys():
            del q['sort_on']
        if 'sort_order' in q.keys():
            del q['sort_order']
        q['sort_on'] = self.sortkey
        if self.reverse:
            q['sort_order'] = 'reverse'

        base_url = self.request.URL
        # After the AJAX call the request is changed and thus the URL part of
        # it as well. In this case we need to tweak the URL to point to have
        # correct URLs
        if '@@updated_search' in base_url:
            base_url = base_url.replace('@@updated_search', '@@search')
        return base_url + '?' + make_query(q)
