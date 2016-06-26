import datetime
import logging
import os
import threading
import time

from . import terminator

TERMINAL_WIDTH = terminator.TERMINAL_WIDTH
clear_command = "clear"

if os.name == "nt":
    clear_command = "cls"


def dummy_function():
    """
    Placeholder function.

    Returns: None
    """
    pass


WINDOW = terminator.TerminalWindow()


def suggest_closest(msg, matches, the_window, closest=True):
    """
    Wrapper around the terminator.find_closest function that gets input and asks the user for confirmation
    on the correction.

    Args:
        msg (str): the message to display when waiting for input.
        matches (iterable): iterable containing the possible matches.
        the_window (terminator.TerminalWindow): window object for IO.
        closest (bool): if True, forces a match in matches.

    Returns: str
    """
    input1 = WINDOW.input(msg)
    if input1 == "":
        return input1
    while True:
        the_closest = terminator.find_closest(input1, matches, closest=closest)
        if the_closest == input1:
            return input1

        the_window.redraw()
        WINDOW.print("Did you mean " + the_closest + "? Press \"Enter\" to confirm, otherwise enter new input.")
        input2 = WINDOW.input()
        if input2.strip() == "":
            return the_closest

        else:
            input1 = input2


def formatted_input(msg):
    """
    Removes whitespace from the beginning and start of a string and makes it lower-case.
    Used to allow easier processing of input such as commands.

    Args:
        msg (str): the text to format.

    Returns: str
    """
    return WINDOW.input(msg).strip().lower()


def updater(period, function=dummy_function()):
    """
    Periodically calls a function. Useful if you want to periodically refresh a screen (e.g. for a clock).

    Args:
        period (int): the number of seconds between each function call.
        function: the function to call.

    Returns: threading.Thread
    """
    def update():
        while True:
            time.sleep(period)
            function()

    thread = threading.Thread(target=update, daemon=True)
    thread.start()

    return thread


class Screen(object):
    """
    Callable menu or screen.

    Makes use of keywords in the form @KEYWORD@ which are replaced when the screen is drawn. These are used to display
    dynamic information such as the current time.
    """
    def __init__(self, title, information, function=dummy_function, args=(), wrap=False, wrap_width=TERMINAL_WIDTH):
        """
        Initialises the screen object

        Args:
            title (str): title of the menu/screen. Displayed in the centre at the top.
            information (str): information to be displayed. Can contain keywords in the form: @KEYWORD@.
            function: optional function to be called after displaying information.
            args (iterable): arguments to be provided to the function.
        """
        self.title = title
        self.title_display = "=== " + title + " ==="
        self.information = information
        self.function = function
        self.func_args = args

        self.wrap = wrap
        self.wrap_width = wrap_width

    def __call__(self, kwargs={}):
        """
        Args:
            kwargs (dict): dictionary containing the keywords to replace as keys and the strings to replace them with as
            the values.

        Returns: self.function output
        """
        WINDOW.clear_screen()
        to_display = self.information

        for key in kwargs.keys():
            to_display = to_display.replace("@" + key + "@", kwargs[key])

        prev_wrap = WINDOW.wrap
        prev_width = WINDOW.wrap_width

        WINDOW.wrap = self.wrap
        WINDOW.wrap_width = self.wrap_width

        WINDOW.print(self.title_display.center(TERMINAL_WIDTH))
        WINDOW.print()
        WINDOW.print(to_display)

        WINDOW.wrap = prev_wrap
        WINDOW.wrap_width = prev_width

        if len(self.func_args) > 0:
            return self.function(*self.func_args)

        else:
            return self.function()