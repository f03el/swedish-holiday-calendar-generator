#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generator for Swedish holidays, producing a calendar on iCalendar
format (RFC 5545). Event dates have been picked from Swedish Wikipedia:
https://sv.wikipedia.org/wiki/Helgdagar_i_Sverige
"""

from enum import Enum
from datetime import date, timedelta
import uuid
import argparse
import dateutil.easter
import icalendar
from icalendar import Event, vRecur, vFrequency, vWeekday


def generate(start_year, count):
    """Generate a calendar containing the holiday events.
    """
    calendar = Calendar()
    calendar.add('prodid', '-//Mozilla.org/NONSGML Mozilla Calendar V1.1//')
    calendar.add('version', '2.0')
    calendar.add_component(FixedHoliday(date(start_year, 1, 1), 'Nyårsdagen'))
    calendar.add_component(FixedHoliday(date(start_year, 1, 5), 'Trettondagsafton', Work.DEPENDS))
    calendar.add_component(FixedHoliday(date(start_year, 1, 6), 'Trettondedag jul'))
    for i in range(count):
        calendar.add_easter(start_year + i)
    calendar.add_component(FixedHoliday(date(start_year, 4, 30), 'Valborgsmässoafton',
                                        Work.DEPENDS))
    calendar.add_component(FixedHoliday(date(start_year, 5, 1), 'Första maj'))
    calendar.add_component(FixedHoliday(date(start_year, 6, 6), 'Sveriges nationaldag'))
    calendar.add_midsummers_eve(start_year)
    calendar.add_midsummer_day(start_year)
    calendar.add_all_saints_eve(start_year)
    calendar.add_all_saints_day(start_year)
    calendar.add_component(FixedHoliday(date(start_year, 12, 24), 'Julafton', Work.DEFACTO))
    calendar.add_component(FixedHoliday(date(start_year, 12, 25), 'Juldagen'))
    calendar.add_component(FixedHoliday(date(start_year, 12, 26), 'Annandag jul'))
    calendar.add_component(FixedHoliday(date(start_year, 12, 31), 'Nyårsafton', Work.DEFACTO))
    return calendar


class Work(Enum):
    """Enum for indicating how work is affected."""
    FREE = 0
    DEFACTO = 1
    DEPENDS = 2


class Holiday(Event):
    """Base event representing a holiday."""

    def __init__(self, dtstart, summary, work=Work.FREE):
        super().__init__()
        self.add('uid', uuid.uuid1())
        self.add('transp', 'TRANSPARENT')
        self.add('dtstart', dtstart)
        self.add('summary', summary)
        if work == Work.DEPENDS:
            self.add('categories', 'Ledighet enligt avtal')
            self.add('description',
                     ('Denna dag har inte lagstadgad ställning som arbetsfri'
                      ' dag. Många arbetsplatser har ändå förkortad arbetstid'
                      ' enligt kollektivavtal eller lokala avtal.'))
        elif work == Work.DEFACTO:
            self.add('description',
                     ('Denna dag räknas som söndag enligt 3 a § i Semesterlagen'
                      ' och är därmed arbetsfri.'))


class FixedHoliday(Holiday):
    """Holiday recurring on a fixed date every year."""

    def __init__(self, dtstart, summary, work=Work.FREE):
        super().__init__(dtstart, summary, work)
        rrule = vRecur()
        rrule['FREQ'] = vFrequency('YEARLY')
        self.add('rrule', rrule)

class Calendar(icalendar.Calendar):
    """Calendar with some specialized methods for adding events."""

    def add_easter(self, year):
        """Add events for holidays that depend on when easter falls the given year."""
        easter = dateutil.easter.easter(year)
        self.add_component(Holiday(easter - timedelta(days=3), 'Skärtorsdagen',
                                   Work.DEPENDS))
        self.add_component(Holiday(easter - timedelta(days=2), 'Långfredagen'))
        self.add_component(Holiday(easter - timedelta(days=1), 'Påskafton'))
        self.add_component(Holiday(easter, 'Påskdagen'))
        self.add_component(Holiday(easter + timedelta(days=1), 'Annandag påsk'))
        self.add_component(Holiday(easter + timedelta(weeks=5, days=4),
                                   'Kristi himmelsfärdsdag'))
        self.add_component(Holiday(easter + timedelta(weeks=6, days=6),
                                   'Pingstafton'))
        self.add_component(Holiday(easter + timedelta(weeks=7), 'Pingstdagen'))

    def add_midsummers_eve(self, year):
        """Add recurring event for midsummer's eve."""
        event = Holiday(date(year, 1, 1), 'Midsommarafton', Work.DEFACTO)
        rrule = vRecur()
        rrule['FREQ'] = vFrequency('YEARLY')
        rrule['BYDAY'] = vWeekday('FR')
        rrule['BYMONTHDAY'] = (19, 20, 21, 22, 23, 24, 25)
        rrule['BYMONTH'] = 6
        event.add('rrule', rrule)
        self.add_component(event)

    def add_midsummer_day(self, year):
        """Add recurring event for the midsummer day."""
        event = Holiday(date(year, 1, 1), 'Midsommardagen')
        rrule = vRecur()
        rrule['FREQ'] = vFrequency('YEARLY')
        rrule['BYDAY'] = vWeekday('SA')
        rrule['BYMONTHDAY'] = (20, 21, 22, 23, 24, 25, 26)
        rrule['BYMONTH'] = 6
        event.add('rrule', rrule)
        self.add_component(event)

    def add_all_saints_eve(self, year):
        """Add recurring event for all saint's eve."""
        event = Holiday(date(year, 1, 1), 'Allhelgonaafton', Work.DEPENDS)
        rrule = vRecur()
        rrule['FREQ'] = vFrequency('YEARLY')
        rrule['BYDAY'] = vWeekday('FR')
        rrule['BYMONTHDAY'] = (30, 31, 1, 2, 3, 4, 5)
        rrule['BYMONTH'] = (10, 11)
        event.add('rrule', rrule)
        self.add_component(event)

    def add_all_saints_day(self, year):
        """Add recurring event for all saint's day."""
        event = Holiday(date(year, 1, 1), 'Alla helgons dag')
        rrule = vRecur()
        rrule['FREQ'] = vFrequency('YEARLY')
        rrule['BYDAY'] = vWeekday('SA')
        rrule['BYMONTHDAY'] = (31, 1, 2, 3, 4, 5, 6)
        rrule['BYMONTH'] = (10, 11)
        event.add('rrule', rrule)
        self.add_component(event)

def main():
    """Parse arguments and start the generation."""
    parser = argparse.ArgumentParser(description='Generate a calendar with Swedish holidays.')
    parser.add_argument('start_year', metavar='start', type=int, help='first year')
    parser.add_argument('count', type=int, help='number of years to generate')
    args = parser.parse_args()
    calendar = generate(args.start_year, args.count)
    print(calendar.to_ical().decode('UTF-8'))

if __name__ == '__main__':
    main()
