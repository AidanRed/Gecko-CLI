import sys
from libs import ansitowin32, termcolor

class ColoredWriter(object):
    def __init__(self):
        self.converter = ansitowin32.AnsiToWin32(sys.stdout)

        self.colour = "white"
        self.on_colour = "on_blue"
        self.attrs = None

    def write(self, text, colour=None, on_colour=None, attrs=None, end="\n"):
        the_colour = self.colour
        the_on_colour = self.on_colour
        the_attrs = self.attrs

        if colour is not None:
            the_colour = colour

        if on_colour is not None:
            the_on_colour = on_colour

        if attrs is not None:
            the_attrs = attrs

        self.converter.write_and_convert(termcolor.colored(text, the_colour, the_on_colour, the_attrs) + end)
