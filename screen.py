import datetime
import logging
import os
import threading
import time

import terminator

LOGFILE = "logfile.log"


def get_datetime():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")


def new_logging_session(path):
    """
    Used to distinguish between different logging sessions.

    :param path: path of the log file.
    :return:
    """
    logfile = open(path, "a+")

    if logfile.read().strip() == "":
        logfile.write("{} New {} session, logging started.\n".format(get_datetime(), __name__))

    else:
        logfile.write("\n\n{} New {} session, logging started.\n".format(get_datetime(), __name__))

    logfile.close()


new_logging_session(LOGFILE)

CONFIG_LEVEL = logging.DEBUG

logging.basicConfig(level=CONFIG_LEVEL,
                    format='%(asctime)s\n%(message)s',
                    handlers=[logging.FileHandler(LOGFILE),
                              logging.StreamHandler()])

logger = logging.getLogger(__name__)

terminal_width = 80
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
        time.sleep(period)
        function()

    thread = threading.Thread(target=function, daemon=True)
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
        logger.debug("{}.__call__ called with args: %s".format(self), kwargs)

        WINDOW.clear_screen()
        to_display = self.information

        for key in kwargs.keys():
            to_display = to_display.replace("@" + key + "@", kwargs[key])

        WINDOW.print(self.title_display.center(terminal_width))
        WINDOW.print()
        WINDOW.print(to_display)

        if len(self.func_args) > 0:
            logger.debug("{}.function called with args: %s".format(self), self.func_args)
            return self.function(*self.func_args)

        else:
            return self.function()
