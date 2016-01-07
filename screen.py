import os
import logging
import datetime
import terminator

LOGFILE = "logfile.log"

def get_datetime():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

def new_logging_session(path):
    logfile = open(path, "a+")

    if logfile.read().strip() == "":
        logfile.write("{} New {} session, logging started.\n".format(get_datetime(), __name__))

    else:
        logfile.write("\n\n{} New {} session, logging started.\n".format(get_datetime(), __name__))

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

class Screen(object):
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
