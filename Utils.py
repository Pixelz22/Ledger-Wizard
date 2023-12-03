import math


def isDate(s: str) -> bool:
    """
    Determines if the given string is a date, using month/day/year.

    :param s: the string to test
    :return: True if the string is a date, False otherwise
    """
    components = s.split('/')
    if len(components) != 3:
        return False
    for comp in components:
        try:
            int(comp)
        except ValueError:
            return False
    return True


def evaluateResponse(s: str) -> bool:
    """
    Helper function for evaluating yes/no prompts

    :param s: the response
    :return: True if the response is some form of "Yes", False otherwise
    """
    return s == "y" or s == "Y" or s.lower() == "yes"


def binaryInsert(target: list, item, evalFunc) -> None:
    # TODO: Implement this for organizing entries in LedgerWeek and LedgerWeeks in ledger pages
    return


def sign(x: float) -> int:
    return int(math.copysign(1, x))


def formatMoney(x: float) -> str:
    return ("-$" if x < 0 else "$") + str(math.fabs(x))
