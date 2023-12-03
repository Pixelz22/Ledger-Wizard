from LedgerConstructs import LedgerWeek, LedgerEntry
from LedgerDates import Date, subtractDates, getMondayDate, NULL_DATE

NULL_LEDGER_WEEK = LedgerWeek(NULL_DATE)

def addWeekToLedgerPage(date: Date, ledgerPage: list[LedgerWeek]) -> LedgerWeek:
    """
    Attempts to add a new LedgerWeek for the given date to the given page and return a reference to it.
    If such a week already existed in the page, the NULL_LEDGER_WEEK is returned.

    :param date: the date of the week to add
    :param ledgerPage: the page to add the week to
    :return: a reference to the new week, or NULL_LEDGER_WEEK if no week was created
    """
    for week in ledgerPage:
        if week.date == date:
            return NULL_LEDGER_WEEK
    newWeek = LedgerWeek(date)
    ledgerPage.append(newWeek)
    return newWeek


def addEntry(entry: LedgerEntry, ledgerPage: list[LedgerWeek]):
    """
    Adds the given LedgerEntry to the given ledger page.
    Automatically creates a new LedgerWeek in the page if it needs to.

    :param entry: the LedgerEntry to add
    :param ledgerPage: the page to add the entry to
    """
    targetWeek = NULL_LEDGER_WEEK
    for week in ledgerPage:
        dist = subtractDates(entry.date, week.date)
        if 0 <= dist < 7:
            targetWeek = week

    if isNullLedgerWeek(targetWeek):  # If the week for the entry isn't in the ledger, add it.
        targetWeek = addWeekToLedgerPage(getMondayDate(entry.date), ledgerPage)
    targetWeek.addEntry(entry)


def isNullLedgerWeek(week: LedgerWeek) -> bool:
    return week is NULL_LEDGER_WEEK
