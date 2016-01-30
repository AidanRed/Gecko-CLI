import datetime
import logging
import os
import threading
import time

import terminator

TERMINAL_WIDTH = 80
clear_command = "clear"

if os.name == "nt":
    clear_command = "cls"


def dummy_function():
    pass


WINDOW = terminator.TerminalWindow()


def formatted_input(msg):
    return WINDOW.input(msg).strip().lower()


def updater(period, function=dummy_function()):
    """
    Periodically calls a function. Useful if you want to periodically refresh a screen (e.g. for a clock).
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

    """
    def __init__(self, title, information, function=dummy_function, args=()):
        self.title = title
        self.title_display = "=== " + title + " ==="
        self.information = information
        self.function = function
        self.func_args = args

    def __call__(self, kwargs={}):
        WINDOW.clear_screen()
        to_display = self.information

        for key in kwargs.keys():
            to_display = to_display.replace("@" + key + "@", kwargs[key])

        WINDOW.print(self.title_display.center(TERMINAL_WIDTH))
        WINDOW.print()
        WINDOW.print(to_display)

        if len(self.func_args) > 0:
            return self.function(*self.func_args)

        else:
            return self.function()
