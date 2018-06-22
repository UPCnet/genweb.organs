# -*- coding: utf-8 -*-
from plone import api
from DateTime import DateTime
from plone.app.contentlisting.interfaces import IContentListing
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.PloneBatch import Batch
from Products.ZCTextIndex.ParseTree import ParseError
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.publisher.browser import BrowserView
from ZTUtils import make_query
from genweb.organs import permissions
from Acquisition import aq_inner
from plone.app.event.base import localized_today
from plone.app.event.base import get_events, construct_calendar
from plone.app.event.base import RET_MODE_OBJECTS
from plone.event.interfaces import IEventAccessor
from plone.app.event.portlets import get_calendar_url
from plone.app.event.base import first_weekday
import calendar
from plone.app.event.base import wkday_to_mon1

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
        from plone import api
        if not api.user.is_anonymous():
            return False
        return True

    def prev_month(self):
        year, month = self.year_month_display()
        year, prev_month = self.get_previous_month(year, month)
        return prev_month

    def prev_year(self):
        year, month = self.year_month_display()
        prev_year, month = self.get_previous_month(year, month)
        return prev_year

    def prev_query(self):
        return '?month=%s&year=%s' % (self.prev_month(), self.prev_year())

    def month_name(self):
        year, month = self.year_month_display()
        _ts = getToolByName(self.context, 'translation_service')
        return PLMF(_ts.month_msgid(month), default=_ts.month_english(month))

    def year(self):
        year, month = self.year_month_display()
        return year

    def next_month(self):
        year, month = self.year_month_display()
        year, next_month = self.get_next_month(year, month)
        return next_month

    def next_year(self):
        year, month = self.year_month_display()
        next_year, month = self.get_next_month(year, month)
        return next_year

    def next_query(self):
        return '?month=%s&year=%s' % (self.next_month(), self.next_year())

    def weekdays(self):
        # strftime %w interprets 0 as Sunday unlike the calendar.
        _ts = getToolByName(self.context, 'translation_service')
        cal = calendar.Calendar(first_weekday())
        strftime_wkdays = [
            wkday_to_mon1(day) for day in cal.iterweekdays()
        ]
        return [PLMF(_ts.day_msgid(day, format='s'), default=_ts.weekday_english(day, format='a')) for day in strftime_wkdays]

    def year_month_display(self):
        """ Return the year and month to display in the calendar.
        """
        context = aq_inner(self.context)
        request = self.request

        # Try to get year and month from request
        year = request.get('year', None)
        month = request.get('month', None)

        # Or use current date
        today = localized_today(context)
        if not year:
            year = today.year
        if not month:
            month = today.month

        # try to transform to number but fall back to current
        # date if this is ambiguous
        try:
            year, month = int(year), int(month)
        except (TypeError, ValueError):
            year, month = today.year, today.month

        return year, month

    def get_previous_month(self, year, month):
        if month == 0 or month == 1:
            month, year = 12, year - 1
        else:
            month -= 1
        return (year, month)

    def get_next_month(self, year, month):
        if month == 12:
            month, year = 1, year + 1
        else:
            month += 1
        return (year, month)

    def date_events_url(self, date):
        return '%s?mode=day&date=%s' % (get_calendar_url(self.context, None), date)

    def cal_data(self):
        """Calendar iterator over weeks and days of the month to display.
        """
        context = aq_inner(self.context)
        today = localized_today(context)
        year, month = self.year_month_display()
        self.cal = calendar.Calendar(first_weekday())
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]
        # import ipdb; ipdb.set_trace()

        # data = self.data
        query_kw = {}
        # if data.search_base:
        #     portal = getToolByName(context, 'portal_url').getPortalObject()
        #     query_kw['path'] = {'query': '%s%s' % (
        #         '/'.join(portal.getPhysicalPath()), data.search_base)}

        # if data.state:
        #     query_kw['review_state'] = data.state

        start = monthdates[0]
        end = monthdates[-1]
        events = get_events(context, start=start, end=end,
                            ret_mode=RET_MODE_OBJECTS,
                            expand=True, **query_kw)
        cal_dict = construct_calendar(events, start=start, end=end)

        # [[day1week1, day2week1, ... day7week1], [day1week2, ...]]
        caldata = [[]]
        for dat in monthdates:
            if len(caldata[-1]) == 7:
                caldata.append([])
            date_events = None
            isodat = dat.isoformat()
            if isodat in cal_dict:
                date_events = cal_dict[isodat]

            events_string = u""
            color = ''
            if date_events:
                for occ in date_events:
                    accessor = IEventAccessor(occ)
                    location = accessor.location
                    whole_day = accessor.whole_day
                    time = accessor.start.time().strftime('%H:%M')
                    color = occ.aq_parent.eventsColor
                    # TODO: make 24/12 hr format configurable
                    base = u'<a href="%s"><span class="title">%s</span> -'u'%s%s%s</a><br/>'
                    events_string += base % (
                        accessor.url,
                        accessor.title,
                        not whole_day and u' %s' % time or u'',
                        not whole_day and location and u', ' or u'',
                        location and u' %s' % location or u'')
                # More than one event in the same day, default color
                if len(date_events) > 1:
                    color = 'red'

            caldata[-1].append(
                {'date': dat,
                 'day': dat.day,
                 'prev_month': dat.month < month,
                 'next_month': dat.month > month,
                 'color': color,
                 'today':
                    dat.year == today.year and
                    dat.month == today.month and
                    dat.day == today.day,
                 'date_string': u"%s-%s-%s" % (dat.year, dat.month, dat.day),
                 'events_string': events_string,
                 'events': date_events})
        return caldata

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

        newresults = []
        new_path = []
        root_path = '/'.join(api.portal.get().getPhysicalPath())  # /998/govern
        lt = getToolByName(self, 'portal_languages')
        lang = lt.getPreferredLanguage()

        if query['latest_session']:
            if query['path'] == root_path + '/' + lang:
                query['path'] = [
                    root_path + '/' + lang + '/consell-de-govern/consell-de-govern/',
                    root_path + '/' + lang + '/cs/ple-del-consell-social/',
                    root_path + '/' + lang + '/claustre-universitari/claustre-universitari/']
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
                    if item.portal_type == 'genweb.organs.document':
                        if permissions.canViewDocument(self, item):
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
            # query['path'] = getNavigationRoot(self.context)
            # Added all defaults folders:
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
        used_types = ('genweb.organs.acord', 'genweb.organs.document', 'genweb.organs.punt')
        return self.filter_types(list(used_types))

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
