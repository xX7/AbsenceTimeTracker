from absence_api import AbsenceAPI
from tkcalendar import Calendar
import datetime
import holidays
import config

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk


def api_format_date(date):
    return date.astimezone(tz=datetime.timezone.utc).isoformat()[:-6] + '.000Z'


def submit_work():
    selection = cal.selection_get()
    print(selection)
    print(selection.isoformat())

    start_work = datetime.datetime.combine(selection, datetime.time(hour=9, minute=30))
    end_work = datetime.datetime.combine(selection, datetime.time(hour=12, minute=00))

    start_break = datetime.datetime.combine(selection, datetime.time(hour=12, minute=00))
    end_break = datetime.datetime.combine(selection, datetime.time(hour=12, minute=30))

    start_work_2 = datetime.datetime.combine(selection, datetime.time(hour=12, minute=30))
    end_work_2 = datetime.datetime.combine(selection, datetime.time(hour=18, minute=00))

    # print(start_work.astimezone(tz=datetime.timezone.utc).isoformat()[:-6] + '.000Z')
    absence_api.post_timespan(start_date=api_format_date(start_work), end_date=api_format_date(end_work), type="work")
    absence_api.post_timespan(start_date=api_format_date(start_break), end_date=api_format_date(end_break),
                              type="break")
    absence_api.post_timespan(start_date=api_format_date(start_work_2), end_date=api_format_date(end_work_2),
                              type="work")


def calendar_month_changed(self):
    month, year = cal.get_displayed_month()
    date = datetime.date(year, month, 1)

    month_timespans = absence_api.get_timespans(date.isoformat())

    cal.calevent_remove(tag='work')
    for month_timespan in month_timespans:
        cal.calevent_create(month_timespan, 'Work', 'work')


def get_absences():
    absence_list = absence_api.get_all_absences()
    cal.calevent_remove(tag='absence')

    for absence in absence_list:
        cal.calevent_create(absence, 'Urlaub', 'absence')


def get_timespans():
    today = datetime.date.today()
    cal.calevent_remove(tag='work')
    timespan_list = absence_api.get_timespans(datetime.date(today.year, today.month, 1).isoformat())

    for timespan in timespan_list:
        cal.calevent_create(timespan, 'Work', 'work')


def get_holidays():
    holiday_list = holidays.country_holidays(country='DE', state='NW', years=today.year)

    for holiday, name in holiday_list.items():
        cal.calevent_create(holiday, name, 'holiday')


root = tk.Tk()

today = datetime.date.today()
cal = Calendar(root, font="Helvetica 16", selectmode='day', year=today.year, month=today.month, tooltipdelay=0,
               showweeknumbers=False)

cal.bind('<<CalendarMonthChanged>>', calendar_month_changed)

cal.calevent_create(today, 'Today', 'today')

cal.tag_config('absence', background='red', foreground='yellow')
cal.tag_config('holiday', background='red', foreground='yellow')
cal.tag_config('work', background='red', foreground='green')
cal.tag_config('today', background='blue', foreground='blue')

cal.pack(fill="both", expand=True)
# ttk.Label(root, text="Hover over the events.").pack()
ttk.Button(root, text="Submit work", command=submit_work).pack()

absence_api = AbsenceAPI(config.absence_id, config.absence_key)
get_holidays()
get_absences()
get_timespans()

root.mainloop()
