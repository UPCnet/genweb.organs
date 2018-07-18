from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import first_weekday
from plone.app.event.base import get_events, construct_calendar
from plone.app.event.base import localized_today
from plone.app.event.base import wkday_to_mon1
from plone.app.event.portlets import get_calendar_url
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.event.interfaces import IEventAccessor
from plone.portlets.interfaces import IPortletDataProvider
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from datetime import datetime
from plone.app.event.base import localized_now
from plone.event.interfaces import IEvent
from datetime import timedelta
from plone import api

import calendar
import itertools


PLMF = MessageFactory('plonelocales')


class ICalendarOrgansPortlet(IPortletDataProvider):
    """A portlet displaying a calendar
    """


class Assignment(base.Assignment):
    implements(ICalendarOrgansPortlet)
    title = _(u'Organs Calendar')


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet_calendar.pt')

    def update(self):
        context = aq_inner(self.context)

        self.calendar_url = get_calendar_url(context, None)

        self.year, self.month = year, month = self.year_month_display()
        self.prev_year, self.prev_month = prev_year, prev_month = (
            self.get_previous_month(year, month))
        self.next_year, self.next_month = next_year, next_month = (
            self.get_next_month(year, month))
        # TODO: respect current url-query string
        self.prev_query = '?month=%s&year=%s' % (prev_month, prev_year)
        self.next_query = '?month=%s&year=%s' % (next_month, next_year)

        self.cal = calendar.Calendar(first_weekday())
        self._ts = getToolByName(context, 'translation_service')
        self.month_name = PLMF(
            self._ts.month_msgid(month),
            default=self._ts.month_english(month)
        )

        # strftime %w interprets 0 as Sunday unlike the calendar.
        strftime_wkdays = [
            wkday_to_mon1(day) for day in self.cal.iterweekdays()
        ]
        self.weekdays = [
            PLMF(self._ts.day_msgid(day, format='s'),
                 default=self._ts.weekday_english(day, format='a'))
            for day in strftime_wkdays
        ]

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
        return '%s?mode=day&date=%s' % (self.calendar_url, date)

    def get_public_organs_fields(self):
        visibleItems = api.content.find(portal_type='genweb.organs.organgovern', visiblefields=True)
        items_path = []
        for obj in visibleItems:
            items_path.append(obj.getPath())
        print items_path
        return items_path

    def getclasstag_event(self, day):
        # Returns class color to show in the calendar
        classtag = ''

        if day['events']:
            # if len(day['events']) > 1:
            if len(day['events']) > 1:
                classtag += ' event-multiple '
        return classtag

    def getDateEvents(self):
        formatDate = "%Y-%m-%d"
        if 'day' in self.request.form:
            date = '{}-{}-{}'.format(self.request.form['year'], self.request.form['month'], self.request.form['day'])
        else:
            date = datetime.today().strftime(formatDate)
        dateEvent = datetime.strptime(date, formatDate)
        return dateEvent

    def getNextThreeEvents(self):
        context = aq_inner(self.context)
        query_kw = {}

        events = get_events(
            context,
            ret_mode=RET_MODE_OBJECTS,
            expand=True,
            path=self.get_public_organs_fields(),
            **query_kw)
        events = self.filterNextEvents(events)
        events = self.filterOccurrenceEvents(events)

        list_events = []
        for event in events[:3]:
            list_events.append(self.getEventCalendarDict(event))

        return list_events

    def getEventCalendarDict(self, event):
        start = event.start.strftime('%d/%m')
        searchStart = event.start.strftime('%m/%s')
        end = event.end.strftime('%d/%m')
        end = None if end == start else end
        return dict(Title=event.title,
                    getURL=event.absolute_url(),
                    start=start,
                    searchStart=searchStart,
                    end=end,
                    community_type='event.community_type',
                    community_name=event.aq_parent.aq_parent.title,
                    community_url=event.aq_parent.aq_parent.absolute_url())

    def filterOccurrenceEvents(self, events):
        filter_events = []
        for event in events:
            if not IEvent.providedBy(event):
                ocurrence = event
                event = event.aq_parent
                if event not in filter_events:
                    event.ocstart = ocurrence.start
                    event.ocend = ocurrence.end
                    filter_events.append(event)
            else:
                filter_events.append(event)

        return filter_events

    def filterNextEvents(self, events):
        filter_events = []
        for event in events:
            if event.end > localized_now():
                filter_events.append(event)
        return filter_events

    def getDayEventsGroup(self):
        group_events = []
        if 'day' not in self.request.form and 'month' in self.request.form:
            return None

        if 'day' not in self.request.form and 'month' not in self.request.form:
            list_events = self.getNextThreeEvents()
        else:
            list_events = self.getDayEvents(self.getDateEvents())

        if len(list_events):
            list_events = sorted(list_events, key=lambda x: x['community_name'])
            for key, group in itertools.groupby(list_events, key=lambda x: x['community_name']):
                events = [event for event in group]
                events = sorted(events, key=lambda x: (x['searchStart'], x['Title']))
                group_events.append(dict(Title=key,
                                         getURL=events[0]['getURL'],
                                         community_url=events[0]['community_url'],
                                         community_type=events[0]['community_type'],
                                         community_name=events[0]['community_name'],
                                         num_events=len(events),
                                         events=events))
            return group_events
        else:
            return None

    def getDayEvents(self, date):
        events = self.getCalendarDict()
        list_events = []
        if date.strftime('%Y-%m-%d') in events:
            events = self.filterOccurrenceEvents(events[date.strftime('%Y-%m-%d')])
            for event in events:
                list_events.append(self.getEventCalendarDict(event))
        return list_events

    def getCalendarDict(self):
        context = aq_inner(self.context)
        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]

        query_kw = {}
        start = monthdates[0]
        end = monthdates[-1]
        events = get_events(context,
                            start=start - timedelta(days=30),
                            end=end,
                            ret_mode=RET_MODE_OBJECTS,
                            path=self.get_public_organs_fields(),
                            expand=True, **query_kw)
        return construct_calendar(events, start=start, end=end)

    @property
    def cal_data(self):
        """Calendar iterator over weeks and days of the month to display.
        """
        context = aq_inner(self.context)
        today = localized_today(context)
        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]

        query_kw = {}

        start = monthdates[0]
        end = monthdates[-1]

        events = get_events(
            context,
            start=start,
            end=end,
            ret_mode=RET_MODE_OBJECTS,
            expand=True,
            path=self.get_public_organs_fields(),
            **query_kw)

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
                    base = u'<a href="%s"><span class="title">%s</span>'\
                           u'%s%s%s</a><br/>'
                    events_string += base % (
                        accessor.url,
                        accessor.title,
                        not whole_day and u' %s' % time or u'',
                        not whole_day and location and u', ' or u'',
                        location and u' %s' % location or u'')

            caldata[-1].append(
                {'date': dat,
                 'day': dat.day,
                 'month': dat.month,
                 'year': dat.year,
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

    def Anon(self):
        if not api.user.is_anonymous():
            return False
        return True


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
