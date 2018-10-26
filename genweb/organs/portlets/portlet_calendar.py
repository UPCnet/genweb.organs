# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.event.base import first_weekday
from plone.app.event.base import construct_calendar
from plone.app.event.base import localized_today
from plone.app.event.base import wkday_to_mon1
from plone.app.event.portlets import get_calendar_url
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from datetime import datetime
from plone.app.event.base import localized_now
from plone.event.interfaces import IEvent
from datetime import timedelta
from plone.event.interfaces import IEventAccessor
from operator import itemgetter
import time
from plone import api
import DateTime
import calendar


PLMF = MessageFactory('plonelocales')


class ICalendarOrgansPortlet(IPortletDataProvider):
    """A portlet displaying a calendar
    """


class Assignment(base.Assignment):
    implements(ICalendarOrgansPortlet)
    title = _(u'Organs Calendar')


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet_calendar.pt')

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

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

    def get_public_organs_fields(self):
        visibleItems = api.content.find(portal_type='genweb.organs.organgovern', visiblefields=True)
        items_path = []
        for obj in visibleItems:
            items_path.append(obj.getPath())
        return items_path

    def getclasstag_event(self, day):
        # Returns class color to render in the calendar
        classtag = ''
        if day['events']:
            if len(day['events']) > 1:
                classtag += ' event-multiple '
        return classtag

    def next3Events(self):
        """ Returns next 3 events based on public organs fields """
        formatDate = "%Y-%m-%d"
        if 'day' in self.request.form and 'year' in self.request.form and 'month' in self.request.form:
            today = '{}-{}-{}'.format(
                self.request.form['year'],
                self.request.form['month'],
                self.request.form['day'])
            tomorrow = '{}-{}-{}'.format(
                self.request.form['year'],
                self.request.form['month'],
                int(self.request.form['day']) + 1)
            dateEvent0 = datetime.strptime(today, formatDate)
            dateEvent1 = datetime.strptime(tomorrow, formatDate)
            # Shows only specified date (today)
            date_events = {'query': (dateEvent0, dateEvent1), 'range': 'min:max'}
        else:
            date = datetime.today().strftime(formatDate)
            dateEvent = datetime.strptime(date, formatDate)
            date_events = {'query': (dateEvent), 'range': 'min'}
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        limit = 3
        if api.user.is_anonymous():
            future_sessions = portal_catalog.unrestrictedSearchResults(
                portal_type='genweb.organs.sessio',
                sort_on='start',
                start=date_events,
                path=self.get_public_organs_fields(),
                sort_limit=limit
            )[:limit]
        else:
            future_sessions = portal_catalog.unrestrictedSearchResults(
                portal_type='genweb.organs.sessio',
                sort_on='start',
                start=date_events,
                sort_limit=limit
            )[:limit]

        future = []
        current_year = datetime.now().strftime('%Y')
        for session in future_sessions:
            obj = session._unrestrictedGetObject()
            event = IEventAccessor(obj)
            start = event.start.strftime('%d/%m')
            end = event.end.strftime('%d/%m')
            end = None if end == start else end
            if obj.start.strftime('%Y') == current_year:
                future.append(dict(
                    title=obj.aq_parent.title,
                    session_title=obj.title,
                    start=start,
                    end=end,
                    color=obj.eventsColor,
                    url=session.getPath()))
        return future

    @property
    def cal_data(self):
        """Calendar iterator over weeks and days of the month to display.
        """
        context = aq_inner(self.context)
        today = localized_today(context)
        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]
        start = monthdates[0]
        end = monthdates[-1]

        date_range_query = {'query': (start, end), 'range': 'min:max'}
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        if api.user.is_anonymous():
            items = portal_catalog.unrestrictedSearchResults(
                portal_type='genweb.organs.sessio',
                start=date_range_query,
                path=self.get_public_organs_fields())
            events = []
            for event in items:
                events.append(event._unrestrictedGetObject())
        else:
            items = portal_catalog.unrestrictedSearchResults(
                portal_type='genweb.organs.sessio',
                start=date_range_query)
            events = []
            username = api.user.get_current().id
            for event in items:
                organ = event._unrestrictedGetObject()
                roles = api.user.get_roles(username=username, obj=organ)
                if 'OG1-Secretari' in roles or 'OG2-Editor' in roles or 'OG3-Membre' in roles or 'OG4-Afectat' in roles or 'Manager' in roles or organ.aq_parent.visiblefields:
                    events.append(organ)

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

            color = ''
            if date_events:
                for occ in date_events:
                    color = occ.aq_parent.eventsColor

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
                 'events': date_events})
        return caldata


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
