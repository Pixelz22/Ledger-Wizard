import LedgerLogic
from LedgerConstructs import LedgerWeek, LedgerEntry
from os import listdir, getcwd
from os.path import isfile, join
from LedgerDates import getDateFromString


LEDGER_PATH = join(getcwd(), "pages")


def loadLedger() -> dict[str, list[LedgerWeek]]:
    """
    Loads and returns the ledger from the LEDGER_PATH directory.
    It automatically skips over any files with invalid formatting.

    :return: the ledger
    """
    ledger = {}  # Clear the ledger
    # Load all files in the directory
    allFiles = [f for f in listdir(LEDGER_PATH) if isfile(join(LEDGER_PATH, f))]
    for fileName in allFiles:
        if not fileName.endswith(".txt"):  # Only consider .txt files
            continue
        try:
            invalidData = False
            with open(join(LEDGER_PATH, fileName)) as ledgerFile:
                ledgerPage: list[LedgerWeek] = []
                workingWeek = LedgerLogic.NULL_LEDGER_WEEK

                # Walk through the lines
                lineNum = 0
                clientName = "dummy"
                for line in ledgerFile:
                    lineNum += 1
                    line = line.replace("\n", "")  # Get rid of any formatting things

                    # Check the first line to see if this is a ledger page file
                    if lineNum == 1:
                        validityCheck = line.split(" ")
                        if len(validityCheck) != 2 or validityCheck[0] != "ledgerpage":
                            invalidData = True
                            break
                        clientName = validityCheck[1]
                        continue

                    if len(line) == 0:  # Ignore empty lines
                        continue
                    if line[0] == 'w':  # Line is a header for a new week
                        if workingWeek != LedgerLogic.NULL_LEDGER_WEEK:  # Add completed week to ledger page
                            ledgerPage.append(workingWeek)

                        try:
                            workingWeek = LedgerWeek(getDateFromString(line[1:]))  # Prepare next week to add
                        except ValueError:  # Something about the week line was wrong
                            invalidData = True
                            break
                    elif line[0] == 'e':  # Line is an entry for the ledger
                        data = line[1:].split(',')
                        if len(data) != 4:  # Entry line has too much or too little sections
                            invalidData = True
                            break

                        try:
                            ledgerEntry = LedgerEntry(getDateFromString(data[0]), float(data[1]),
                                                      data[2], getDateFromString(data[3]))
                            workingWeek.addEntry(ledgerEntry)
                        except ValueError:  # Something about the entry line was formatted wrong
                            invalidData = True
                            break
                    else:  # Line has illegal header
                        invalidData = True
                        break
                if invalidData:  # Something somewhere in the file was wrong, skip this file
                    continue
                if workingWeek != LedgerLogic.NULL_LEDGER_WEEK:
                    ledgerPage.append(workingWeek)  # Add the last working week if it's not null
                ledger[clientName] = ledgerPage  # Add the ledger page to the ledger
        except FileNotFoundError:
            continue
    return ledger


def saveLedger(ledger: dict[str, list[LedgerWeek]]) -> bool:
    """
    Saves the ledger to the LEDGER_PATH directory.

    :param ledger: the ledger to save
    :return: True if ledger was saved, False if it could not write to the files
    """
    for client in ledger:
        try:
            with open(join(LEDGER_PATH, client + ".txt"), 'w') as fp:
                fp.write("ledgerpage " + client + "\n")
                for week in ledger[client]:
                    fp.write("w" + str(week.date) + "\n")
                    for entry in week.entries:
                        fp.write("e" + str(entry) + "\n")
                pass
        except FileNotFoundError:
            return False
    return True
