from LedgerDates import Date, subtractDates

class LedgerEntry:
    def __init__(self, date: Date, balanceChange: float, notes: str, editDate: Date):
        self.date = date
        self.balanceChange = balanceChange
        self.notes = notes
        self.editDate = editDate

    def __str__(self):
        return str(self.date) + "," + str(self.balanceChange) + "," + self.notes + "," + str(self.editDate)

def validateNotes(notes: str) -> bool:
    """
    Checks whether the given string is allowed to be stored as the notes for a LedgerEntry
    Notes are invalid if they contain commas.

    :param notes: the string to validate
    :return: False if one of the conditions for invalid strings are met, True otherwise
    """
    if ',' in notes:
        return False
    return True

class LedgerWeek:
    def __init__(self, date: Date):
        self.date = date
        self.entries: list[LedgerEntry] = []

    def addEntry(self, entry: LedgerEntry) -> None:
        """
        Adds a LedgerEntry to the week's list of entries.
        Raises ValueError if the entry was dated before the start of or after the end of this week.

        :param entry: entry to add
        :return: None
        """
        diff = subtractDates(entry.date, self.date)
        if diff < 0 or diff > 6:
            raise ValueError("Entry Date comes before start of the week")
        self.entries.append(entry)

    def removeEntry(self, idx: int) -> LedgerEntry:
        """
        Removes and returns the entry of the given index from the LedgerWeek.
        Raises IndexError if idx is out of range of the week's entry list.
        :param idx: index of the entry to remove
        :return: the removed entry
        """
        return self.entries.pop(idx)

    def getSubBalance(self) -> float:
        ret = 0
        for entry in self.entries:
            ret += entry.balanceChange
        return ret
