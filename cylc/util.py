"""Utility collection needed in the Cylc package"""

import re

STR_INDEX = re.compile(r"(\d+)$")


def increase_index_in_str_by_one(s: str) -> str:
    """Given a string like expX, return expY, where Y = X + 1"""
    match = STR_INDEX.search(s)
    if match:
        # Get the starting position of the number and the number itself.
        start_index = match.start()
        number = int(match.group())
        # Increment the number and reconstruct the string.
        return s[:start_index] + str(number + 1)
    else:
        # If no number is found, append "1" to the string.
        return f"{s}1"
