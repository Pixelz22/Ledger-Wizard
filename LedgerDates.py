import datetime

import Utils

DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def getDaysInMonth(month: int, year: int):
    if month < 1 or month > 12:
        raise ValueError("Month out of range.")
    if year < 1:
        raise ValueError("Year out of range.")
    return DAYS_IN_MONTH[month - 1] + (1 if year % 4 == 0 else 0)


class Date:
    def __init__(self, day: int, month: int, year: int):
        # 0, 0, 0 is the Null Date
        if day == 0 and month == 0 and year == 0:
            self.day = 0
            self.month = 0
            self.year = 0
            return

        if month < 1 or day < 1 or year < 1 or month > 12:
            raise ValueError("Invalid date.")
        if day > getDaysInMonth(month, year):
            raise ValueError("Invalid date.")
        self.day = day
        self.month = month
        self.year = year

    def __str__(self):
        return str(self.month) + "/" + str(self.day) + "/" + str(self.year)


NULL_DATE = Date(0, 0, 0)


def getDateFromString(dateString: str) -> Date:
    """
    Returns a new Date object based on a string given in month/day/year format.
    Raises ValueError if the string is not a valid date.

    :param dateString: the string to parse
    :return: a Date object based on dateString
    """
    components = dateString.split('/')
    if len(components) != 3:
        raise ValueError("Invalid date string.")
    try:
        return Date(int(components[1]), int(components[0]), int(components[2]))
    except ValueError:
        raise ValueError("Invalid date string.")


# TODO: TEST WITH LEAP YEAR EDGE CASES
def subtractDates(d1: Date, d2: Date) -> int:
    """
    Returns the distance in days between two Dates, positive if d1 comes later, negative if d2 comes later.

    :param d1: the first Date to compare
    :param d2: the second Date to compare
    :return: the distance in days between d1 and d2, positive if d1 comes later, negative if d2 comes later
    """
    yearDiff = d1.year - d2.year
    leapYearCount = int(yearDiff / 4)
    yearDiff = (yearDiff - leapYearCount) * 365 + leapYearCount * 366
    monthDiff = 0
    for i in range(d2.month, d1.month, Utils.sign(d1.month - d2.month)):
        # If they are both leap years, the extra day is counted in yearDiff
        monthDiff += Utils.sign(d1.month - d2.month) * (
                DAYS_IN_MONTH[i - 1] + (1 if i == 2 and (d1.month % 4 == 0 or d2.month % 4 == 0) else 0))
    return d1.day - d2.day + monthDiff + yearDiff


def compareDates(d1: Date, d2: Date) -> int:
    """
    Helper function for determining the order of dates.
    Returns 1 if d1 is later, -1 is d2 is later, and 0 if they are the same date

    :param d1: the first Date to compare
    :param d2: the second Date to compare
    :return: 1 if d1 > d2, -1 if d1 < d2, and 0 if they're equal
    """
    # Compare the components, prioritizing the years, then months, then days
    if d1.year != d2.year:
        return Utils.sign(d1.year - d2.year)
    if d1.month != d2.month:
        return Utils.sign(d1.month - d2.month)
    if d1.day != d2.day:
        return Utils.sign(d1.day - d2.day)
    return 0


def subtractDaysFromDate(date: Date, days: int) -> Date:
    """
    Computes the date that occurs the given amount of days before 'date'.

    :param date: the date to start at
    :param days: the days before
    :return: a Date object for the date that occurs 'days' days before 'date'
    """
    newDay = date.day - days
    if newDay > 0:
        return Date(newDay, date.month, date.year)
    newMonth = date.month - 1
    newDay = getDaysInMonth(newMonth, date.year) + newDay + 1
    if newMonth > 0:
        return Date(newDay, newMonth, date.year)
    return Date(newDay, 12, date.year - 1)


# TODO: Finish this
def getMondayDate(date: Date) -> Date:
    """
    Returns the date of the latest Monday to occur before 'date'.
    If 'date' is a Monday, a copy of it is returned.

    :param date: the date to compare
    :return: the Date of the latest Monday before 'date'
    """
    return subtractDaysFromDate(date, datetime.date(date.year, date.month, date.day).isoweekday() - 1)



