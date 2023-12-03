import datetime

import Utils
from LedgerConstructs import LedgerEntry, LedgerWeek, validateNotes
import LedgerIO
import LedgerLogic
from Utils import *
from LedgerDates import Date, getDateFromString, subtractDates

LEGAL_COMMAND_FLAGS = {
    "man": [],
    "quit": ["--r"],
    "save": [],
    "client": ["--a"],
    "list": ["--c"],
    "balance": [],
    "query": ["--l"],
    "entry": ["--d", "--o"],
    "session": ["--d", "--r", "--b"],
    "interest": [],
    "verify": [],
}

HOURLY_RATE = 25
# TODO: fill out gas rates
COST_PER_MILE = 0.43

OUTSOURCE_RECIPIENT = "Parents"

def save(ledger: dict[str, list[LedgerWeek]]):
    print("Saving current ledger...")
    if LedgerIO.saveLedger(ledger):
        print("Ledger saved successfully.")
    else:
        print("Failed to save ledger.")


if __name__ == "__main__":
    print("Tutoring Ledger Wizard Started")

    # Initialize main variables
    LEDGER = LedgerIO.loadLedger()
    workingClient = ""
    mostRecentEntryLoc = (0, 0)  # (weekIdx, entryIdx)

    try:
        while True:
            # region Get Command Components
            if workingClient == "":
                inputPromptHeader = ">> "
            else:
                inputPromptHeader = "[" + workingClient + "] >> "
            consoleInput = input(inputPromptHeader)
            parsed_input = consoleInput.split(" ")
            if len(parsed_input) == 0:
                continue
            command = parsed_input[0]
            args = []
            flags = []
            for i in range(1, len(parsed_input)):
                parameter = parsed_input[i]
                if parameter == "":
                    continue
                elif parameter[:2] == "--":
                    flags.append(parameter)
                else:
                    args.append(parameter)

            # endregion

            # region Big Command Parser

            # region Legal command and flag check
            if command not in LEGAL_COMMAND_FLAGS:
                print("ERROR: Unknown command name '" + command + "'.")
                continue

            badFlag = False
            for flag in flags:
                if flag not in LEGAL_COMMAND_FLAGS[command]:
                    print("ERROR: Invalid flag '" + flag + "' for command '" + command + "'.")
                    badFlag = True
                    break
            if badFlag:
                continue
            # endregion

            # region Global Commands
            if command == "quit":
                # region 'quit' command
                if "--r" in flags and \
                        evaluateResponse(input("WARNING: Unsaved changes will be deleted. Are you sure? (Y/N) ")):
                    print("Alright then. Unsaved changes deleted.")
                else:
                    save(LEDGER)
                print("Exiting Ledger Wizard. Have a wizard day! :D")
                exit()
                # endregion

            elif command == "save":
                # region 'save' command
                if len(args) != 0:
                    print("ERROR: Command 'save' takes no arguments.")
                    continue
                save(LEDGER)
                continue
                # endregion

            elif command == "client":
                # region 'client' command
                if len(args) != 1:
                    print("ERROR: Command 'client' takes 1 argument.")
                    continue
                if args[0] not in LEDGER:
                    if "--a" in flags or evaluateResponse(input("Client '" + args[0] +
                                                                "' is not in the ledger. Would you like to add them?"
                                                                " (Y/N) ")):
                        workingClient = args[0]
                        LEDGER[workingClient]: list[LedgerWeek] = []
                        print("Successfully added and switched to new client '" + workingClient + "' to the ledger.")
                else:
                    workingClient = args[0]
                    print("Successfully switched working client to '" + workingClient + "'.")
                continue
                # endregion

            elif command == "list" and workingClient == "":
                # region 'list' command case 1
                if len(args) != 0:
                    print("ERROR: Command 'list' takes no arguments.")
                    continue
                for client in LEDGER:
                    print(client)
                continue
                # endregion

            elif command == "balance":
                # region 'balance' command
                if len(args) > 1:
                    print("ERROR: Command 'balance' takes at most 1 argument.")
                    continue
                if len(args) == 0:
                    if workingClient == "":
                        print("ERROR: No client selected.")
                        continue
                    searchClient = workingClient
                else:
                    searchClient = args[0]
                balance = 0
                for week in LEDGER[searchClient]:
                    balance += week.getSubBalance()
                balance = round(balance * 100) / 100  # To get rid of weird floating point shenanigans
                print(Utils.formatMoney(balance))
                continue
                # endregion

            elif command == "man":
                # region 'man' command
                # TODO: Add descriptions for each command and its flags
                if len(args) > 0:
                    print("ERROR: Command 'man' takes no arguments.")
                    continue

                print("COMMAND LIST")
                for c in LEGAL_COMMAND_FLAGS:
                    flagString = ""
                    for flag in LEGAL_COMMAND_FLAGS[c]:  # Load up the legal flags
                        flagString += flag + ", "
                    if len(flagString) > 2:
                        flagString = flagString[:len(flagString) - 2]  # trim the last two chars
                    else:
                        flagString = "No flags"

                    print(c + ": " + flagString)  # Display each command along with its legal flags
                continue
                # endregion
            # endregion

            # region Client-based Commands
            if workingClient == "":
                print("ERROR: No client selected.")
                continue

            if command == "list":
                # region 'list' command case 2
                if len(args) != 0:
                    print("ERROR: Command 'list' takes no arguments.")
                    continue
                if "--c" in flags:
                    for client in LEDGER:
                        print(client)
                    continue

                for i in range(len(LEDGER[workingClient])):
                    print(str(i) + ": Week of " + str(LEDGER[workingClient][i].date))
                continue
                # endregion
            elif command == "query":
                # region 'query' command
                if len(args) != 1:
                    print("ERROR: Command 'query' takes 1 argument.")
                    continue

                # Collect and Validate command arguments
                try:
                    weekIdx = int(args[0])
                except ValueError:
                    print("ERROR: Expected int for command 'query'.")
                    continue

                # Assert that the weekIdx is within range
                if weekIdx < 0 or weekIdx >= len(LEDGER[workingClient]):
                    print("ERROR: Week index out of range.")
                    continue

                # Print each entry
                subBalance = 0
                for entry in LEDGER[workingClient][weekIdx].entries:
                    subBalance += entry.balanceChange
                    displayString = str(entry.date) + ": "
                    displayString += Utils.formatMoney(entry.balanceChange) + "; "
                    displayString += entry.notes + "; " if len(entry.notes) != 0 else ""
                    displayString += "Edited on " + str(entry.editDate) if "--l" in flags else ""
                    displayString += ";"
                    print(displayString)
                subBalance = round(subBalance * 100) / 100  # To get rid of weird floating point shenanigans
                print("Sub-Balance: " + Utils.formatMoney(subBalance))
                continue
                # endregion
            elif command == "entry":
                # region 'entry' command
                if len(args) != 1:
                    print("ERROR: Command 'entry' takes 1 argument.")
                    continue

                # Collect and Validate command arguments
                balanceChange = 0
                try:
                    balanceChange = float(args[0])
                except ValueError:
                    print("ERROR: Expected a float for command 'entry'.")
                    continue

                # Have to screw around to get the date in a usable form.
                externalDateObject = datetime.date.today()
                editDate = Date(int(externalDateObject.day), int(externalDateObject.month), int(externalDateObject.year))
                if "--d" in flags:
                    entryDate = editDate
                else:
                    while True:  # Loop until we get a valid date
                        try:
                            entryDate = getDateFromString(input("What is the date of the entry: "))
                            break
                        except ValueError:
                            print("ERROR: Invalid date.")

                # Get the notes from the user, ensure they are valid
                while True:
                    notes = input("Enter any notes about the entry: ")
                    if validateNotes(notes):
                        break
                    print("ERROR: Notes are invalid. Please enter valid notes.")

                # If the parents were the direct recipient of the payment, copy the entry into their ledger
                if "--o" in flags:
                    if OUTSOURCE_RECIPIENT not in LEDGER:
                        if evaluateResponse(input("Outsourced recipient has not yet been created. "
                                                  "Would you like to do so? (Y/N)")):
                            LEDGER[OUTSOURCE_RECIPIENT]: list[LedgerWeek] = []
                        else:  # If we don't want to create an outsource recipient
                            # Add the original entry to the ledger and back out
                            LedgerLogic.addEntry(LedgerEntry(entryDate, balanceChange, notes, editDate),
                                                 LEDGER[workingClient])
                            continue
                    # Edit the notes slightly and add a copy of the entry to the outsource recipient ledger
                    recipientNotes = "Outsourced recipient from " + workingClient + " on " \
                                     + str(entryDate) + "; " + notes
                    LedgerLogic.addEntry(LedgerEntry(entryDate, -balanceChange,
                                                     recipientNotes, editDate), LEDGER[OUTSOURCE_RECIPIENT])
                    notes = notes + "; Outsourced Recipient"

                # Add the entry to the ledger
                LedgerLogic.addEntry(LedgerEntry(entryDate, balanceChange, notes, editDate), LEDGER[workingClient])
                continue
                # endregion
            elif command == "session":
                # region 'session' command
                if len(args) != 2:
                    print("ERROR: Command 'session' takes 2 argument.")
                    continue

                # Collect and Validate command arguments
                minutes = 0
                miles = 0
                try:
                    minutes = float(args[0])
                    miles = float(args[1])
                except ValueError:
                    print("ERROR: Expected a float for command 'session'.")
                    continue
                rate = HOURLY_RATE
                if "--r" in flags:
                    while True:  # Loop until we get a valid rate
                        try:
                            rate = float(input("Please enter custom rate (dollars per hour): "))
                            break
                        except ValueError:
                            print("ERROR: Expected a float.")
                if "--b" in flags:
                    balanceChange = round(-((rate * minutes / 60) + miles) * 100) / 100
                else:
                    balanceChange = round(-((rate * minutes / 60) + (COST_PER_MILE * miles)) * 100) / 100

                externalDateObject = datetime.date.today()
                editDate = Date(int(externalDateObject.day), int(externalDateObject.month), int(externalDateObject.year))
                if "--d" in flags:
                    entryDate = editDate
                else:
                    while True:  # Loop until we get a valid date
                        try:
                            entryDate = getDateFromString(input("What is the date of the session: "))
                            break
                        except ValueError:
                            print("ERROR: Invalid date.")

                notes = str(minutes) + " minute session"

                if "--b" in flags:
                    notes += "; base pay of " + formatMoney(miles)
                else:
                    notes += "; travelled " + str(miles) + " miles"
                if "--r" in flags:
                    notes += "; custom rate of " + formatMoney(rate) + " per hour"

                LedgerLogic.addEntry(LedgerEntry(entryDate, balanceChange, notes, editDate), LEDGER[workingClient])
                continue
                # endregion
            elif command == "interest":
                # region 'interest' command
                # TODO: TEST, THEN REMOVE SAFETY CHECK
                if not evaluateResponse(input("Still undergoing testing. Are you sure you want to proceed? (Y/N)")):
                    continue

                if len(args) != 1:
                    print("ERROR: Command 'interest' takes 1 argument.")
                    continue

                # Collect and Validate command arguments
                rate = 0
                try:
                    rate = float(args[0])
                    if rate < 0:
                        print("ERROR: Interest rate must be non-negative.")
                        continue
                except ValueError:
                    print("ERROR: Expected a float for command 'entry'.")
                    continue

                if len(LEDGER[workingClient]) == 0:
                    print("No unpaid dues.")
                    continue

                balance = 0
                for week in LEDGER[workingClient]:
                    balance += week.getSubBalance()
                if balance >= 0:
                    print("No unpaid dues.")
                    continue

                mostRecentWeek = LEDGER[workingClient][len(LEDGER[workingClient]) - 1]
                externalDateObject = datetime.date.today()
                todayDate = Date(int(externalDateObject.day), int(externalDateObject.month), int(externalDateObject.year))

                # If we haven't reached the most recent week, don't bother adding dues
                passedWeeks = int(subtractDates(todayDate, mostRecentWeek.date) / 7)
                if passedWeeks <= 0:
                    print("No overdue payments.")
                    continue

                notes = str(rate * 100) + "% Interest on " + formatMoney(balance)

                LedgerLogic.addEntry(LedgerEntry(todayDate, balance * (rate ** passedWeeks), notes, todayDate),
                                     LEDGER[workingClient])

                print("Added " + notes + ".")
                continue
                # endregion
            elif command == "verify":
                # region 'verify' command
                print("ERROR: Command not finished")
                continue
                # endregion
            # endregion

            # endregion
    except KeyboardInterrupt:  # Check if we want to save if manually exiting the program
        print()
        if evaluateResponse(input("Do you want to save any changes? (Y/N) ")):
            save(LEDGER)
