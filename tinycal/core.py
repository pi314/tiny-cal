import sys

import calendar

from calendar import Calendar, SUNDAY, MONDAY
from datetime import date, timedelta

from . import CALRCS
from . import cli
from .config import TinyCalConfig, Color


class DateCursor:
    def __init__(self, cal, year, month, day):
        self.cal = cal
        self.year = year
        self.month = month
        self.day = day

    @property
    def umn(self):
        return (self.year * 12) + (self.month - 1)

    @staticmethod
    def from_date(cal, d):
        return DateCursor(cal, d.year, d.month, d.day)

    def to_date(self):
        if self.day == -1:
            day = calendar.monthrange(self.year, self.month)[1]
        else:
            day = self.day

        return date(self.year, self.month, day)

    def __isub__(self, other):
        d = date(self.year, self.month, self.day)
        d -= timedelta(other)
        self.year = d.year
        self.month = d.month
        self.day = d.day
        return self

    def __iadd__(self, other):
        d = date(self.year, self.month, self.day)
        d += other
        self.year = d.year
        self.month = d.month
        self.day = d.day
        return self

    def move_back_n_month(self, months):
        umn = self.umn
        umn -= months
        self.year = umn // 12
        self.month = (umn % 12) + 1
        self.day = 1
        return self

    def move_forward_n_month(self, months):
        umn = self.umn
        umn += months
        self.year = umn // 12
        self.month = (umn % 12) + 1
        self.day = -1
        return self

    def move_to_week_begin(self):
        d = date(self.year, self.month, self.day) - timedelta(
                days=list(self.cal.iterweekdays()).index(
                    self.to_date().weekday()))
        self.year = d.year
        self.month = d.month
        self.day = d.day
        return self

    @staticmethod
    def cal_week_num(cal, date):
        return ((date - cal.monthdatescalendar(date.year, 1)[0][0]).days // 7) + 1


class MonthDelta:
    def __init__(self, months):
        self.months = months

    def __int__(self):
        return self.months


def main():
    conf = TinyCalConfig.parse_conf(CALRCS)
    args = cli.parse_args()

    print(conf)
    print()

    print(args)
    print()

    # Remove arguments that are no part of TinyCalConfig
    month = args.month
    delattr(args, 'month')

    year = args.year
    delattr(args, 'year')

    color = args.color
    delattr(args, 'color')

    today = args.today or date.today()
    delattr(args, 'today')

    conf.merge(vars(args))
    print(conf)
    print()

    cal = Calendar(MONDAY if conf.start_monday else SUNDAY)

    # Calculate display range
    if year is not None and month is not None:
        # given year, month
        display_range_start = DateCursor(cal, year, month, 1)
        display_range_end = DateCursor(cal, year, month, -1)

    elif year is not None and month is None:
        # given year
        display_range_start = DateCursor(cal, year, 1, 1)
        display_range_end = DateCursor(cal, year, 12, 31)

    else:
        display_range_start = DateCursor.from_date(cal, today)
        display_range_end = DateCursor.from_date(cal, today)

    # Apply before/after
    if conf.before:
        if conf.before.unit == 'W':
            display_range_start -= timedelta(weeks=conf.before.value)

        elif conf.before.unit == 'M':
            display_range_start.move_back_n_month(conf.before.value)

    if conf.after:
        if conf.after.unit == 'W':
            display_range_end += timedelta(weeks=conf.after.value)

        elif conf.after.unit == 'M':
            display_range_end.move_forward_n_month(conf.after.value)

    print('today =', today)
    print()

    if not conf.cont:
        print('start =', display_range_start.to_date())
        print('end =  ', display_range_end.to_date())
        print()

        for umn in range(display_range_start.umn, display_range_end.umn + 1):
            year = umn // 12
            month = (umn % 12) + 1
            print(year, month)
            print('WK', ' '.join(map(lambda x: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su', 'WK'][x], cal.iterweekdays())))
            for week in cal.monthdatescalendar(year, month):
                wk = DateCursor.cal_week_num(cal, week[0])
                print(str(wk).rjust(2), ' '.join(str(day.day).rjust(2) for day in week))

            print()

    else:
        display_cursor = display_range_start.move_to_week_begin().to_date()

        print('cont')
        print('start =', display_cursor)
        print('end =  ', display_range_end.to_date())
        print()

        print('WK', ' '.join(map(lambda x: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su', 'WK'][x], cal.iterweekdays())))
        while display_cursor <= display_range_end.to_date():
            wk = DateCursor.cal_week_num(cal, display_cursor)
            print(str(wk).rjust(2), ' '.join(str((display_cursor + timedelta(days=d)).day).rjust(2) for d in range(7)))

            display_cursor += timedelta(days=7)
